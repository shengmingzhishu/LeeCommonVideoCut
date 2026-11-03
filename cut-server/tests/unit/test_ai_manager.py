"""
AI Manager 单元测试（不依赖真实 API）
===================================
覆盖：JSON 解析容错、长文清洗、大纲结构规整。
"""
from __future__ import annotations

import pytest

from app.managers.ai_manager import AIManager


class TestParseJson:
    """JSON 解析容错"""

    def test_plain_json(self):
        assert AIManager._parse_json('{"a": 1}') == {"a": 1}

    def test_markdown_fence(self):
        raw = '```json\n{"a": 1}\n```'
        assert AIManager._parse_json(raw) == {"a": 1}

    def test_json_with_prose(self):
        raw = '好的，结果如下：{"a": 1} 希望有帮助'
        assert AIManager._parse_json(raw) == {"a": 1}

    def test_invalid_returns_empty(self):
        assert AIManager._parse_json("完全不是 JSON") == {}


class TestNormalizeOutline:
    """大纲结构规整"""

    def test_full_outline(self):
        data = {
            "core_keywords": ["萧炎", "斗气"],
            "core_words": ["逆袭"],
            "ref_titles": [{"title": "斗破苍穹", "subtitle": "少年崛起"}],
            "main_task": "介绍剧情",
            "core_value": ["热血"],
            "keypoints": ["废柴开局"],
        }
        result = AIManager._normalize_outline(data, title="斗破苍穹")
        assert result["core_keywords"] == ["萧炎", "斗气"]
        assert result["ref_titles"][0]["subtitle"] == "少年崛起"
        assert result["main_task"] == "介绍剧情"

    def test_ref_titles_as_string(self):
        """AI 可能把 ref_titles 返回成字符串数组"""
        result = AIManager._normalize_outline({"ref_titles": ["标题A"]}, title="x")
        assert result["ref_titles"] == [{"title": "标题A", "subtitle": ""}]

    def test_missing_fields_filled(self):
        result = AIManager._normalize_outline({}, title="x")
        assert result["core_keywords"] == []
        assert result["ref_titles"] == []
        assert result["main_task"] == ""


class TestNormalizeLongArticle:
    """长文清洗"""

    def test_plain_text(self):
        title, content, count = AIManager._normalize_long_article(
            "这是一段口播文案内容，用来测试清洗逻辑是否正常工作。", fallback_title="默认标题"
        )
        assert "口播文案" in content
        assert count > 0
        assert title == "默认标题"

    def test_markdown_fence_stripped(self):
        raw = "```\n第一句话。第二句话。\n```"
        _, content, _ = AIManager._normalize_long_article(raw, fallback_title="t")
        assert not content.startswith("```")
        assert "```" not in content

    def test_json_wrapper_extracted(self):
        raw = '{"script": "这是正文内容。第二句。"}'
        _, content, _ = AIManager._normalize_long_article(raw, fallback_title="t")
        assert content.startswith("这是正文内容")
        assert "script" not in content

    def test_title_split_from_first_line(self):
        raw = "斗破苍穹：少年逆袭\n正文第一句。正文第二句。"
        title, content, _ = AIManager._normalize_long_article(raw, fallback_title="默认")
        assert title == "斗破苍穹：少年逆袭"
        assert content.startswith("正文第一句")

    def test_word_count_excludes_whitespace(self):
        raw = "一二三四五六七八九十"
        _, _, count = AIManager._normalize_long_article(raw, fallback_title="t")
        assert count == 10

    def test_outline_list_joined(self):
        raw = '{"outline": ["第一段", "第二段"]}'
        _, content, _ = AIManager._normalize_long_article(raw, fallback_title="t")
        assert "第一段" in content
        assert "第二段" in content


class _FakeStatusError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


class TestRetryAfterSeconds:
    """限流等待解析（不真的 sleep）"""

    def test_rate_limit_with_retry_after(self):
        assert AIManager._retry_after_seconds(_FakeStatusError(402, "Retry after 28s")) == 29

    def test_balance_error_without_retry_after(self):
        assert AIManager._retry_after_seconds(_FakeStatusError(402, "insufficient balance (1008)")) is None

    def test_wait_capped_at_90(self):
        assert AIManager._retry_after_seconds(_FakeStatusError(429, "Retry after 300s")) == 90

    def test_other_status_not_retried(self):
        assert AIManager._retry_after_seconds(_FakeStatusError(401, "Retry after 5s")) is None


class TestStyleMap:
    """风格映射"""

    def test_known_styles(self):
        from app.managers.ai_manager import STYLE_DESCRIPTIONS

        assert "热血安利" in STYLE_DESCRIPTIONS
        assert "客观测评" in STYLE_DESCRIPTIONS

    def test_goal_map(self):
        from app.managers.ai_manager import GOAL_TEXT_MAP

        assert "intro_episode" in GOAL_TEXT_MAP
        assert len(GOAL_TEXT_MAP) == 4
