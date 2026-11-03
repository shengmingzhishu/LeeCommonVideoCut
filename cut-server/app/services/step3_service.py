"""
Step3 服务：音视频素材
======================
- media_list：获取音频与视频素材列表（系统音频 + 自定义录音 + 视频）
- remark：对勾选视频重新随机标记（目标时长以音频时长为锚）
- save_state：保存素材选择状态
- compose：提交一键合成任务（异步）
- list_outputs：完成页的多次合成列表
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.logger import get_logger
from app.managers.video_marker_manager import (
    FALLBACK_TARGET_DURATION,
    SUPPORTED_VIDEO_EXT,
    VideoMarkerManager,
)
from app.models.creation import Creation
from app.models.episode import Episode
from app.models.output import Output
from app.models.project import Project
from app.services.step_service import StepService
from app.utils.safe_path import gen_id

logger = get_logger()

SUPPORTED_AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".webm", ".ogg"}


def parse_force_style(force_style: str) -> dict[str, Any]:
    """解析 ffmpeg force_style，抽出前端预览需要的数值参数"""
    fields: dict[str, str] = {}
    for chunk in force_style.split(","):
        if "=" in chunk:
            key, value = chunk.split("=", 1)
            fields[key.strip()] = value.strip()

    def _num(key: str, default: float) -> float:
        try:
            return float(fields.get(key, default))
        except (TypeError, ValueError):
            return default

    return {
        "font_size": int(_num("FontSize", 18)),
        "margin_v": int(_num("MarginV", 30)),
        "alignment": int(_num("Alignment", 2)),
        "outline": _num("Outline", 1),
        "border_style": int(_num("BorderStyle", 1)),
        "primary_colour": fields.get("PrimaryColour", "&H00FFFFFF"),
        "outline_colour": fields.get("OutlineColour", "&H00000000"),
        "back_colour": fields.get("BackColour", "&H00000000"),
    }


def normalize_markers(
    markers: list[dict[str, Any]],
    durations: dict[str, float],
) -> list[dict[str, Any]]:
    """按素材真实时长收敛标记（防越界切片 / 防路径穿越）

    Args:
        markers: 前端提交的标记
        durations: 素材文件名 → 时长（秒）

    Raises:
        ValidationError: 源文件非法、不存在或片段过短
    """
    normalized: list[dict[str, Any]] = []
    for index, mark in enumerate(markers, start=1):
        source = str(mark.get("source") or "").strip()
        if len(Path(source).parts) != 1 or source in {"", ".", ".."}:
            raise ValidationError("非法视频源文件名", code="STEP3_422_003")
        total = float(durations.get(source, 0) or 0)
        if total <= 0:
            raise ValidationError(f"视频源不存在或时长为 0: {source}", code="STEP3_422_003")

        start = max(0.0, float(mark.get("start", 0) or 0))
        if start >= total:
            start = max(0.0, total - 0.5)
        end = min(float(mark.get("end", 0) or 0), total)
        if end <= start:
            end = min(total, start + 0.5)
        if end - start < 0.2:
            raise ValidationError(f"片段时长过短: {source}", code="STEP3_422_004")

        item = dict(mark)
        item["id"] = int(mark.get("id") or index)
        item["source"] = source
        item["start"] = round(start, 3)
        item["end"] = round(end, 3)
        item["duration"] = round(end - start, 3)
        normalized.append(item)
    return normalized


class Step3Service:
    """Step3 业务逻辑"""

    def __init__(self, db: Session):
        self.db = db

    # ---------- 素材列表 ----------

    def media_list(self, creation: Creation) -> dict[str, Any]:
        """获取音频与视频素材列表

        Returns:
            {
                "system_audios": [...],
                "custom_audios": [...],
                "video_files": [...],
                "deleted_audio_paths": [...],
                "deleted_video_paths": [...],
            }
        """
        state = self._load_state(creation)

        audio_dir = settings.workdir_abs / creation.id / "audio"
        system_audios = self._list_system_audios(audio_dir)
        custom_audios = self._list_custom_audios(audio_dir)

        # 默认策略：有系统音频则自定义音频全不选
        deleted_audio = set(state.get("deleted_audio_paths", []))
        for item in system_audios:
            item["selected"] = item["path"] not in deleted_audio
        for item in custom_audios:
            item["selected"] = (
                item["path"] not in deleted_audio and not system_audios
            )

        video_files = self._list_videos(creation, state)

        return {
            "system_audios": system_audios,
            "custom_audios": custom_audios,
            "video_files": video_files,
            "deleted_audio_paths": sorted(deleted_audio),
            "deleted_video_paths": sorted(state.get("deleted_video_paths", [])),
        }

    # ---------- 批量上传绑定 / 字幕样式 ----------

    def bind_video_sources(
        self,
        *,
        creation: Creation,
        file_ids: list[str],
    ) -> dict[str, Any]:
        """把已上传的视频文件绑定为当前创作的素材目录

        上传文件落在同一用户目录下，取其公共父目录写入 project.video_dir。

        Returns:
            {"video_files": [...]}（与 media-list 的视频项结构一致）
        """
        from app.models.file import File
        from app.services.project_service import ProjectService

        project = self._get_project(creation)
        for file_id in file_ids:
            record = self.db.get(File, file_id)
            if not record or record.user_id != creation.user_id:
                raise NotFoundError(f"文件不存在: {file_id}", code="FILE_404_001")
            path = Path(record.path)
            if not path.is_file():
                raise NotFoundError(f"文件已被移除: {record.path}", code="FILE_404_002")
            if path.suffix.lower() not in SUPPORTED_VIDEO_EXT:
                raise ValidationError(f"不是支持的视频文件: {path.name}", code="FILE_422_003")

        project.video_dir = ProjectService(self.db)._resolve_video_dir(
            creation.user_id, file_ids
        )
        self.db.commit()
        self.db.refresh(project)

        logger.info(
            "Step3 绑定上传视频素材",
            extra={"creation_id": creation.id, "file_count": len(file_ids)},
        )
        return {"video_files": self._list_videos(creation, self._load_state(creation))}

    def subtitle_styles(self) -> list[dict[str, Any]]:
        """字幕模板清单 + 烧录端真实参数（前端据此等比换算预览）"""
        from app.managers.ffmpeg_manager import SUBTITLE_STYLES

        return [
            {"name": name, "force_style": force_style, **parse_force_style(force_style)}
            for name, force_style in SUBTITLE_STYLES.items()
        ]

    # ---------- 随机标记 ----------

    def markers(self, *, creation: Creation) -> dict[str, Any]:
        """读取已保存的视频标记与素材时长（刷新后恢复手动指定）

        Returns:
            {markers, total_duration, video_files}
        """
        project = self._get_project(creation)
        vm = VideoMarkerManager(creation.id)
        marks = vm.load_marks()
        videos = vm.scan(project.video_dir or "")
        total = round(sum(float(m.get("duration") or 0) for m in marks), 3)
        return {"markers": marks, "total_duration": total, "video_files": videos}

    def save_markers(self, *, creation: Creation, marks: list[dict[str, Any]]) -> dict[str, Any]:
        """保存手动编辑后的视频标记（刷新后仍可恢复）

        Args:
            creation: 创作实例
            marks: 前端提交的标记列表（含 start / end / duration）

        Returns:
            {markers, total_duration, video_files}
        """
        project = self._get_project(creation)
        vm = VideoMarkerManager(creation.id)
        vm.save_marks(marks)
        videos = vm.scan(project.video_dir or "")
        total = round(sum(float(m.get("duration") or 0) for m in marks), 3)
        logger.info(
            "Step3 手动标记已保存",
            extra={"creation_id": creation.id, "marker_count": len(marks)},
        )
        return {"markers": marks, "total_duration": total, "video_files": videos}

    def remark(
        self,
        *,
        creation: Creation,
        video_files: list[str],
        target_duration: int | None,
    ) -> dict[str, Any]:
        """对勾选视频重新随机标记

        目标时长推导规则（对齐旧版）：
        - 有系统音频 → 音频总时长
        - 无系统音频但有自定义录音 → 最长录音时长
        - 都无 → 兜底 72 秒

        Args:
            creation: 创作实例
            video_files: 参与标记的视频文件名（为空则用全部）
            target_duration: 指定目标时长（为空则自动推导）

        Returns:
            {markers_path, marker_count, total_duration, sources_used, video_files, markers}
        """
        project = self._get_project(creation)
        vm = VideoMarkerManager(creation.id)

        all_videos = vm.scan(project.video_dir or "")
        if video_files:
            selected = [v for v in all_videos if v["name"] in set(video_files)]
            if not selected:
                raise ValidationError(
                    "勾选的视频不存在或无有效时长", code="FILE_422_006"
                )
        else:
            selected = all_videos

        duration = (
            float(target_duration)
            if target_duration
            else self._derive_target_duration(creation)
        )

        marks = vm.generate_marks(video_files=selected, target_duration=duration)
        markers_path = vm.save_marks(marks)

        total = sum(m["duration"] for m in marks)
        sources_used = sorted({m["source"] for m in marks})

        logger.info(
            "Step3 视频标记完成",
            extra={
                "creation_id": creation.id,
                "marker_count": len(marks),
                "total_duration": round(total, 2),
            },
        )

        return {
            "markers_path": str(markers_path.relative_to(settings.workdir_abs).as_posix()),
            "marker_count": len(marks),
            "total_duration": round(total, 2),
            "sources_used": sources_used,
            "video_files": [
                {
                    "name": v["name"],
                    "duration": v["duration_seconds"],
                    "duration_str": v["duration"],
                    "selected": True,
                }
                for v in selected
            ],
            "markers": marks,
        }

    # ---------- 保存状态 ----------

    def save_state(
        self,
        *,
        creation: Creation,
        audio_files: list[dict[str, Any]],
        video_files: list[dict[str, Any]],
        deleted_media: dict[str, list[str]],
        compose_settings: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """保存素材选择状态（step_no=3）"""
        payload: dict[str, Any] = {
            "audio_files": audio_files,
            "video_files": video_files,
            "deleted_media": deleted_media,
        }
        if compose_settings:
            payload["compose_settings"] = compose_settings
        StepService(self.db).save_step_result(
            creation_id=creation.id,
            step_no=3,
            payload=payload,
            user_id=creation.user_id,
        )
        return {"creation_id": creation.id, "current_step": creation.current_step}

    # ---------- 合成 ----------

    def compose(
        self,
        *,
        creation: Creation,
        audio_files: list[str],
        markers: list[dict[str, Any]],
        fast_mode: bool,
        resolution: str,
        subtitle_style: str,
        subtitle_position: dict[str, Any] | None = None,
        global_transition: dict[str, Any] | None = None,
        avatar: dict[str, Any] | None = None,
        quality: dict[str, Any] | None = None,
        bgm: dict[str, Any] | None = None,
        intro_outro: dict[str, Any] | None = None,
    ) -> str:
        """提交一键合成任务（异步）

        Returns:
            task_id
        """
        from app.tasks.task_queue import TYPE_COMPOSE, task_queue

        if not markers:
            raise ValidationError("没有视频标记，无法合成", code="STEP3_422_001")
        if not audio_files:
            raise ValidationError("没有选中音频，无法合成", code="STEP3_422_002")

        project = self._get_project(creation)

        # 按素材真实时长收敛切片：避免前端按段换素材后越界导致合成失败
        try:
            scanned = VideoMarkerManager(creation.id).scan(project.video_dir or "")
        except ValidationError as e:
            raise ValidationError("素材目录不可用，无法校验视频标记", code="STEP3_422_003") from e
        durations = {v["name"]: float(v["duration_seconds"]) for v in scanned}
        markers = normalize_markers(markers, durations)

        return task_queue.submit(
            task_type=TYPE_COMPOSE,
            user_id=creation.user_id,
            payload={
                "creation_id": creation.id,
                "video_dir": project.video_dir or "",
                "audio_paths": audio_files,
                "markers": markers,
                "resolution": resolution,
                "subtitle_style": subtitle_style,
                "subtitle_position": subtitle_position,
                "fast_mode": fast_mode,
                "global_transition": global_transition or {"type": "none", "duration": 0.5},
                "avatar": avatar,
                "quality": quality or {"resolution": resolution, "crf": 23, "preset": "medium"},
                "bgm": bgm,
                "intro_outro": intro_outro,
            },
        )

    # ---------- 封面导出 ----------

    def export_cover(
        self,
        *,
        creation: Creation,
        output_path: str | None = None,
        time: float | None = None,
    ) -> Path:
        """从成片指定时间点导出封面图

        Args:
            creation: 创作（用于所有权与路径边界校验）
            output_path: 成片路径（工作区相对路径）；为空取该创作最新成片
            time: 截取时间点（秒），默认 1.0

        Returns:
            导出的 JPEG 路径
        """
        from app.managers.ffmpeg_manager import FFmpegManager

        if output_path:
            rel = Path(output_path)
            if rel.is_absolute():
                raise ForbiddenError("非法文件路径", code="FILE_403_001")
            target = (settings.workdir_abs / rel).resolve()
        else:
            outputs = self.list_outputs(creation)
            if not outputs:
                raise NotFoundError("该创作还没有成片", code="FILE_404_001")
            target = (settings.workdir_abs / outputs[0].output_path).resolve()

        base = (settings.workdir_abs / creation.id).resolve()
        try:
            target.relative_to(base)
        except ValueError as e:
            raise ForbiddenError("非法文件路径", code="FILE_403_001") from e
        if not target.is_file():
            raise NotFoundError(f"成片不存在: {target.name}", code="FILE_404_001")

        stamp = 1.0 if time is None else max(float(time), 0.0)
        cover = target.parent / f"cover_{stamp:.1f}s.jpg"
        FFmpegManager.export_cover(target, cover, stamp)
        logger.info(
            "封面帧导出完成",
            extra={"creation_id": creation.id, "time": stamp, "cover": cover.name},
        )
        return cover

    # ---------- 完成页 ----------

    def list_outputs(self, creation: Creation) -> list[Output]:
        """完成页：该创作的多次合成列表（版本倒序 = 最新置顶）"""
        stmt = (
            select(Output)
            .where(Output.creation_id == creation.id)
            .order_by(Output.version.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def record_output(
        self,
        *,
        creation_id: str,
        output_path: str,
        duration: float,
        file_size: int,
        resolution: str,
    ) -> Output:
        """登记一次合成结果"""
        stmt = select(func.max(Output.version)).where(Output.creation_id == creation_id)
        version = (self.db.execute(stmt).scalar() or 0) + 1

        output = Output(
            id=gen_id("o"),
            creation_id=creation_id,
            version=version,
            output_path=output_path,
            duration=duration,
            file_size=file_size,
            resolution=resolution,
        )
        self.db.add(output)
        self.db.commit()
        self.db.refresh(output)
        return output

    # ---------- 内部工具 ----------

    def resolve_preview_path(self, creation: Creation, scope: str, name: str) -> Path:
        """解析串播预览文件路径（防路径穿越）

        Args:
            creation: 创作
            scope: video（项目素材目录）/ audio（创作音频目录）
            name: video 为文件名；audio 为音频目录下的相对路径或工作区相对路径

        Raises:
            ValidationError: scope 非法或目录不存在
            ForbiddenError: 路径越界
            NotFoundError: 文件不存在
        """
        if scope == "video":
            project = self._get_project(creation)
            base = Path(project.video_dir or "")
            if not base.is_dir():
                raise ValidationError("项目未配置视频素材目录", code="FILE_422_002")
        elif scope == "audio":
            base = settings.workdir_abs / creation.id / "audio"
            if not base.is_dir():
                raise ValidationError("音频目录不存在", code="FILE_422_002")
        else:
            raise ValidationError(f"不支持的预览类型: {scope}", code="STEP3_422_001")

        rel = Path(name)
        if rel.is_absolute():
            raise ForbiddenError("非法文件路径", code="FILE_403_001")
        if scope == "audio" and rel.parts and rel.parts[0] == creation.id:
            target = (settings.workdir_abs / rel).resolve()
        else:
            target = (base / rel).resolve()

        try:
            target.relative_to(base.resolve())
        except ValueError as e:
            raise ForbiddenError("非法文件路径", code="FILE_403_001") from e
        if not target.is_file():
            raise NotFoundError(f"文件不存在: {name}", code="FILE_404_001")
        return target

    def _get_project(self, creation: Creation) -> Project:
        """取创作所属项目"""
        episode = self.db.get(Episode, creation.episode_id)
        if not episode:
            raise NotFoundError(f"剧集不存在: {creation.episode_id}", code="EPIS_404_001")
        project = self.db.get(Project, episode.project_id)
        if not project:
            raise NotFoundError(f"项目不存在: {episode.project_id}", code="PROJ_404_001")
        return project

    def _load_state(self, creation: Creation) -> dict[str, Any]:
        """读取 Step3 已保存的状态"""
        result = StepService(self.db).get_step_result(creation.id, 3)
        if not result:
            return {}
        payload = result.payload or {}
        deleted = payload.get("deleted_media") or {}
        return {
            "audio_files": payload.get("audio_files", []),
            "video_files": payload.get("video_files", []),
            "deleted_audio_paths": deleted.get("audio_paths", []),
            "deleted_video_paths": deleted.get("video_paths", []),
        }

    def _list_system_audios(self, audio_dir: Path) -> list[dict[str, Any]]:
        """系统音频（AI 生成）：位于 audio 目录，文件名与创作标题相关"""
        items: list[dict[str, Any]] = []
        if not audio_dir.is_dir():
            return items

        for f in sorted(audio_dir.iterdir()):
            if not f.is_file() or f.suffix.lower() not in SUPPORTED_AUDIO_EXT:
                continue
            rel = f.relative_to(settings.workdir_abs).as_posix()
            duration = self._probe_audio_duration(f)
            items.append(
                {
                    "path": rel,
                    "name": f.name,
                    "duration": duration,
                    "duration_str": self._fmt_duration(duration),
                    "source": "system",
                    "selected": True,
                }
            )
        return items

    def _list_custom_audios(self, audio_dir: Path) -> list[dict[str, Any]]:
        """自定义录音（用户上传）：upload 目录"""
        items: list[dict[str, Any]] = []
        upload_dir = audio_dir / "upload"
        if not upload_dir.is_dir():
            return items

        for f in sorted(upload_dir.iterdir()):
            if not f.is_file() or f.suffix.lower() not in SUPPORTED_AUDIO_EXT:
                continue
            rel = f.relative_to(settings.workdir_abs).as_posix()
            duration = self._probe_audio_duration(f)
            items.append(
                {
                    "path": rel,
                    "name": f.name,
                    "duration": duration,
                    "duration_str": self._fmt_duration(duration),
                    "source": "custom",
                    "selected": False,
                }
            )
        return items

    def _list_videos(self, creation: Creation, state: dict[str, Any]) -> list[dict[str, Any]]:
        """视频列表（扫描项目素材目录）"""
        project = self._get_project(creation)
        deleted = set(state.get("deleted_video_paths", []))

        try:
            scanned = VideoMarkerManager(creation.id).scan(project.video_dir or "")
        except ValidationError:
            return []

        return [
            {
                "name": v["name"],
                "duration": v["duration_seconds"],
                "duration_str": v["duration"],
                "selected": v["name"] not in deleted,
            }
            for v in scanned
        ]

    def _derive_target_duration(self, creation: Creation) -> float:
        """按音频时长推导标记目标时长"""
        audio_dir = settings.workdir_abs / creation.id / "audio"
        durations: list[float] = []

        for f in audio_dir.rglob("*") if audio_dir.is_dir() else []:
            if f.is_file() and f.suffix.lower() in SUPPORTED_AUDIO_EXT:
                d = self._probe_audio_duration(f)
                if d > 0:
                    durations.append(d)

        if not durations:
            return FALLBACK_TARGET_DURATION
        # 多段音频会被顺序拼接，目标时长应为总和而非最大值
        return sum(durations)

    @staticmethod
    def _probe_audio_duration(path: Path) -> float:
        """探测音频时长"""
        from app.managers.ffmpeg_manager import FFmpegManager

        return FFmpegManager.probe_duration(path)

    @staticmethod
    def _fmt_duration(seconds: float) -> str:
        """秒 → MM:SS"""
        s = int(seconds)
        m = (s % 3600) // 60
        sec = s % 60
        if s >= 3600:
            h = s // 3600
            return f"{h:02d}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"
