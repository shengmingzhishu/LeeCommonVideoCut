"""
Step3 标记收敛与字幕样式参数单元测试
=====================================
"""
from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.services.step3_service import (
    Step3Service,
    normalize_markers,
    parse_force_style,
)


class TestParseForceStyle:
    """force_style 解析"""

    def test_parses_core_fields(self):
        spec = parse_force_style(
            "FontSize=20,MarginV=55,Alignment=2,Outline=6,BorderStyle=1,"
            "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000"
        )
        assert spec["font_size"] == 20
        assert spec["margin_v"] == 55
        assert spec["alignment"] == 2
        assert spec["outline"] == pytest.approx(6)
        assert spec["border_style"] == 1
        assert spec["primary_colour"] == "&H00FFFFFF"

    def test_defaults_when_missing(self):
        spec = parse_force_style("FontName=Microsoft YaHei")
        assert spec["font_size"] == 18
        assert spec["margin_v"] == 30
        assert spec["alignment"] == 2

    def test_all_templates_have_metrics(self):
        styles = Step3Service(None).subtitle_styles()  # type: ignore[arg-type]
        assert len(styles) >= 10
        names = {s["name"] for s in styles}
        assert {"白底黑字条", "描边加粗白字", "顶部居中白字", "超大综艺字"} <= names
        for style in styles:
            assert style["font_size"] > 0
            assert style["margin_v"] >= 0
            assert style["force_style"]


class TestNormalizeMarkers:
    """按素材真实时长收敛标记"""

    def test_clamps_end_to_source_duration(self):
        markers = [{"id": 1, "source": "a.mp4", "start": 2.0, "end": 99.0, "duration": 97.0}]
        out = normalize_markers(markers, {"a.mp4": 10.0})
        assert out[0]["start"] == 2.0
        assert out[0]["end"] == 10.0
        assert out[0]["duration"] == pytest.approx(8.0)

    def test_start_beyond_duration_resets(self):
        markers = [{"source": "a.mp4", "start": 30.0, "end": 35.0}]
        out = normalize_markers(markers, {"a.mp4": 10.0})
        assert out[0]["start"] == 9.5
        assert out[0]["end"] == 10.0

    def test_rejects_path_traversal(self):
        with pytest.raises(ValidationError):
            normalize_markers([{"source": "../secret.mp4", "start": 0, "end": 1}], {"secret.mp4": 5})

    def test_rejects_unknown_source(self):
        with pytest.raises(ValidationError):
            normalize_markers([{"source": "missing.mp4", "start": 0, "end": 1}], {"a.mp4": 5})

    def test_rejects_too_short_segment(self):
        with pytest.raises(ValidationError):
            normalize_markers([{"source": "a.mp4", "start": 9.9, "end": 10.0}], {"a.mp4": 10.0})

    def test_preserves_transition(self):
        markers = [
            {
                "id": 3,
                "source": "a.mp4",
                "start": 0,
                "end": 2,
                "transition": {"type": "fade", "duration": 0.5},
            }
        ]
        out = normalize_markers(markers, {"a.mp4": 10.0})
        assert out[0]["transition"] == {"type": "fade", "duration": 0.5}
