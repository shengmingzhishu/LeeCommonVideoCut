"""
视频标记管理器单元测试
======================
覆盖：随机切片算法、时长上限保护、边界条件。
"""
from __future__ import annotations

import pytest

from app.managers.video_marker_manager import (
    MAX_SEGMENT_SECONDS,
    MIN_SEGMENT_SECONDS,
    VideoMarkerManager,
)


def _videos(count: int = 3, duration: float = 60.0) -> list[dict]:
    """构造测试用视频列表"""
    return [
        {
            "name": f"clip{i}.mp4",
            "path": f"/tmp/clip{i}.mp4",
            "duration_seconds": duration,
            "duration": "01:00",
        }
        for i in range(count)
    ]


class TestGenerateMarks:
    """随机标记生成"""

    def test_basic_count(self):
        vm = VideoMarkerManager("test_proj")
        marks = vm.generate_marks(video_files=_videos(), target_duration=30.0, seed=42)
        assert len(marks) > 0
        assert all("source" in m and "start" in m and "end" in m for m in marks)

    def test_ids_are_sequential(self):
        vm = VideoMarkerManager("test_proj")
        marks = vm.generate_marks(video_files=_videos(), target_duration=30.0, seed=1)
        assert [m["id"] for m in marks] == list(range(1, len(marks) + 1))

    def test_segment_duration_in_range(self):
        """段长应在 5~15 秒之间（最后一段可能更短）"""
        vm = VideoMarkerManager("test_proj")
        marks = vm.generate_marks(video_files=_videos(), target_duration=60.0, seed=7)
        for m in marks[:-1]:
            assert MIN_SEGMENT_SECONDS - 0.01 <= m["duration"] <= MAX_SEGMENT_SECONDS + 0.01

    def test_start_within_video_bounds(self):
        """起点 + 时长不能超出视频时长"""
        vm = VideoMarkerManager("test_proj")
        videos = _videos(count=2, duration=20.0)
        marks = vm.generate_marks(video_files=videos, target_duration=30.0, seed=3)
        durations = {v["name"]: v["duration_seconds"] for v in videos}
        for m in marks:
            assert m["start"] >= 0
            assert m["end"] <= durations[m["source"]] + 0.01

    def test_total_duration_close_to_target(self):
        """总时长接近目标（最后一次可能略短）"""
        vm = VideoMarkerManager("test_proj")
        marks = vm.generate_marks(video_files=_videos(), target_duration=45.0, seed=11)
        total = sum(m["duration"] for m in marks)
        assert total <= 45.0 + 0.5
        assert total >= 45.0 - MAX_SEGMENT_SECONDS

    def test_max_segments_cap(self):
        """超长目标时长时片段数不超过上限"""
        vm = VideoMarkerManager("test_proj")
        marks = vm.generate_marks(video_files=_videos(), target_duration=10000.0, seed=5)
        assert len(marks) <= 50

    def test_short_video_no_crash(self):
        """视频时长小于最小段长时不应崩溃"""
        vm = VideoMarkerManager("test_proj")
        marks = vm.generate_marks(
            video_files=_videos(count=1, duration=2.0), target_duration=30.0, seed=2
        )
        assert isinstance(marks, list)

    def test_empty_video_files_raises(self):
        from app.core.exceptions import ValidationError

        vm = VideoMarkerManager("test_proj")
        with pytest.raises(ValidationError):
            vm.generate_marks(video_files=[], target_duration=30.0)

    def test_seed_is_reproducible(self):
        """相同 seed 应产生相同结果"""
        vm = VideoMarkerManager("test_proj")
        a = vm.generate_marks(video_files=_videos(), target_duration=30.0, seed=99)
        b = vm.generate_marks(video_files=_videos(), target_duration=30.0, seed=99)
        assert a == b


class TestSaveAndLoad:
    """标记落盘与读取"""

    def test_save_and_load(self, tmp_path, monkeypatch):
        import app.managers.video_marker_manager as mod

        monkeypatch.setattr(mod.settings, "workdir", tmp_path)

        vm = VideoMarkerManager("proj_save")
        marks = vm.generate_marks(video_files=_videos(), target_duration=20.0, seed=1)
        path = vm.save_marks(marks)
        assert path.exists()

        loaded = vm.load_marks()
        assert len(loaded) == len(marks)
        assert loaded[0]["source"] == marks[0]["source"]

    def test_load_missing_returns_empty(self, tmp_path, monkeypatch):
        import app.managers.video_marker_manager as mod

        monkeypatch.setattr(mod.settings, "workdir", tmp_path)
        vm = VideoMarkerManager("proj_missing")
        assert vm.load_marks() == []
