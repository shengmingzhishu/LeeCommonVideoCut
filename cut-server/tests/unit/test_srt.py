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


class TestSingleLineCues:
    """字幕保证单行展示"""

    def test_newlines_collapsed(self):
        srt = generate_srt([{"text": "第一行\n第二行", "start": 0, "end": 2}])
        assert "第一行 第二行" in srt
        assert "第一行\n第二行" not in srt

    def test_long_text_split_into_single_line_cues(self):
        text = "如果你也是青春懵懂与财富好奇心爆棚的那种人，那就别眨眼，跟我一起走进港岛少年"
        srt = generate_srt([{"text": text, "start": 0, "end": 10}], max_chars=18)
        blocks = [b for b in srt.strip().split("\n\n") if b]
        assert len(blocks) > 1
        for block in blocks:
            lines = block.split("\n")
            assert len(lines) == 3, "每条字幕只能是「序号 + 时间轴 + 单行文本」"
            assert len(lines[2]) <= 19
        # 拆分后仍覆盖原始时间轴
        assert "00:00:00,000" in blocks[0]
        assert "00:00:10,000" in blocks[-1]

    def test_split_timeline_is_contiguous(self):
        srt = generate_srt(
            [{"text": "一二三四五六七八九十一二三四五六七八九十", "start": 0, "end": 8}],
            max_chars=10,
        )
        times = [
            line
            for line in srt.splitlines()
            if "-->" in line
        ]
        assert len(times) >= 2
        end_of_previous = None
        for line in times:
            start, end = (part.strip() for part in line.split("-->"))
            if end_of_previous is not None:
                assert start == end_of_previous
            end_of_previous = end

    def test_style_based_max_chars(self):
        from app.managers.ffmpeg_manager import FFmpegManager

        assert FFmpegManager.subtitle_max_chars("默认白字黑描边") == 18
        assert FFmpegManager.subtitle_max_chars("超大综艺字") < 18
        assert FFmpegManager.subtitle_max_chars("不存在的样式") == 18


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
