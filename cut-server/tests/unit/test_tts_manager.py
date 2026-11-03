"""
TTS Manager 单元测试（不依赖真实网络与音频设备）
================================================
覆盖：音色目录完整性、语调自然区间、音色解析、文本清洗、时长校验。
"""
from __future__ import annotations

import pytest

from app.managers.tts_manager import (
    DEFAULT_VOICE_ID,
    VOICE_CATALOG,
    VOICE_MAP,
    TTSManager,
)


class TestVoiceCatalog:
    """音色目录"""

    def test_default_voice_exists(self):
        assert DEFAULT_VOICE_ID in VOICE_MAP

    def test_ids_are_unique(self):
        ids = [v["id"] for v in VOICE_CATALOG]
        assert len(ids) == len(set(ids))

    def test_covers_multiple_voices_and_styles(self):
        assert len(VOICE_CATALOG) >= 10
        assert len({v["voice"] for v in VOICE_CATALOG}) >= 9
        assert len({v["style"] for v in VOICE_CATALOG}) >= 8

    @pytest.mark.parametrize("item", VOICE_CATALOG, ids=[v["id"] for v in VOICE_CATALOG])
    def test_prosody_stays_natural(self, item):
        """语调收敛在自然区间，避免机械感与破音"""
        assert -15 <= item["rate"] <= 15
        assert -6 <= item["pitch"] <= 6
        assert -5 <= item["volume"] <= 5
        assert item["voice"].startswith("zh-")
        assert item["name"] and item["description"]


class TestResolveProfile:
    """音色解析"""

    def test_known_id(self):
        profile = TTSManager.resolve_profile("male_magnetic")
        assert profile["voice"] == "zh-CN-YunjianNeural"

    def test_unknown_falls_back_to_default(self):
        profile = TTSManager.resolve_profile("not_exists")
        assert profile["id"] == DEFAULT_VOICE_ID

    def test_raw_neural_name(self):
        profile = TTSManager.resolve_profile("zh-CN-YunxiNeural")
        assert profile["voice"] == "zh-CN-YunxiNeural"

    def test_voice_override(self):
        profile = TTSManager.resolve_profile("female_sweet", "zh-CN-XiaoyiNeural")
        assert profile["voice"] == "zh-CN-XiaoyiNeural"


class TestNormalizeText:
    """朗读文本清洗"""

    def test_remove_markdown_and_emoji(self):
        raw = "## 标题\n- **重点**：这款产品😀真的很好用！"
        assert TTSManager._normalize_text(raw) == "标题\n重点：这款产品真的很好用！"

    def test_markdown_link_keeps_text(self):
        assert TTSManager._normalize_text("看[这里](https://a.com)") == "看这里"

    def test_remove_spaces_between_chinese(self):
        assert TTSManager._normalize_text("你 好 世 界") == "你好世界"

    def test_keep_space_between_latin_words(self):
        assert TTSManager._normalize_text("AI 剪辑") == "AI 剪辑"

    def test_normalize_segments_skips_empty(self):
        segments = [
            {"text": "**第一段**"},
            {"text": "😀"},
            {"text": "第二段"},
        ]
        result = TTSManager._normalize_segments(segments, "", DEFAULT_VOICE_ID)
        assert [s["text"] for s in result] == ["第一段", "第二段"]

    def test_script_splits_paragraphs(self):
        result = TTSManager._normalize_segments(None, "第一段。\n\n第二段。", DEFAULT_VOICE_ID)
        assert [s["text"] for s in result] == ["第一段。", "第二段。"]


class TestValidateDuration:
    """时长校验"""

    def test_reject_invalid_short_audio(self):
        manager = TTSManager()
        with pytest.raises(RuntimeError, match="音频无效"):
            manager._validate_duration("edge-tts", 0.3, [{"text": "你好"}])

    def test_reject_audio_shorter_than_text(self):
        manager = TTSManager()
        with pytest.raises(RuntimeError, match="短于文本所需"):
            manager._validate_duration("edge-tts", 2.0, [{"text": "字" * 100}])

    def test_accept_valid_duration(self):
        manager = TTSManager()
        manager._validate_duration("edge-tts", 3.0, [{"text": "字" * 30}])


class TestFallbackChain:
    """引擎降级链"""

    def test_preferred_engine_first(self):
        chain = TTSManager._build_chain("pyttsx3")
        names = [name for name, _ in chain]
        assert names[0] == "pyttsx3"
        assert "sapi" in names

    def test_unknown_engine_ignored(self):
        chain = TTSManager._build_chain("not_exists")
        assert chain and all(name in {"edge-tts", "pyttsx3", "sapi"} for name, _ in chain)