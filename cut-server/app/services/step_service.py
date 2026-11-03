"""
Step 通用服务（保存 Step 结果到 step_results + generation_history）
==================================================================
v4.0 流程共 3 步：Step1 创作信息 / Step2 口播长文 / Step3 音视频素材。
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models.creation import Creation
from app.models.history import GenerationHistory
from app.models.step_result import StepResult
from app.utils.safe_path import gen_id

logger = get_logger()

MAX_STEP_NO = 3


class StepService:
    """Step 结果的通用保存/历史逻辑"""

    def __init__(self, db: Session):
        self.db = db

    def save_step_result(
        self,
        *,
        creation_id: str,
        step_no: int,
        payload: dict[str, Any],
        user_id: str,
    ) -> StepResult:
        """保存 Step 结果（写入 step_results + generation_history）

        - step_results：每个 (creation_id, step_no, version) 唯一，写入新版本
        - generation_history：每次执行都 INSERT 一份快照

        Args:
            creation_id: 创作 ID
            step_no: 步骤号（1~3）
            payload: 结果内容（JSON 可序列化）
            user_id: 操作用户 ID

        Returns:
            新建的 StepResult
        """
        if not 1 <= step_no <= MAX_STEP_NO:
            raise ValueError(f"step_no 必须在 1~{MAX_STEP_NO} 之间，收到 {step_no}")

        stmt = select(func.max(StepResult.version)).where(
            StepResult.creation_id == creation_id,
            StepResult.step_no == step_no,
        )
        max_version = self.db.execute(stmt).scalar() or 0
        new_version = max_version + 1

        result = StepResult(
            id=gen_id("sr"),
            creation_id=creation_id,
            step_no=step_no,
            version=new_version,
            payload=payload,
        )
        self.db.add(result)

        history = GenerationHistory(
            creation_id=creation_id,
            step_no=step_no,
            version=new_version,
            payload=payload,
        )
        self.db.add(history)

        creation = self.db.get(Creation, creation_id)
        if creation:
            creation.current_step = min(max(creation.current_step, step_no + 1), MAX_STEP_NO)

        self.db.commit()
        self.db.refresh(result)

        logger.info(
            "Step 结果已保存",
            extra={
                "user_id": user_id,
                "creation_id": creation_id,
                "step_no": step_no,
                "version": new_version,
            },
        )
        return result

    def get_step_result(self, creation_id: str, step_no: int) -> StepResult | None:
        """获取某 Step 当前最新版本结果"""
        stmt = (
            select(StepResult)
            .where(StepResult.creation_id == creation_id, StepResult.step_no == step_no)
            .order_by(StepResult.version.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()
