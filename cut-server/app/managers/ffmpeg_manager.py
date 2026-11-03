"""
ffmpeg 管理器
=============
封装 ffmpeg/ffprobe 调用：
- cut_segment：裁切单段（-ss 后置于 -i，实现帧级精确 seek）
- concat_segments：concat demuxer 合并
- cut_and_merge_fast：单条 ffmpeg concat filter 方案（比逐段快 3~5 倍）
- merge_audio_video：音视频合并
- burn_subtitles：字幕烧录
- concat_audio：多音频合并

所有外部命令均用 subprocess.run + 参数列表（不拼 shell 字符串），避免命令注入。
"""
from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path

from app.core.exceptions import ExternalServiceError
from app.core.logger import get_logger
from app.utils.ffmpeg import ffmpeg_bin, ffprobe_bin

logger = get_logger()

# ffmpeg 执行超时（秒）
FFMPEG_TIMEOUT = 1800
PROBE_TIMEOUT = 30

# 字幕样式预设
SUBTITLE_STYLES = {
    "默认白字黑描边": "FontName=Microsoft YaHei,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,MarginV=40,Alignment=2",
    "大号黄字": "FontName=Microsoft YaHei,FontSize=28,PrimaryColour=&H0000D7FF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,MarginV=60,Alignment=2",
    "底部居中白字": "FontName=Microsoft YaHei,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,Shadow=0,MarginV=20,Alignment=2",
    "背景条白字": "FontName=Microsoft YaHei,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=4,BackColour=&H80000000,Outline=0,Shadow=0,MarginV=50,Alignment=2",
    "综艺黄字": "FontName=Microsoft YaHei,FontSize=26,PrimaryColour=&H0000E5FF,OutlineColour=&H00000000,BorderStyle=1,Outline=4,Shadow=2,MarginV=70,Alignment=2",
    "小清新白字": "FontName=Microsoft YaHei,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H40000000,BorderStyle=1,Outline=1,Shadow=0,MarginV=90,Alignment=2",
    # 新增模板：白底黑字条 / 描边加粗 / 顶部居中 / 超大综艺
    "白底黑字条": "FontName=Microsoft YaHei,FontSize=18,PrimaryColour=&H00000000,OutlineColour=&H00FFFFFF,BorderStyle=4,BackColour=&H00FFFFFF,Outline=0,Shadow=0,MarginV=45,Alignment=2",
    "描边加粗白字": "FontName=Microsoft YaHei,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=6,Shadow=1,MarginV=55,Alignment=2",
    "顶部居中白字": "FontName=Microsoft YaHei,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,MarginV=60,Alignment=8",
    "超大综艺字": "FontName=Microsoft YaHei,FontSize=34,PrimaryColour=&H0000E5FF,OutlineColour=&H00000000,BorderStyle=1,Outline=5,Shadow=3,MarginV=140,Alignment=2",
}

# 转场类型 → xfade 名称
XFADE_MAP = {
    "fade": "fade",
    "slide": "slideleft",
    "zoom": "zoomin",
}


