"""
Step1 服务：创作信息 + AI 大纲
=============================
- generate_outline：调用 AI 生成大纲（不落库，前端可反复重新生成）
- save：保存表单 + 大纲到 step_results（step_no=1）
- load：读取已保存的表单 + 大纲
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.managers.ai_manager import AIManager
from app.models.creation import Creation
from app.models.episode import Episode
from app.schemas import Step1Form, Step1Outline, Step1SaveResponse
from app.services.step_service import StepService

logger = get_logger()

# 关联资料的字符上限（避免 prompt 过长）
MAX_KB_CHARS = 4000
# 单个文本文件的截断长度
MAX_FILE_CHARS = 2000


class Step1Service:
    """Step1 业务逻辑"""

    def __init__(self, db: Session):
        self.db = db
        self.ai = AIManager()

    def generate_outline(
        self,
        *,
        creation: Creation,
        form: Step1Form,
    ) -> Step1Outline:
        """生成大纲（不落库）

        Args:
            creation: 创作实例
            form: 创作信息表单

        Returns:
            大纲结构
        """
        kb_context = self._build_context(creation, form)

        data = self.ai.generate_outline(
            title=form.title or "",
            author=form.author or "",
            intro=form.intro or "",
            style=form.style,
            target_duration=form.target_duration,
            keywords=form.keywords,
            ref_titles=form.ref_titles,
            value_points=form.value_points,
            goals=form.goals,
            kb_context=kb_context,
        )

        logger.info(
            "Step1 大纲生成完成",
            extra={"creation_id": creation.id, "user_id": creation.user_id},
        )
        return Step1Outline(**data)

    def save(
        self,
        *,
        creation: Creation,
        form: Step1Form,
        outline: Step1Outline,
    ) -> Step1SaveResponse:
        """保存表单 + 大纲（step_no=1）"""
        payload: dict[str, Any] = {
            "form": form.model_dump(),
            "outline": outline.model_dump(),
        }
        StepService(self.db).save_step_result(
            creation_id=creation.id,
            step_no=1,
            payload=payload,
            user_id=creation.user_id,
        )
        return Step1SaveResponse(creation_id=creation.id, current_step=creation.current_step)

    def load(self, creation: Creation) -> Step1SaveResponse:
        """读取已保存的表单 + 大纲"""
        result = StepService(self.db).get_step_result(creation.id, 1)
        if not result:
            return Step1SaveResponse(creation_id=creation.id, current_step=creation.current_step)

        payload = result.payload or {}
        form_data = payload.get("form") or {}
        outline_data = payload.get("outline") or {}

        return Step1SaveResponse(
            creation_id=creation.id,
            current_step=creation.current_step,
            form=Step1Form(**form_data) if form_data else None,
            outline=Step1Outline(**outline_data) if outline_data else None,
        )

    def load_payload(self, creation: Creation) -> dict[str, Any]:
        """读取已保存的原始 payload（供 Step2 复用大纲）"""
        result = StepService(self.db).get_step_result(creation.id, 1)
        return result.payload or {} if result else {}

    # ---------- 内部工具 ----------

    def _build_context(self, creation: Creation, form: Step1Form) -> str:
        """组装关联资料上下文（关联剧集文本 + 用户指定文本文件）"""
        parts: list[str] = []
        total = 0

        # 关联剧集简介
        for episode_id in form.episode_ids:
            episode = self.db.get(Episode, episode_id)
            if episode and episode.description:
                chunk = f"[剧集 {episode.title}]\n{episode.description}"
                parts.append(chunk)
                total += len(chunk)

        # 用户指定的文本文件（每个截断）
        for path in form.text_files:
            content = self._read_text(path)
            if not content:
                continue
            chunk = f"[资料 {path.split(chr(92))[-1].split('/')[-1]}]\n{content[:MAX_FILE_CHARS]}"
            parts.append(chunk)
            total += len(chunk)
            if total >= MAX_KB_CHARS:
                break

        return "\n\n".join(parts)[:MAX_KB_CHARS]

    @staticmethod
    def _read_text(path: str) -> str:
        """读取文本文件（失败返回空串，不阻断流程）"""
        from pathlib import Path

        try:
            p = Path(path)
            if not p.is_file():
                return ""
            return p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""
