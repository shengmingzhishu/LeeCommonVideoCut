"""
视频扫描与时间标记管理器
=========================
- 扫描 video_dir 下的视频文件，用 ffprobe 探测时长
- 随机生成时间段标记（5~15 秒随机段长，以音频时长为锚）

标记算法要点（对齐旧版已验证实现）：
- 段长 5~15 秒随机，避免切片过短
- 起点在 [0, 视频时长 - 段长] 内随机，保证不越界
- 三重上限保护：最大片段数、最大迭代次数、空片段连续次数
- 目标总时长以音频时长为锚（留 2 秒余量）
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logger import get_logger
from app.utils.ffmpeg import ffprobe_available

logger = get_logger()

SUPPORTED_VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"}

# 单段时长范围（秒）
MIN_SEGMENT_SECONDS = 5.0
MAX_SEGMENT_SECONDS = 15.0

# 目标总时长相对音频的余量（秒）
DURATION_MARGIN = 2.0

# 无音频时的兜底目标时长（秒）
FALLBACK_TARGET_DURATION = 72.0


class VideoMarkerManager:
    """视频扫描 + 随机时间段标记"""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.workdir = settings.workdir_abs

    @property
    def output_path(self) -> Path:
        """Step3 产物路径（mark 落盘）"""
        path = self.workdir / self.project_id / "video"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def scan(self, video_dir: str) -> list[dict]:
        """扫描视频目录

        Args:
            video_dir: 视频素材目录

        Returns:
            [{"name", "path", "duration_seconds", "duration"}]

        Raises:
            ValidationError: ffprobe 不可用、目录不存在或无视频
        """
        if not ffprobe_available():
            raise ValidationError("ffprobe 未安装，无法扫描视频", code="FILE_422_001")

        if not video_dir or not Path(video_dir).is_dir():
            raise ValidationError(f"视频目录不存在: {video_dir}", code="FILE_422_002")

        vdir = Path(video_dir)
        files: list[dict] = []
        for f in sorted(vdir.rglob("*")):
            if not f.is_file() or f.suffix.lower() not in SUPPORTED_VIDEO_EXT:
                continue
            duration = self._probe_duration(str(f))
            if duration is None or duration <= 1:
                continue
            files.append(
                {
                    "name": f.name,
                    "path": str(f),
                    "duration_seconds": round(duration, 1),
                    "duration": self._fmt_duration(duration),
                }
            )

        if not files:
            raise ValidationError(
                f"视频目录 {video_dir} 下未找到视频文件（支持 {', '.join(sorted(SUPPORTED_VIDEO_EXT))}）",
                code="FILE_422_003",
            )

        logger.info(
            "视频扫描完成",
            extra={
                "project_id": self.project_id,
                "video_count": len(files),
                "total_seconds": sum(f["duration_seconds"] for f in files),
            },
        )
        return files

    def generate_marks(
        self,
        *,
        video_files: list[dict],
        target_duration: float,
        seed: int | None = None,
    ) -> list[dict]:
        """随机生成视频片段标记

        Args:
            video_files: scan() 的结果
            target_duration: 目标总时长（秒）
            seed: 随机种子（便于复现）

        Returns:
            [{"id", "source", "start", "end", "duration", "muted"}]

        Raises:
            ValidationError: 没有可用视频
        """
        if not video_files:
            raise ValidationError("没有可用视频文件", code="FILE_422_004")

        rng = random.Random(seed)

        # 上限保护：最大片段数 = 10 ~ 50，随目标时长增长
        max_segments = min(50, max(10, int(target_duration / 5) + 5))
        max_iterations = max_segments * 8

        marks: list[dict] = []
        current_total = 0.0
        empty_streak = 0
        iterations = 0

        while current_total < target_duration and len(marks) < max_segments:
            if empty_streak > 10 or iterations >= max_iterations:
                break
            iterations += 1

            video = rng.choice(video_files)
            video_duration = video["duration_seconds"]

            # 段长 5~15 秒随机，不超过剩余目标
            remaining = target_duration - current_total
            seg = rng.uniform(MIN_SEGMENT_SECONDS, MAX_SEGMENT_SECONDS)
            if remaining < MIN_SEGMENT_SECONDS:
                seg = remaining
            if seg > remaining:
                seg = remaining

            if seg < 0.5:
                empty_streak += 1
                continue

            if video_duration < 0.5:
                empty_streak += 1
                continue

            # 起点与段长：保证 start + seg <= 视频时长（短视频则整段取用）
            if video_duration <= seg:
                start = 0.0
                seg = round(video_duration, 2)
            else:
                start = rng.uniform(0, video_duration - seg)

            marks.append(
                {
                    "id": len(marks) + 1,
                    "source": video["name"],
                    "start": round(start, 2),
                    "end": round(start + seg, 2),
                    "duration": round(seg, 2),
                    "muted": True,
                }
            )
            current_total += seg
            empty_streak = 0

        logger.info(
            "视频标记生成完成",
            extra={
                "project_id": self.project_id,
                "marker_count": len(marks),
                "total_seconds": round(current_total, 2),
                "target_seconds": round(target_duration, 2),
            },
        )
        return marks

    def save_marks(self, marks: list[dict]) -> Path:
        """标记落盘（markers.json）"""
        path = self.output_path / "markers.json"
        total = sum(m["duration"] for m in marks)
        path.write_text(
            json.dumps(
                {"marks": marks, "total_duration": round(total, 2)},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return path

    def load_marks(self) -> list[dict]:
        """读取已保存的标记"""
        path = self.output_path / "markers.json"
        if not path.is_file():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("marks", [])
        except (json.JSONDecodeError, OSError):
            return []

    # ---------- 内部工具 ----------

    @staticmethod
    def _probe_duration(file_path: str) -> float | None:
        """ffprobe 探测时长（秒）"""
        import subprocess

        try:
            out = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    file_path,
                ],
                capture_output=True, text=True, timeout=30,
            )
            if out.returncode != 0:
                return None
            return float(out.stdout.strip())
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            return None

    @staticmethod
    def _fmt_duration(seconds: float) -> str:
        """秒 → MM:SS / HH:MM:SS"""
        s = int(seconds)
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"