class FFmpegManager:
    """ffmpeg 命令封装"""

    @staticmethod
    def _run(cmd: list[str], timeout: int = FFMPEG_TIMEOUT) -> subprocess.CompletedProcess[str]:
        """执行命令（不抛异常，由调用方判断 returncode）"""
        logger.debug(f"执行 ffmpeg 命令: {' '.join(cmd[:6])}...")
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    # ---------- 探测 ----------

    @staticmethod
    def probe_duration(path: Path | str) -> float:
        """探测媒体时长（秒），失败返回 0.0"""
        try:
            result = subprocess.run(
            [
                ffprobe_bin(), "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        )
            if result.returncode != 0:
                return 0.0
            return round(float(result.stdout.strip()), 2)
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            return 0.0

    @staticmethod
    def probe_resolution(path: Path | str) -> str:
        """探测分辨率（宽x高），失败返回空串"""
        try:
            result = subprocess.run(
            [
                ffprobe_bin(), "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=s=x:p=0",
                str(path),
            ],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        )
            return result.stdout.strip() if result.returncode == 0 else ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""

    # ---------- 裁切与合并 ----------

    @staticmethod
    def cut_segment(
        source: Path,
        start: float,
        duration: float,
        output: Path,
        *,
        resolution: str = "",
    ) -> Path:
        """裁切单个片段

        -ss 放在 -i 之后：实现帧级精确 seek（放在前面只能定位到关键帧）
        """
        cmd = [
            ffmpeg_bin(), "-y",
            "-i", str(source),
            "-ss", f"{start:.3f}",
            "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
            "-an",
            "-avoid_negative_ts", "make_zero",
        ]

        if resolution:
            width, height = resolution.split("x", 1)
            cmd += [
                "-vf",
                # 等比放大到覆盖目标画幅后居中裁切，避免竖屏成片上下出现黑边
                f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},setsar=1,fps=30",
            ]

        cmd.append(str(output))

        result = FFmpegManager._run(cmd)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                f"视频裁切失败: {source.name}",
                code="FILE_502_001",
                detail=result.stderr[-300:],
            )
        return output

    @staticmethod
    def concat_segments(segment_paths: list[Path], output: Path) -> Path:
        """用 concat demuxer 合并片段

        关键：必须加 `-fflags +genpts` 重新生成 PTS，
        否则片段间时间戳不连续会导致时长丢失（本项目曾丢失 1.4s）。
        """
        list_file = output.parent / f"{output.stem}_filelist.txt"
        lines = []
        for p in segment_paths:
            escaped = str(p.resolve()).replace("'", "'\\''")
            lines.append(f"file '{escaped}'")
        list_file.write_text("\n".join(lines), encoding="utf-8")

        cmd = [
            ffmpeg_bin(), "-y",
            "-fflags", "+genpts",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c:v", "copy",
            "-avoid_negative_ts", "make_zero",
            str(output),
        ]
        result = FFmpegManager._run(cmd)

        if result.returncode != 0 or not output.exists():
            # 回退：重编码合并（重编码会重新计算时间戳，绝对准确）
            logger.warning("concat demuxer 失败，回退到重编码合并")
            cmd = [
                ffmpeg_bin(), "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(list_file),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-r", "30", "-fps_mode", "cfr",
                "-avoid_negative_ts", "make_zero",
                str(output),
            ]
            result = FFmpegManager._run(cmd)
            if result.returncode != 0 or not output.exists():
                raise ExternalServiceError(
                    "视频合并失败",
                    code="FILE_502_002",
                    detail=result.stderr[-300:],
                )

        list_file.unlink(missing_ok=True)
        return output

    @staticmethod
    def cut_and_merge_fast(
        segments: list[tuple[Path, float, float]],
        output: Path,
        *,
        resolution: str = "1080x1920",
    ) -> Path:
        """快速方案：单条 ffmpeg 命令 + concat filter（只编码一次）

        Args:
            segments: [(源文件, 起始秒, 结束秒), ...]
            output: 输出文件
            resolution: 目标分辨率 "宽x高"
        """
        if not segments:
            raise ExternalServiceError("没有可裁切的片段", code="FILE_422_005")

        width, height = resolution.split("x", 1)

        cmd: list[str] = [ffmpeg_bin(), "-y"]
        for src, _, _ in segments:
            cmd += ["-i", str(src)]

        filters: list[str] = []
        labels: list[str] = []
        for i, (_, start, end) in enumerate(segments):
            filters.append(
                f"[{i}:v]trim=start={start:.3f}:end={end:.3f},"
                f"setpts=PTS-STARTPTS,"
                # 等比放大到覆盖目标画幅后居中裁切，避免竖屏成片上下出现黑边
                f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},"
                f"setsar=1,fps=30[v{i}]"
            )
            labels.append(f"[v{i}]")

        filters.append(f"{''.join(labels)}concat=n={len(segments)}:v=1:a=0[outv]")
        cmd += [
            "-filter_complex", ";".join(filters),
            "-map", "[outv]",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-an",
            "-avoid_negative_ts", "make_zero",
            str(output),
        ]

        result = FFmpegManager._run(cmd)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "视频快速裁切合并失败",
                code="FILE_502_003",
                detail=result.stderr[-300:],
            )
        return output

    @staticmethod
    def merge_clips_with_transitions(
        clips: list[Path],
        boundaries: list[dict[str, object]],
        output: Path,
        *,
        crf: int = 23,
        preset: str = "medium",
        pad_to: float | None = None,
    ) -> Path:
        """按边界转场合并已裁切好的片段

        Args:
            clips: 已裁切片段（同分辨率/帧率/编码参数）
            boundaries: 长度 = len(clips)-1，元素 {type, duration}；
                type=none 表示直切，其余进入 xfade
            output: 输出文件
            crf/preset: 转场片段的重编码质量
            pad_to: 目标总时长（通常取音频时长）；不足时用最后一帧补齐

        Returns:
            输出文件路径
        """
        if not clips:
            raise ExternalServiceError("没有可合并的片段", code="FILE_422_005")
        if len(clips) == 1:
            if pad_to and FFmpegManager.probe_duration(clips[0]) < pad_to:
                pad = pad_to - FFmpegManager.probe_duration(clips[0])
                return FFmpegManager._pad_clip(clips[0], pad, output, crf=crf, preset=preset)
            return FFmpegManager._copy(clips[0], output)

        durations = [FFmpegManager.probe_duration(p) for p in clips]

        # 按直切边界分组：组内用 xfade，组间用 concat
        groups: list[list[int]] = [[0]]
        group_trans: list[list[dict[str, object]]] = [[]]
        for i in range(1, len(clips)):
            boundary = boundaries[i - 1] if i - 1 < len(boundaries) else {"type": "none"}
            if str(boundary.get("type", "none")) != "none":
                groups[-1].append(i)
                group_trans[-1].append(boundary)
            else:
                groups.append([i])
                group_trans.append([])

        group_outputs: list[Path] = []
        for gi, (indexes, transitions) in enumerate(zip(groups, group_trans)):
            if len(indexes) == 1:
                group_outputs.append(clips[indexes[0]])
                continue
            group_out = output.parent / f".group_{gi + 1:02d}.mp4"
            FFmpegManager._xfade_group(
                [clips[i] for i in indexes],
                [durations[i] for i in indexes],
                transitions,
                group_out,
                crf=crf,
                preset=preset,
            )
            group_outputs.append(group_out)

        if len(group_outputs) > 1:
            merged = output.parent / f".merged_{output.stem}.mp4"
            FFmpegManager.concat_segments(group_outputs, merged)
            FFmpegManager.safe_move(merged, output)
        else:
            FFmpegManager.safe_move(group_outputs[0], output)

        # 补齐总时长（转场会缩短视频，需要与音频对齐）
        if pad_to:
            actual = FFmpegManager.probe_duration(output)
            if actual + 0.05 < pad_to:
                padded = output.parent / f".padded_{output.stem}.mp4"
                FFmpegManager._pad_clip(output, pad_to - actual, padded, crf=crf, preset=preset)
                FFmpegManager.safe_move(padded, output)

        for p in group_outputs:
            if p.name.startswith(".group_"):
                p.unlink(missing_ok=True)
        return output

    @staticmethod
    def _xfade_group(
        clips: list[Path],
        durations: list[float],
        transitions: list[dict[str, object]],
        output: Path,
        *,
        crf: int,
        preset: str,
    ) -> Path:
        """组内 xfade 链（每段转场时长按两侧片段时长夹取）"""
        cmd: list[str] = [ffmpeg_bin(), "-y"]
        for clip in clips:
            cmd += ["-i", str(clip)]

        filters: list[str] = []
        for i in range(len(clips)):
            filters.append(f"[{i}:v]setpts=PTS-STARTPTS[v{i}]")

        base_label = "v0"
        acc = durations[0]
        for i in range(1, len(clips)):
            raw = transitions[i - 1] if i - 1 < len(transitions) else {"type": "fade", "duration": 0.5}
            ttype = XFADE_MAP.get(str(raw.get("type", "fade")), "fade")
            wanted = float(raw.get("duration", 0.5))
            d = max(0.05, min(wanted, durations[i - 1] * 0.45, durations[i] * 0.45))
            offset = max(acc - d, 0.0)
            out_label = f"x{i}"
            filters.append(
                f"[{base_label}][v{i}]xfade=transition={ttype}:duration={d:.3f}:offset={offset:.3f}[{out_label}]"
            )
            acc = acc + durations[i] - d
            base_label = out_label

        cmd += [
            "-filter_complex", ";".join(filters),
            "-map", f"[{base_label}]",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-pix_fmt", "yuv420p", "-r", "30",
            "-an",
            str(output),
        ]
        result = FFmpegManager._run(cmd)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "转场合并失败",
                code="FILE_502_007",
                detail=result.stderr[-300:],
            )
        return output

    @staticmethod
    def _pad_clip(src: Path, pad: float, output: Path, *, crf: int, preset: str) -> Path:
        """用最后一帧补齐时长"""
        pad = max(pad, 0.0)
        cmd = [
            ffmpeg_bin(), "-y", "-i", str(src),
            "-vf", f"tpad=stop_mode=clone:stop_duration={pad:.3f}",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-pix_fmt", "yuv420p", "-r", "30", "-an",
            str(output),
        ]
        result = FFmpegManager._run(cmd)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "视频补时长失败",
                code="FILE_502_008",
                detail=result.stderr[-300:],
            )
        return output

    # ---------- 音视频处理 ----------

    @staticmethod
    def merge_audio_video(video: Path, audio: Path, output: Path) -> Path:
        """音视频合并（视频流 copy，音频转 aac，取较长者时长）

        当视频更长时给音频补静音（apad），保证音轨覆盖整片。
        """
        video_duration = FFmpegManager.probe_duration(video)
        audio_duration = FFmpegManager.probe_duration(audio)
        duration = max(video_duration, audio_duration)

        cmd = [
            ffmpeg_bin(), "-y",
            "-i", str(video), "-i", str(audio),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
        ]
        if video_duration > audio_duration + 0.1:
            cmd += ["-af", "apad"]
        if duration > 0:
            cmd += ["-t", f"{duration:.3f}"]
        cmd.append(str(output))

        result = FFmpegManager._run(cmd)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "音视频合并失败",
                code="FILE_502_004",
                detail=result.stderr[-300:],
            )
        return output

    @staticmethod
    def mix_bgm(
        video: Path,
        bgm: Path,
        output: Path,
        *,
        volume: int = 30,
        ducking: bool = True,
        duck_level: int = 30,
        fade_in: float = 0.6,
        fade_out: float = 0.8,
        loop: bool = True,
    ) -> Path:
        """把 BGM 混入成片音轨（支持人声闪避与首尾淡入淡出）

        Args:
            video: 已含人声音轨的视频
            bgm: 背景音乐
            output: 输出文件
            volume: BGM 基准音量百分比（0~100）
            ducking: 人声出现时是否自动压低音乐
            duck_level: 人声出现时保留的音乐百分比（5~100）
            fade_in/fade_out: 音乐淡入/淡出时长（秒）
            loop: BGM 短于成片时是否循环

        Returns:
            输出文件路径
        """
        duration = FFmpegManager.probe_duration(video)
        if duration <= 0:
            raise ExternalServiceError("无法读取成片时长，BGM 混音中止", code="FILE_422_005")

        level = max(0, min(int(volume), 100)) / 100.0
        fade_in = max(0.0, min(fade_in, duration))
        fade_out = max(0.0, min(fade_out, duration - fade_in))
        fade_out_start = max(duration - fade_out, 0.0)
        # sidechaincompress 的 ratio 与「保留比例」近似互为倒数
        duck_ratio = max(1.0, 100.0 / max(int(duck_level), 5))

        cmd: list[str] = [ffmpeg_bin(), "-y", "-i", str(video)]
        if loop:
            cmd += ["-stream_loop", "-1"]
        cmd += ["-i", str(bgm)]

        bgm_chain = (
            f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,"
            f"asetpts=PTS-STARTPTS,apad,atrim=duration={duration:.3f},"
            f"volume={level:.3f}"
        )
        if fade_in > 0:
            bgm_chain += f",afade=t=in:st=0:d={fade_in:.3f}"
        if fade_out > 0:
            bgm_chain += f",afade=t=out:st={fade_out_start:.3f}:d={fade_out:.3f}"

        filters = [
            f"[0:a]aformat=sample_rates=44100:channel_layouts=stereo,asetpts=PTS-STARTPTS[voice]",
            f"{bgm_chain}[bgm]",
        ]
        if ducking:
            filters += [
                # 人声作为 sidechain，音乐作为被压缩信号
                f"[bgm][voice]sidechaincompress=threshold=0.02:ratio={duck_ratio:.2f}:"
                f"attack=20:release=350:makeup=1[bgmduck]",
                f"[voice][bgmduck]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]",
            ]
        else:
            filters += [
                f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]",
            ]

        cmd += [
            "-filter_complex", ";".join(filters),
            "-map", "0:v:0", "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{duration:.3f}",
            str(output),
        ]
        result = FFmpegManager._run(cmd)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "BGM 混音失败",
                code="FILE_502_010",
                detail=result.stderr[-400:],
            )
        return output

    @staticmethod
    def build_title_card(
        output: Path,
        *,
        title: str,
        subtitle: str = "",
        duration: float = 3.0,
        resolution: str = "1080x1920",
        background_color: str = "#0F1117",
        text_color: str = "#FFFFFF",
        image_path: Path | None = None,
        fps: int = 30,
    ) -> Path:
        """生成片头/片尾字卡（标题 + 副标题 + 淡入淡出 + 静音音轨）"""
        try:
            width, height = (int(v) for v in resolution.lower().split("x", 1))
        except ValueError:
            width, height = 1080, 1920

        cmd: list[str] = [ffmpeg_bin(), "-y"]
        if image_path:
            cmd += ["-loop", "1", "-i", str(image_path)]
        else:
            cmd += ["-f", "lavfi", "-i", f"color=c={background_color}:s={width}x{height}:r={fps}:d={duration:.3f}"]
        cmd += ["-f", "lavfi", "-t", f"{duration:.3f}", "-i", "anullsrc=r=44100:cl=stereo"]

        filters: list[str] = []
        if image_path:
            filters.append(
                f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},setsar=1,fps={fps}[card]"
            )
            base = "[card]"
        else:
            base = "[0:v]"

        # 半透明压暗条，保证任何背景图上文字都可读
        box_y = int(height * 0.30)
        box_h = int(height * 0.26)
        filters.append(
            f"{base}drawbox=x=0:y={box_y}:w={width}:h={box_h}:color=black@0.35:t=fill[cardbox]"
        )
        text_color_ff = text_color.replace("#", "0x")
        fade_out_start = max(duration - 0.4, 0)
        # 字号同时受画幅高度与文本长度约束，避免长标题左右溢出
        max_text_width = int(width * 0.86)
        font_title = min(
            max(int(height * 0.060), 28),
            max(int(max_text_width / max(len(title.strip()), 1)), 20),
        )
        font_sub = min(
            max(int(height * 0.034), 18),
            max(int(max_text_width / max(len(subtitle.strip()), 1)), 16),
        )

        if title.strip():
            title_file = output.parent / f".{output.stem}_title.txt"
            title_file.write_text(title.strip(), encoding="utf-8")
            filters.append(
                f"[cardbox]drawtext=fontfile='{FFmpegManager._drawtext_font()}':"
                f"textfile='{FFmpegManager._escape_filter_path(title_file)}':"
                f"expansion=none:fontsize={font_title}:fontcolor={text_color_ff}:"
                f"x=(w-text_w)/2:y=h*0.40[cardtitle]"
            )
            base = "[cardtitle]"
        else:
            base = "[cardbox]"

        if subtitle.strip():
            sub_file = output.parent / f".{output.stem}_subtitle.txt"
            sub_file.write_text(subtitle.strip(), encoding="utf-8")
            filters.append(
                f"{base}drawtext=fontfile='{FFmpegManager._drawtext_font()}':"
                f"textfile='{FFmpegManager._escape_filter_path(sub_file)}':"
                f"expansion=none:fontsize={font_sub}:fontcolor={text_color_ff}:"
                f"x=(w-text_w)/2:y=h*0.47[cardsub]"
            )
            base = "[cardsub]"

        filters.append(
            f"{base}fade=t=in:st=0:d=0.4,fade=t=out:st={fade_out_start:.3f}:d=0.4,"
            f"format=yuv420p[vout]"
        )
        filters.append("[1:a]aformat=sample_rates=44100:channel_layouts=stereo[aout]")

        cmd += [
            "-filter_complex", ";".join(filters),
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-r", str(fps), "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{duration:.3f}",
            str(output),
        ]
        result = FFmpegManager._run(cmd)
        for tmp in output.parent.glob(f".{output.stem}_*.txt"):
            tmp.unlink(missing_ok=True)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "片头/片尾字卡生成失败",
                code="FILE_502_011",
                detail=result.stderr[-400:],
            )
        return output

    @staticmethod
    def join_cards(
        body: Path,
        output: Path,
        *,
        intro: Path | None = None,
        outro: Path | None = None,
        crf: int = 23,
        preset: str = "medium",
    ) -> Path:
        """把片头 / 正片 / 片尾按顺序拼接（统一重编码，避免时间戳错乱）"""
        cards: list[Path] = []
        if intro:
            cards.append(intro)
        cards.append(body)
        if outro:
            cards.append(outro)

        cmd: list[str] = [ffmpeg_bin(), "-y"]
        for card in cards:
            cmd += ["-i", str(card)]

        filters: list[str] = []
        labels: list[str] = []
        for i in range(len(cards)):
            filters.append(f"[{i}:v]setsar=1,fps=30[v{i}]")
            filters.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo[a{i}]")
            labels.append(f"[v{i}][a{i}]")
        filters.append(f"{''.join(labels)}concat=n={len(cards)}:v=1:a=1[outv][outa]")

        cmd += [
            "-filter_complex", ";".join(filters),
            "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "192k",
            str(output),
        ]
        result = FFmpegManager._run(cmd)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "片头/片尾拼接失败",
                code="FILE_502_012",
                detail=result.stderr[-400:],
            )
        return output

    @staticmethod
    def export_cover(video: Path, output: Path, time: float = 1.0) -> Path:
        """从成片指定时间点导出封面图（JPEG）"""
        duration = FFmpegManager.probe_duration(video)
        stamp = max(0.0, min(time, max(duration - 0.05, 0.0)))
        cmd = [
            ffmpeg_bin(), "-y",
            "-ss", f"{stamp:.3f}",
            "-i", str(video),
            "-frames:v", "1",
            "-q:v", "2",
            str(output),
        ]
        result = FFmpegManager._run(cmd)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "封面帧导出失败",
                code="FILE_502_013",
                detail=result.stderr[-300:],
            )
        return output

    @staticmethod
    def _drawtext_font() -> str:
        """选择可用的中文字体路径（filter 转义格式）"""
        candidates = [
            Path("C:/Windows/Fonts/msyh.ttc"),
            Path("C:/Windows/Fonts/msyhbd.ttc"),
            Path("C:/Windows/Fonts/simhei.ttf"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate.as_posix().replace(":", r"\:")
        return ""

    @staticmethod
    def _escape_filter_path(path: Path) -> str:
        """filter 内路径转义（Windows 盘符冒号）"""
        return str(path.resolve()).replace("\\", "/").replace(":", r"\:")

    @staticmethod
    def finalize_video(
        video: Path,
        output: Path,
        *,
        srt_file: Path | None = None,
        style: str = "默认白字黑描边",
        avatar_path: Path | None = None,
        avatar: dict[str, object] | None = None,
        crf: int = 23,
        preset: str = "medium",
    ) -> Path:
        """一次性完成字幕烧录 + 主持人人像圆形叠加

        人像处理：圆形 alpha 蒙版 → 描边圆环 → 可选阴影 → overlay，
        支持四角定位、尺寸占比、出现时间段。
        """
        has_avatar = bool(avatar_path and avatar and avatar.get("file_id"))
        if not srt_file and not has_avatar:
            return FFmpegManager._copy(video, output)

        resolution = FFmpegManager.probe_resolution(video) or "1080x1920"
        try:
            width, height = (int(v) for v in resolution.lower().split("x", 1))
        except ValueError:
            width, height = 1080, 1920

        cmd: list[str] = [ffmpeg_bin(), "-y", "-i", str(video)]
        filters: list[str] = []
        base = "[0:v]"

        if srt_file:
            escaped_srt = str(srt_file.resolve()).replace("\\", "/").replace(":", r"\:")
            force_style = SUBTITLE_STYLES.get(style, SUBTITLE_STYLES["默认白字黑描边"])
            filters.append(
                f"[0:v]subtitles='{escaped_srt}':force_style='{force_style}'[sub]"
            )
            base = "[sub]"

        if has_avatar:
            cmd += ["-i", str(avatar_path)]
            filters.extend(
                FFmpegManager._avatar_filters(width, height, avatar or {}, base)
            )
            map_label = "[outv]"
        else:
            if srt_file:
                filters.append(f"{base}null[outv]")
            map_label = "[outv]" if srt_file else "0:v:0"

        cmd += [
            "-filter_complex", ";".join(filters),
            "-map", map_label,
            "-map", "0:a?",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            str(output),
        ]
        result = FFmpegManager._run(cmd)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "字幕/人像处理失败",
                code="FILE_502_009",
                detail=result.stderr[-400:],
            )
        return output

    @staticmethod
    def _avatar_filters(
        width: int,
        height: int,
        avatar: dict[str, object],
        base_label: str,
    ) -> list[str]:
        """生成圆形头像 + 描边 + 阴影的滤镜链"""
        short_side = min(width, height)
        size = max(int(short_side * float(avatar.get("size_ratio", 0.18))), 48)
        border = int(avatar.get("border_width", 4) or 0)
        outer = size + border * 2

        rr, gg, bb = FFmpegManager._hex_to_rgb(str(avatar.get("border_color") or "#FFFFFF"))
        circle_outer = (
            f"if(lte(pow(X-{outer / 2:.1f},2)+pow(Y-{outer / 2:.1f},2),pow({outer / 2:.1f},2)),255,0)"
        )
        circle_inner = (
            f"if(lte(pow(X-{size / 2:.1f},2)+pow(Y-{size / 2:.1f},2),pow({size / 2:.1f},2)),255,0)"
        )

        margin = int(short_side * 0.025)
        position = str(avatar.get("position", "bottom_right"))
        x = margin if "left" in position else width - outer - margin
        y = margin if "top" in position else height - outer - margin

        start = float(avatar.get("start", 0) or 0)
        end = avatar.get("end")
        if end is None:
            enable = f"gte(t,{start:.2f})"
        else:
            enable = f"between(t,{start:.2f},{float(end):.2f})"

        filters = [
            f"color=c=#{rr:02X}{gg:02X}{bb:02X}:s={outer}x{outer}:d=1,format=rgba,"
            f"geq=r={rr}:g={gg}:b={bb}:a='{circle_outer}'[ring]",
            f"[1:v]scale={size}:{size}:force_original_aspect_ratio=increase,"
            f"crop={size}:{size},format=rgba,"
            f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='{circle_inner}'[av]",
            f"[ring][av]overlay={(outer - size) // 2}:{(outer - size) // 2}[avc]",
        ]

        if avatar.get("shadow", True):
            shadow_circle = (
                f"if(lte(pow(X-{outer / 2:.1f},2)+pow(Y-{outer / 2:.1f},2),pow({outer / 2:.1f},2)),140,0)"
            )
            filters += [
                f"color=c=black:s={outer}x{outer}:d=1,format=rgba,"
                f"geq=r=0:g=0:b=0:a='{shadow_circle}',boxblur=8:8[sh]",
                f"{base_label}[sh]overlay={x + 6}:{y + 6}:enable='{enable}'[b1]",
                f"[b1][avc]overlay={x}:{y}:enable='{enable}'[outv]",
            ]
        else:
            filters.append(f"{base_label}[avc]overlay={x}:{y}:enable='{enable}'[outv]")

        return filters

    @staticmethod
    def _hex_to_rgb(value: str) -> tuple[int, int, int]:
        """#RRGGBB → (r, g, b)"""
        raw = value.lstrip("#")
        if len(raw) == 3:
            raw = "".join(c * 2 for c in raw)
        try:
            return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
        except (ValueError, IndexError):
            return 255, 255, 255

    @staticmethod
    def concat_audio(audio_paths: list[Path], output: Path) -> Path:
        """多音频顺序合并"""
        if len(audio_paths) == 1:
            return FFmpegManager._copy(audio_paths[0], output)

        list_file = output.parent / f"{output.stem}_audiolist.txt"
        lines = []
        for p in audio_paths:
            escaped = str(p.resolve()).replace("'", "'\\''")
            lines.append(f"file '{escaped}'")
        list_file.write_text("\n".join(lines), encoding="utf-8")

        cmd = [
            ffmpeg_bin(), "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c:a", "aac", "-b:a", "192k",
            str(output),
        ]
        result = FFmpegManager._run(cmd)
        list_file.unlink(missing_ok=True)

        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "音频合并失败",
                code="FILE_502_005",
                detail=result.stderr[-300:],
            )
        return output

    @staticmethod
    def burn_subtitles(video: Path, srt_file: Path, output: Path, style: str = "默认白字黑描边") -> Path:
        """字幕烧录"""
        force_style = SUBTITLE_STYLES.get(style, SUBTITLE_STYLES["默认白字黑描边"])
        # Windows 路径中的 \ 和 : 需要转义，否则 filter 解析失败
        escaped_srt = str(srt_file.resolve()).replace("\\", "/").replace(":", r"\:")

        cmd = [
            ffmpeg_bin(), "-y",
            "-i", str(video),
            "-vf", f"subtitles='{escaped_srt}':force_style='{force_style}'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy",
            str(output),
        ]
        result = FFmpegManager._run(cmd)
        if result.returncode != 0 or not output.exists():
            raise ExternalServiceError(
                "字幕烧录失败",
                code="FILE_502_006",
                detail=result.stderr[-300:],
            )
        return output

    @staticmethod
    def _copy(src: Path, dst: Path) -> Path:
        """文件复制"""
        import shutil

        shutil.copy2(src, dst)
        return dst

    @staticmethod
    def safe_move(src: Path, dst: Path) -> Path:
        """安全移动（Windows 文件占用时降级重试）"""
        import os
        import shutil
        import time

        dst.parent.mkdir(parents=True, exist_ok=True)

        # 1. 删除已存在的目标
        for _ in range(5):
            try:
                if dst.exists():
                    dst.unlink()
                break
            except OSError:
                time.sleep(0.8)

        # 2. os.replace
        try:
            os.replace(src, dst)
            return dst
        except OSError:
            pass

        # 3. copy2 + 删除源
        try:
            shutil.copy2(src, dst)
            src.unlink(missing_ok=True)
            return dst
        except OSError:
            pass

        # 4. 带时间戳的备用名
        stamp = time.strftime("%Y%m%d_%H%M%S")
        fallback = dst.with_name(f"{dst.stem}_{stamp}{dst.suffix}")
        shutil.copy2(src, fallback)
        src.unlink(missing_ok=True)
        return fallback


def sanitize_filename(name: str, default: str = "output") -> str:
    """文件名清理（去非法字符 + 限长）"""
    cleaned = re.sub(r'[\\/:*?"<>|]', "_", name or default)
    cleaned = re.sub(r"[\r\n\t]", "", cleaned)
    cleaned = re.sub(r"\s+", "_", cleaned).strip("_.")
    if not cleaned:
        cleaned = default
    if len(cleaned) > 96:
        cleaned = cleaned[:96]
    return cleaned


ProgressCallback = Callable[[int], None]
