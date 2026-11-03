"""
AI 大模型管理器
===============
封装 MiniMax M3（OpenAI 兼容协议）的调用，提供 Step1 大纲与 Step2 口播长文生成。

设计要点：
- 单一职责：只做 AI 调用与输出清洗，不含业务规则
- 失败统一抛 ExternalServiceError（HTTP 502），由上层转业务异常
- JSON 解析有容错：AI 常返回 markdown 围栏或混入解释文字
"""
from __future__ import annotations

import json
import re
import time
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logger import get_logger

logger = get_logger()

# 文案风格 → 风格描述（供 Prompt 注入）
STYLE_DESCRIPTIONS = {
    "热血安利": "用热情澎湃的语气推荐，像资深漫剧粉一样真情实感地安利，让观众也想立刻追下去",
    "客观测评": "用客观中立的口吻分析剧情与制作水准，褒贬分明、有理有据，像专业影评人",
    "悬念种草": "用制造悬念的方式吊胃口，频繁设置信息差与反转钩子，让观众必须看到结尾",
    "剧情向": "聚焦剧情本身的冲突与反转，用讲故事的方式带领观众沉浸其中",
}

DEFAULT_STYLE = "热血安利"

# 快捷选项 → 生成目标（对应 Step1 表单的 goals）
GOAL_TEXT_MAP = {
    "intro_episode": "本次长文目标为介绍当前短句的关联剧集的片段，保证给出有价值有质量的剧情内容",
    "random_story": "随机一个故事钩子",
    "random_character": "随机一个有价值的人物介绍",
    "random_perspective": "随机一个任务视角介绍",
}


