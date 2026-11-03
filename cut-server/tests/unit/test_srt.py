"""
SRT 工具单元测试
=================
"""
from __future__ import annotations

import pytest

from app.utils.srt import format_srt_time, generate_srt, generate_timestamps_from_script


class TestFormatSrtTime:
    """时间格式化"""

    def test_basic(self):
        assert format_srt_time(0) == "00:00:00,000"

    def test_with_millis(self):
        assert format_srt_time(1.5) == "00:00:01,500"

    def test_over_minute(self):
        assert format_srt_time(65.25) == "00:01:05,250"

    def test_over_hour(self):
        assert format_srt_time(3661.5) == "01:01:01,500"

    def test_negative_clamped(self):
        assert format_srt_time(-5) == "00:00:00,000"


class TestGenerateSrt:
    """SRT 生成"""

    def test_empty(self):
        assert generate_srt([]) == ""

    def test_single_entry(self):
        srt = generate_srt([{"text": "你好", "start": 0, "end": 2}])
        assert "1\n00:00:00,000 --> 00:00:02,000\n你好" in srt

    def test_index_increments(self):
        srt = generate_srt(
            [
                {"text": "A", "start": 0, "end": 1},
                {"text": "B", "start": 1, "end": 2},
            ]
        )
        assert "1\n" in srt
        assert "2\n" in srt

    def test_empty_text_skipped(self):
        srt = generate_srt([{"text": "  ", "start": 0, "end": 1}])
        assert srt == ""

    def test_end_before_start_extended(self):
        """end <= start 时自动延长 1.5 秒"""
        srt = generate_srt([{"text": "A", "start": 5, "end": 5}])
        assert "00:00:06,500" in srt


class TestGenerateTimestamps:
    """按字数比例估算时间轴"""

    def test_empty_script(self):
        assert generate_timestamps_from_script("", 10) == []

    def test_zero_duration(self):
        assert generate_timestamps_from_script("你好世界", 0) == []

    def test_sentences_split(self):
        ts = generate_timestamps_from_script("第一句话。第二句话。第三句话。", 30)
        assert len(ts) == 3
        assert ts[0]["start"] == 0

    def test_contiguous_timeline(self):
        ts = generate_timestamps_from_script("第一句话。第二句话。", 20)
        assert ts[0]["end"] == ts[1]["start"]

    def test_total_matches_duration(self):
        ts = generate_timestamps_from_script("一二三四。五六七八。", 40)
        assert ts[-1]["end"] == pytest.approx(40, abs=0.1)
