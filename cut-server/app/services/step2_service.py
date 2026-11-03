"""
Step2 服务：口播长文
===================
- generate：基于 Step1 大纲生成口播长文（不落库，前端可反复重新生成）
- save：保存长文；skip_tts=False 时提交异步 TTS 任务
- load：读取已保存的长文
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.managers.ai_manager import AIManager
from app.models.creation import Creation
from app.schemas import Step2GenerateResponse, Step2SaveResponse, TTSConfig
from app.services.step1_service import Step1Service
from app.services.step_service import StepService

logger = get_logger()


class Step2Service:
    """Step2 业务逻辑"""

    def __init__(self, db: Session):
        self.db = db
        self.ai = AIManager()

    def generate(
        self,
        *,
        creation: Creation,
        title: str | None = None,
        subtitle: str | None = None,
    ) -> Step2GenerateResponse:
        """生成口播长文（不落库）

        Args:
            creation: 创作实例
            title: 标题（为空则用 Step1 大纲中的参考标题）
            subtitle: 副标题

        Returns:
            {title, content, word_count}
        """
        step1_payload = Step1Service(self.db).load_payload(creation)
        form = step1_payload.get("form") or {}
        outline = step1_payload.get("outline") or {}

        final_title = title or self._pick_title(outline, form)
        final_subtitle = subtitle or self._pick_subtitle(outline)

        article_title, content, word_count = self.ai.generate_long_article(
            title=final_title,
            subtitle=final_subtitle,
            author=form.get("author", ""),
            intro=form.get("intro", ""),
            style=form.get("style", "热血安利"),
            target_duration=int(form.get("target_duration", 70)),
            outline=outline,
        )

        logger.info(
            "Step2 口播长文生成完成",
            extra={"creation_id": creation.id, "word_count": word_count},
        )
        return Step2GenerateResponse(
            title=article_title,
            content=content,
            word_count=word_count,
        )

    def save(
        self,
        *,
        creation: Creation,
        title: str,
        content: str,
        word_count: int,
        skip_tts: bool,
        tts_config: TTSConfig | None = None,
    ) -> Step2SaveResponse:
        """保存口播长文（step_no=2）

        Args:
            creation: 创作实例
            title: 标题
            content: 正文
            word_count: 字数
            skip_tts: 是否跳过自动 TTS
            tts_config: 多音色配置（全局音色 + 段落覆盖）

        Returns:
            {creation_id, current_step, tts_task_id}
        """
        if not word_count:
            word_count = len(re.sub(r"\s", "", content))

        payload: dict[str, Any] = {
            "long_article": {
                "title": title,
                "content": content,
                "word_count": word_count,
            }
        }
        if tts_config:
            payload["tts_config"] = tts_config.model_dump()

        tts_task_id: str | None = None
        if not skip_tts:
            tts_task_id = self._submit_tts(creation, title, content, tts_config)

        StepService(self.db).save_step_result(
            creation_id=creation.id,
            step_no=2,
            payload=payload,
            user_id=creation.user_id,
        )

        return Step2SaveResponse(
            creation_id=creation.id,
            current_step=creation.current_step,
            tts_task_id=tts_task_id,
        )

    def load(self, creation: Creation) -> Step2GenerateResponse | None:
        """读取已保存的口播长文"""
        result = StepService(self.db).get_step_result(creation.id, 2)
        if not result:
            return None
        payload = result.payload or {}
        article = payload.get("long_article") or {}
        config = payload.get("tts_config")
        return Step2GenerateResponse(
            title=article.get("title", ""),
            content=article.get("content", ""),
            word_count=article.get("word_count", 0),
            tts_config=TTSConfig.model_validate(config) if config else None,
        )

    # ---------- 内部工具 ----------

    def _submit_tts(
        self,
        creation: Creation,
        title: str,
        content: str,
        tts_config: TTSConfig | None = None,
    ) -> str | None:
        """提交异步 TTS 任务"""
        from app.tasks.task_queue import TYPE_TTS, task_queue

        audio_name = self._safe_filename(title) + ".mp3"
        segments = self._build_segments(content, tts_config)
        try:
            return task_queue.submit(
                task_type=TYPE_TTS,
                user_id=creation.user_id,
                payload={
                    "creation_id": creation.id,
                    "script": content,
                    "filename": audio_name,
                    "provider": (tts_config.provider if tts_config else None),
                    "voice_id": (tts_config.global_voice_id if tts_config else None),
                    "segments": segments,
                },
            )
        except ValueError as e:
            # 任务队列未启动（如测试环境），记录日志但不阻断保存
            logger.warning(f"TTS 任务提交失败: {e}", extra={"creation_id": creation.id})
            return None

    @staticmethod
    def _build_segments(content: str, config: TTSConfig | None) -> list[dict[str, Any]]:
        """把 TTS 配置展开为逐段合成参数"""
        if config and config.segments:
            result: list[dict[str, Any]] = []
            for seg in config.segments:
                result.append(
                    {
                        "text": seg.text,
                        "voice_id": seg.voice_id or config.global_voice_id,
                        "rate": seg.rate if seg.rate else config.rate,
                        "pitch": seg.pitch if seg.pitch else config.pitch,
                        "volume": seg.volume if seg.volume else config.volume,
                        "pause_after_ms": seg.pause_after_ms or config.paragraph_gap_ms,
                    }
                )
            return result

        paragraphs = [p.strip() for p in re.split(r"\n+", content) if p.strip()]
        return [
            {
                "text": p,
                "voice_id": config.global_voice_id if config else "female_sweet",
                "rate": config.rate if config else 0,
                "pitch": config.pitch if config else 0,
                "volume": config.volume if config else 0,
                "pause_after_ms": config.paragraph_gap_ms if config else 300,
            }
            for p in paragraphs
        ]

    def _audio_dir(self, creation: Creation) -> Path:
        """音频输出目录（项目工作目录）"""
        path = settings.workdir_abs / creation.id / "audio"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _safe_filename(name: str) -> str:
        """文件名清理（禁止路径分隔符等非法字符）"""
        cleaned = re.sub(r'[\\/:*?"<>|]', "_", name or "audio")
        cleaned = re.sub(r"\s+", "_", cleaned).strip("_.")
        return (cleaned or "audio")[:80]

    @staticmethod
    def _pick_title(outline: dict[str, Any], form: dict[str, Any]) -> str:
        """从大纲参考标题中挑一个，没有则用表单标题"""
        ref_titles = outline.get("ref_titles") or []
        if ref_titles:
            first = ref_titles[0]
            if isinstance(first, dict):
                return str(first.get("title", "")) or str(form.get("title", ""))
            return str(first)
        return str(form.get("title", ""))

    @staticmethod
    def _pick_subtitle(outline: dict[str, Any]) -> str:
        """从大纲参考标题中取副标题"""
        ref_titles = outline.get("ref_titles") or []
        if ref_titles and isinstance(ref_titles[0], dict):
            return str(ref_titles[0].get("subtitle", ""))
        return ""
