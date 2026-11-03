"""
任务处理器
==========
- TTS：合成口播音频 + 生成字幕时间轴
- 合成：裁切合并 + 音视频合成 + 字幕烧录（Step3 一键合成）
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.logger import get_logger
from app.managers.ffmpeg_manager import FFmpegManager, sanitize_filename
from app.managers.tts_manager import TTSManager
from app.managers.video_marker_manager import VideoMarkerManager
from app.tasks.task_queue import (
    TYPE_COMPOSE,
    TYPE_TTS,
    TaskContext,
    task_queue,
)
from app.utils.srt import generate_srt

logger = get_logger()


async def handle_tts(ctx: TaskContext) -> dict[str, Any]:
    """TTS 合成任务

    payload: {creation_id, script, filename, provider?, segments?}
    segments 支持按段落指定 voice_id / rate / pitch / volume / pause_after_ms。
    """
    payload = ctx.get_payload()
    creation_id = payload.get("creation_id", "")
    script = payload.get("script", "")
    filename = payload.get("filename", "audio.mp3")
    provider = payload.get("provider")
    segments = payload.get("segments")

    ctx.update_progress(10)

    output_dir = settings.workdir_abs / creation_id / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    result = await TTSManager().synthesize(
        script=script,
        output_path=output_path,
        segments=segments,
        provider=provider,
    )

    ctx.update_progress(70)

    # 字幕时间轴落盘（与音频同目录）
    timestamps = result.get("timestamps") or []
    timestamps_path = output_path.with_suffix(".timestamps.json")
    timestamps_path.write_text(
        json.dumps(timestamps, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    rel_path = output_path.relative_to(settings.workdir_abs).as_posix()

    meta = {
        "audio_path": rel_path,
        "timestamps_path": timestamps_path.relative_to(settings.workdir_abs).as_posix(),
        "duration": result.get("duration", 0),
        "engine_used": result.get("engine_used", ""),
        "provider": result.get("provider", ""),
        "provider_label": result.get("provider_label", ""),
        "voice_id": result.get("voice_id", ""),
        "voices_used": result.get("voices_used", []),
        "warning": result.get("warning"),
    }
    ctx.update_progress(100, result=meta)
    return meta


def _resolve_user_file(file_id: str | None, creation_id: str, label: str) -> Path | None:
    """把用户上传的 file_id 解析为本地路径（校验文件归属）"""
    if not file_id:
        return None

    from app.core.database import session_scope
    from app.models.creation import Creation
    from app.models.file import File

    with session_scope() as db:
        creation = db.get(Creation, creation_id)
        record = db.get(File, str(file_id))
        if not record:
            raise FileNotFoundError(f"{label}文件不存在: {file_id}")
        if creation and record.user_id != creation.user_id:
            raise PermissionError(f"{label}文件不属于当前用户")
        path = Path(record.path)

    if not path.is_file():
        raise FileNotFoundError(f"{label}文件已丢失: {path.name}")
    return path


def _resolve_avatar_path(avatar: dict[str, Any] | None, creation_id: str) -> Path | None:
    """把头像 file_id 解析为本地路径（校验文件归属）"""
    if not avatar:
        return None
    return _resolve_user_file(avatar.get("file_id"), creation_id, "头像")


async def handle_compose(ctx: TaskContext) -> dict[str, Any]:
    """合成任务（裁切 + 转场合并 + 音视频合成 + 字幕 + 主持人人像）

    payload: {
        creation_id, video_dir, audio_paths, markers, resolution,
        subtitle_style, fast_mode, global_transition, avatar, quality
    }
    """
    payload = ctx.get_payload()
    creation_id = payload.get("creation_id", "")
    video_dir = payload.get("video_dir", "")
    audio_paths: list[str] = payload.get("audio_paths", [])
    markers: list[dict[str, Any]] = payload.get("markers", [])
    resolution = payload.get("resolution", "1080x1920")
    subtitle_style = payload.get("subtitle_style", "默认白字黑描边")
    subtitle_position = payload.get("subtitle_position") or None
    fast_mode = payload.get("fast_mode", False)
    global_transition = payload.get("global_transition") or {"type": "none", "duration": 0.5}
    avatar = payload.get("avatar") or None
    quality = payload.get("quality") or {}
    bgm = payload.get("bgm") or None
    intro_outro = payload.get("intro_outro") or None

    if not markers:
        raise ValueError("没有视频标记，无法合成")
    if not audio_paths:
        raise ValueError("没有可用音频，无法合成")

    quality_resolution = str(quality.get("resolution") or resolution)
    crf = int(quality.get("crf", 23))
    preset = str(quality.get("preset", "medium"))

    work_dir = settings.workdir_abs / creation_id / "output"
    work_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _timestamp()
    out_dir = work_dir / f"{timestamp}_{creation_id[-6:]}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. 解析标记对应的源文件
    segments: list[tuple[Path, float, float]] = []
    for mark in markers:
        source = Path(video_dir) / mark["source"]
        if not source.is_file():
            raise FileNotFoundError(f"视频源文件不存在: {mark['source']}")
        segments.append((source, float(mark["start"]), float(mark["end"])))

    # 边界转场：单段覆盖优先，否则用全局配置
    boundaries: list[dict[str, Any]] = []
    for i in range(1, len(markers)):
        raw = markers[i].get("transition") or global_transition
        boundaries.append(
            {
                "type": str(raw.get("type", "none")),
                "duration": float(raw.get("duration", 0.5)),
            }
        )
    has_transition = any(b["type"] != "none" for b in boundaries)

    ctx.update_progress(10)

    # 2. 先合并音频（后续视频按音频总时长补齐）
    audio_files = [settings.workdir_abs / p for p in audio_paths]
    for p in audio_files:
        if not p.is_file():
            raise FileNotFoundError(f"音频文件不存在: {p.name}")

    if len(audio_files) > 1:
        merged_audio = out_dir / "audio_merged.mp3"
        FFmpegManager.concat_audio(audio_files, merged_audio)
    else:
        merged_audio = audio_files[0]
    audio_duration = FFmpegManager.probe_duration(merged_audio)

    ctx.update_progress(30)

    # 3. 裁切 + 转场合并
    if fast_mode and not has_transition:
        merged = out_dir / "clips_merged.mp4"
        FFmpegManager.cut_and_merge_fast(segments, merged, resolution=quality_resolution)
        if audio_duration and FFmpegManager.probe_duration(merged) < audio_duration - 0.05:
            padded = out_dir / "clips_padded.mp4"
            FFmpegManager._pad_clip(
                merged,
                audio_duration - FFmpegManager.probe_duration(merged),
                padded,
                crf=crf,
                preset="veryfast",
            )
            merged = padded
    else:
        segment_paths: list[Path] = []
        for i, (src, start, end) in enumerate(segments):
            seg_path = out_dir / f"segment_{i + 1:03d}.mp4"
            FFmpegManager.cut_segment(
                src, start, end - start, seg_path, resolution=quality_resolution
            )
            segment_paths.append(seg_path)
        merged = out_dir / "clips_merged.mp4"
        FFmpegManager.merge_clips_with_transitions(
            segment_paths,
            boundaries,
            merged,
            crf=crf,
            preset=preset,
            pad_to=audio_duration or None,
        )
        for p in segment_paths:
            p.unlink(missing_ok=True)

    ctx.update_progress(55)

    # 4. 音视频合成
    with_audio = out_dir / "with_audio.mp4"
    FFmpegManager.merge_audio_video(merged, merged_audio, with_audio)

    # 4.1 片头 / 片尾字卡（拼接后字幕整体后移 intro 时长）
    intro_duration = 0.0
    outro_duration = 0.0
    intro_path: Path | None = None
    outro_path: Path | None = None
    if intro_outro:
        cards: list[Path] = []
        for key, label in (("intro", "片头"), ("outro", "片尾")):
            item = intro_outro.get(key) or {}
            if not item.get("enabled"):
                continue
            card_path = out_dir / f"{key}.mp4"
            FFmpegManager.build_title_card(
                card_path,
                title=str(item.get("title") or ""),
                subtitle=str(item.get("subtitle") or ""),
                duration=float(item.get("duration", 3.0)),
                resolution=quality_resolution,
                background_color=str(item.get("background_color") or "#0F1117"),
                text_color=str(item.get("text_color") or "#FFFFFF"),
                image_path=_resolve_user_file(item.get("image_file_id"), creation_id, f"{label}背景图"),
            )
            cards.append(card_path)
            if key == "intro":
                intro_path = card_path
            else:
                outro_path = card_path
        if cards:
            with_cards = out_dir / "with_cards.mp4"
            FFmpegManager.join_cards(
                with_audio,
                with_cards,
                intro=intro_path,
                outro=outro_path,
                crf=crf,
                preset=preset,
            )
            with_audio = with_cards
            if intro_path:
                intro_duration = FFmpegManager.probe_duration(intro_path)
            if outro_path:
                outro_duration = FFmpegManager.probe_duration(outro_path)

    # 4.2 BGM 混音 + 人声闪避（在片头片尾之后，音乐覆盖全片）
    bgm_path: Path | None = None
    if bgm and bgm.get("file_id"):
        bgm_path = _resolve_user_file(bgm.get("file_id"), creation_id, "BGM")
        mixed = out_dir / "with_bgm.mp4"
        FFmpegManager.mix_bgm(
            with_audio,
            bgm_path,
            mixed,
            volume=int(bgm.get("volume", 30)),
            ducking=bool(bgm.get("ducking", True)),
            duck_level=int(bgm.get("duck_level", 30)),
            fade_in=float(bgm.get("fade_in", 0.6)),
            fade_out=float(bgm.get("fade_out", 0.8)),
            loop=bool(bgm.get("loop", True)),
        )
        with_audio = mixed

    ctx.update_progress(75)

    # 5. 字幕 + 主持人人像（一次性处理；失败时降级）
    timestamps_path = audio_files[0].with_suffix(".timestamps.json")
    timestamps: list[dict[str, Any]] = []
    if timestamps_path.is_file():
        timestamps = json.loads(timestamps_path.read_text(encoding="utf-8"))

    srt_path: Path | None = None
    if timestamps:
        srt_path = out_dir / "subtitle.srt"
        max_chars = FFmpegManager.subtitle_max_chars(subtitle_style)
        srt_path.write_text(
            generate_srt(timestamps, offset=intro_duration, max_chars=max_chars),
            encoding="utf-8",
        )

    avatar_path = _resolve_avatar_path(avatar, creation_id)
    final_path = out_dir / "final.mp4"
    try:
        FFmpegManager.finalize_video(
            with_audio,
            final_path,
            srt_file=srt_path,
            style=subtitle_style,
            subtitle_position=subtitle_position,
            avatar_path=avatar_path,
            avatar=avatar,
            crf=crf,
            preset=preset,
        )
    except Exception as e:
        logger.warning(f"字幕/人像合成失败，降级处理: {e}")
        if avatar_path and srt_path:
            try:
                FFmpegManager.finalize_video(
                    with_audio, final_path, srt_file=srt_path, style=subtitle_style,
                    subtitle_position=subtitle_position,
                    crf=crf, preset=preset,
                )
            except Exception as e2:
                logger.warning(f"仅字幕烧录仍失败，输出无字幕版本: {e2}")
                FFmpegManager.safe_move(with_audio, final_path)
        else:
            FFmpegManager.safe_move(with_audio, final_path)

    ctx.update_progress(95)

    # 6. 收集元信息
    duration = FFmpegManager.probe_duration(final_path)
    file_size = final_path.stat().st_size
    final_resolution = FFmpegManager.probe_resolution(final_path)
    rel_path = final_path.relative_to(settings.workdir_abs).as_posix()

    # 7. 登记到 outputs 表（完成页多次合成列表）
    from app.core.database import session_scope
    from app.services.step3_service import Step3Service

    with session_scope() as db:
        Step3Service(db).record_output(
            creation_id=creation_id,
            output_path=rel_path,
            duration=duration,
            file_size=file_size,
            resolution=final_resolution,
        )

    meta = {
        "output_path": rel_path,
        "duration": duration,
        "file_size": file_size,
        "resolution": final_resolution,
        "transition": global_transition,
        "transitions_applied": boundaries,
        "avatar": {
            "position": (avatar or {}).get("position"),
            "size_ratio": (avatar or {}).get("size_ratio"),
            "border_width": (avatar or {}).get("border_width"),
            "shadow": (avatar or {}).get("shadow"),
            "start": (avatar or {}).get("start"),
            "end": (avatar or {}).get("end"),
            "applied": bool(avatar_path),
        } if avatar else None,
        "quality": {"resolution": quality_resolution, "crf": crf, "preset": preset},
        "bgm": {
            "volume": (bgm or {}).get("volume"),
            "ducking": (bgm or {}).get("ducking"),
            "duck_level": (bgm or {}).get("duck_level"),
            "fade_in": (bgm or {}).get("fade_in"),
            "fade_out": (bgm or {}).get("fade_out"),
            "applied": bool(bgm_path),
        } if bgm else None,
        "intro_outro": {
            "intro_duration": intro_duration,
            "outro_duration": outro_duration,
            "title": (intro_outro or {}).get("intro", {}).get("title") if intro_outro else None,
        } if intro_outro and (intro_path or outro_path) else None,
    }
    ctx.update_progress(100, result=meta)
    return meta


def register_handlers() -> None:
    """注册所有任务处理器（应用启动时调用）"""
    task_queue.register(TYPE_TTS, handle_tts)
    task_queue.register(TYPE_COMPOSE, handle_compose)
    logger.info("任务处理器注册完成")


def _timestamp() -> str:
    """时间戳目录名"""
    from datetime import datetime

    return datetime.now().strftime("%Y%m%d_%H%M%S")


__all__ = ["VideoMarkerManager", "handle_compose", "handle_tts", "register_handlers", "sanitize_filename"]