class AIManager:
    """MiniMax M3 调用封装"""

    def __init__(self) -> None:
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        """惰性创建 OpenAI 客户端（OpenAI 兼容协议指向 MiniMax）"""
        if self._client is None:
            self._client = OpenAI(
                api_key=settings.minimax_api_key,
                base_url=settings.minimax_base_url,
                timeout=120.0,
            )
        return self._client

    def _chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.8,
        max_tokens: int = 2000,
    ) -> str:
        """调用大模型，返回文本内容

        Raises:
            ExternalServiceError: 调用失败或返回为空
        """
        for attempt in range(2):
            try:
                resp = self.client.chat.completions.create(
                    model=settings.minimax_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                break
            except Exception as e:
                wait = self._retry_after_seconds(e)
                if attempt == 0 and wait is not None:
                    logger.warning(
                        "AI 服务限流，等待后重试",
                        extra={"model": settings.minimax_model, "wait_seconds": wait},
                    )
                    time.sleep(wait)
                    continue
                logger.error(
                    f"AI 调用失败: {type(e).__name__}",
                    extra={"model": settings.minimax_model},
                    exc_info=e,
                )
                raise ExternalServiceError(
                    "AI 服务调用失败，请稍后重试",
                    code="COMMON_502_001",
                    detail=f"{type(e).__name__}: {e}",
                ) from e

        content = resp.choices[0].message.content if resp.choices else ""
        if not content:
            raise ExternalServiceError(
                "AI 返回内容为空，请重试",
                code="COMMON_502_002",
            )
        return content.strip()

    # ---------- Step1：大纲生成 ----------

    def generate_outline(
        self,
        *,
        title: str,
        author: str,
        intro: str,
        style: str = DEFAULT_STYLE,
        target_duration: int = 70,
        keywords: list[str] | None = None,
        ref_titles: list[str] | None = None,
        value_points: list[str] | None = None,
        goals: list[str] | None = None,
        kb_context: str = "",
    ) -> dict[str, Any]:
        """生成 Step1 大纲

        Args:
            title: 漫剧标题
            author: 作者
            intro: 简介
            style: 文案风格
            target_duration: 目标口播时长（秒）
            keywords: 用户自定义关键词
            ref_titles: 用户参考标题
            value_points: 用户补充价值点
            goals: 快捷选项（见 GOAL_TEXT_MAP）
            kb_context: 关联剧集文本 / 资料摘要

        Returns:
            {
                "core_keywords": [...],
                "core_words": [...],
                "ref_titles": [{"title": ..., "subtitle": ...}],
                "main_task": "...",
                "core_value": [...],
                "keypoints": [...]
            }

        Raises:
            ExternalServiceError: AI 调用失败
        """
        system_prompt = (
            "你是一位资深的漫剧推广文案策划专家，擅长从漫剧作品中提炼核心卖点和传播要素。"
            "你需要基于给定的漫剧信息与参考资料，输出结构化的大纲，严格以 JSON 格式返回。"
        )

        parts: list[str] = [
            f"标题：{title or '未提供'}",
            f"作者：{author or '未提供'}",
            f"简介：{intro or '未提供'}",
            f"目标口播时长：{target_duration} 秒",
            f"文案风格：{STYLE_DESCRIPTIONS.get(style, style)}",
        ]

        if keywords:
            parts.append(f"用户指定关键词：{', '.join(keywords)}")
        if ref_titles:
            parts.append(f"用户参考标题：{', '.join(ref_titles)}")
        if value_points:
            parts.append(f"用户补充价值点：{', '.join(value_points)}")
        if goals:
            goal_texts = [GOAL_TEXT_MAP[g] for g in goals if g in GOAL_TEXT_MAP]
            if goal_texts:
                parts.append("本次生成目标：\n- " + "\n- ".join(goal_texts))
        if kb_context:
            parts.append(f"关联资料摘要：\n{kb_context}")

        parts.append(
            "请输出 JSON，字段要求：\n"
            "{\n"
            '  "core_keywords": ["3~8 个核心关键词，包含人物名/主题/题材"],\n'
            '  "core_words": ["3~8 个更精炼的标签词"],\n'
            '  "ref_titles": [{"title": "参考标题", "subtitle": "副标题"}],  // 3 组\n'
            '  "main_task": "本次口播的主要任务描述（1 段话）",\n'
            '  "core_value": ["3~5 个核心价值点"],\n'
            '  "keypoints": ["3~5 个关键点"]\n'
            "}\n"
            "只返回 JSON，不要其他解释。"
        )

        raw = self._chat(
            system_prompt=system_prompt,
            user_prompt="\n".join(parts),
            temperature=0.8,
            max_tokens=2000,
        )
        return self._normalize_outline(self._parse_json(raw), title=title)

    # ---------- Step2：口播长文 ----------

    def generate_long_article(
        self,
        *,
        title: str,
        subtitle: str = "",
        author: str = "",
        intro: str = "",
        style: str = DEFAULT_STYLE,
        target_duration: int = 70,
        outline: dict[str, Any] | None = None,
        kb_context: str = "",
    ) -> tuple[str, str, int]:
        """生成口播长文（纯文本）

        Args:
            title: 标题
            subtitle: 副标题
            author: 作者
            intro: 简介
            style: 文案风格
            target_duration: 目标时长（秒）
            outline: Step1 生成的大纲
            kb_context: 关联资料摘要

        Returns:
            (标题, 正文, 字数)

        Raises:
            ExternalServiceError: AI 调用失败
        """
        system_prompt = (
            "你是一位专业的短视频口播文案写手。"
            "请直接输出完整的口播文案纯文本正文，"
            "不要输出 JSON、不要输出代码块、不要输出大纲结构、不要输出任何标记符号。"
            "只输出可以直接朗读的口播文案文字。"
        )

        target_words = int(target_duration * 3.5)  # 中文口播约 3.5 字/秒
        outline = outline or {}

        parts: list[str] = [
            f"标题：{title or '未提供'}",
            f"副标题：{subtitle or '无'}",
            f"作者：{author or '未提供'}",
            f"简介：{intro or '未提供'}",
            f"风格要求：{STYLE_DESCRIPTIONS.get(style, style)}",
            f"字数要求：约 {target_words} 字（对应 {target_duration} 秒口播）",
        ]

        if outline.get("core_keywords"):
            parts.append(f"核心关键词：{', '.join(outline['core_keywords'])}")
        if outline.get("core_words"):
            parts.append(f"核心词：{', '.join(outline['core_words'])}")
        if outline.get("main_task"):
            parts.append(f"主要任务：{outline['main_task']}")
        if outline.get("core_value"):
            parts.append(f"核心价值：{', '.join(outline['core_value'])}")
        if outline.get("keypoints"):
            parts.append(f"关键点：{', '.join(outline['keypoints'])}")
        if kb_context:
            parts.append(f"参考资料：\n{kb_context}")

        parts.append(
            "写作要求：\n"
            "1. 开头 3 秒必须有强钩子抓住注意力\n"
            "2. 节奏紧凑，口语化，能直接朗读\n"
            "3. 结尾有号召行动\n"
            "4. 不要输出标题行，正文直接从第一句话开始"
        )

        raw = self._chat(
            system_prompt=system_prompt,
            user_prompt="\n".join(parts),
            temperature=0.85,
            max_tokens=3000,
        )
        return self._normalize_long_article(raw, fallback_title=title)

    # ---------- 内部工具 ----------

    @staticmethod
    def _retry_after_seconds(error: Exception) -> int | None:
        """解析限流错误中的等待秒数（仅对 402/429 且带 Retry after 的响应生效）

        MiniMax 余额不足的 402 不含 Retry after，不会误触发重试。
        """
        if getattr(error, "status_code", None) not in (402, 429):
            return None
        match = re.search(r"Retry after (\d+)\s*s", str(error), re.IGNORECASE)
        if not match:
            return None
        return min(int(match.group(1)) + 1, 90)

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        """从 AI 输出中提取 JSON 对象（兼容 markdown 围栏、前后解释文字）"""
        text = raw.strip()

        # 剥离 ```json ... ``` 围栏
        fence = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.DOTALL)
        if fence:
            text = fence.group(1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 截取第一个 { 到最后一个 }
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass

        logger.warning("AI 输出无法解析为 JSON，返回空结果")
        return {}

    @staticmethod
    def _normalize_outline(data: dict[str, Any], *, title: str) -> dict[str, Any]:
        """规整大纲结构（补齐缺失字段、统一类型）"""
        ref_titles: list[dict[str, str]] = []
        for item in data.get("ref_titles") or []:
            if isinstance(item, str):
                ref_titles.append({"title": item, "subtitle": ""})
            elif isinstance(item, dict) and item.get("title"):
                ref_titles.append(
                    {"title": str(item.get("title", "")), "subtitle": str(item.get("subtitle", ""))}
                )

        def _str_list(key: str) -> list[str]:
            return [str(x) for x in (data.get(key) or []) if x]

        return {
            "core_keywords": _str_list("core_keywords"),
            "core_words": _str_list("core_words"),
            "ref_titles": ref_titles,
            "main_task": str(data.get("main_task") or ""),
            "core_value": _str_list("core_value"),
            "keypoints": _str_list("keypoints"),
        }

    @staticmethod
    def _normalize_long_article(raw: str, *, fallback_title: str) -> tuple[str, str, int]:
        """规整长文输出：剥离围栏、剥离 JSON 包装、拆分标题与正文"""
        text = raw.strip()

        # 剥离 ``` 围栏
        fence = re.search(r"```(?:\w+)?\s*(.+?)\s*```", text, re.DOTALL)
        if fence:
            text = fence.group(1).strip()

        # AI 有时仍返回 JSON，从键中取正文
        joined_outline = False
        if text.startswith("{"):
            try:
                obj = json.loads(text)
                for key in ("script", "content", "文案", "正文", "text", "article"):
                    if obj.get(key):
                        text = str(obj[key])
                        break
                else:
                    outline = obj.get("outline")
                    if isinstance(outline, list):
                        text = "\n".join(str(x) for x in outline)
                        joined_outline = True
            except json.JSONDecodeError:
                pass

        # 去掉行尾残留的 JSON 标记（如 '"script": "'）
        text = re.sub(r'^\s*"?(?:script|content|文案|正文)"?\s*:\s*"?', "", text)
        text = re.sub(r'"?\s*,?\s*$', "", text)
        text = text.replace("\\n", "\n").replace('\\"', '"')

        # 首行较短且不以句末标点结尾时视为标题
        lines = text.split("\n")
        article_title = fallback_title
        first = lines[0].strip()
        if (
            len(lines) > 1
            and 0 < len(first) <= 30
            and not first.endswith(("。", "！", "？", "!", "?", "，", ",", "、", "…"))
            and not joined_outline
        ):
            article_title = first
            text = "\n".join(lines[1:]).strip()

        word_count = len(re.sub(r"\s", "", text))
        return article_title, text, word_count
