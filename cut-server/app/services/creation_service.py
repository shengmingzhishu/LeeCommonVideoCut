"""
创作服务（含 Step 结果读写）
"""
from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.creation import Creation
from app.models.episode import Episode
from app.models.step_result import StepResult
from app.schemas import (
    CreationCreateRequest,
    CreationDetailResponse,
    CreationResponse,
    StepResultResponse,
)
from app.utils.safe_path import gen_id


class CreationService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, episode_id: str, user_id: str, req: CreationCreateRequest) -> Creation:
        ep = self.db.get(Episode, episode_id)
        if not ep:
            raise NotFoundError(f"剧集不存在: {episode_id}", code="EPIS_404_001")

        creation = Creation(
            id=gen_id("c"),
            episode_id=episode_id,
            user_id=user_id,
            title=req.title,
            current_step=1,
            status="active",
        )
        self.db.add(creation)
        self.db.commit()
        self.db.refresh(creation)
        return creation

    def get(self, creation_id: str) -> Creation:
        c = self.db.get(Creation, creation_id)
        if not c:
            raise NotFoundError(f"创作不存在: {creation_id}", code="CREAT_404_001")
        return c

    def list_by_project(self, project_id: str, user_id: str) -> Sequence[Creation]:
        """通过 episode.project_id 过滤"""
        stmt = (
            select(Creation)
            .join(Episode, Creation.episode_id == Episode.id)
            .where(Episode.project_id == project_id, Creation.user_id == user_id)
            .order_by(Creation.created_at.desc())
        )
        return self.db.execute(stmt).scalars().all()

    def delete(self, creation_id: str) -> None:
        c = self.get(creation_id)
        self.db.delete(c)
        self.db.commit()

    def get_detail(self, creation_id: str, user_id: str, is_admin: bool) -> CreationDetailResponse:
        """创作详情（含所有 step_results）"""
        c = self.get(creation_id)
        if not is_admin and c.user_id != user_id:
            raise ForbiddenError("无权访问该创作", code="CREAT_403_001")

        stmt = select(StepResult).where(StepResult.creation_id == creation_id)
        results = self.db.execute(stmt).scalars().all()

        # 取每个 step_no 的最新 version
        latest: dict[int, StepResult] = {}
        for r in results:
            if r.step_no not in latest or r.version > latest[r.step_no].version:
                latest[r.step_no] = r

        step_results_dict = {
            sr.step_no: StepResultResponse.model_validate(sr) for sr in latest.values()
        }

        return CreationDetailResponse(
            **CreationResponse.model_validate(c).model_dump(),
            step_results=step_results_dict,
        )

    def get_step_result(self, creation_id: str, step_no: int) -> StepResult | None:
        """获取某 step 当前最新结果"""
        stmt = (
            select(StepResult)
            .where(StepResult.creation_id == creation_id, StepResult.step_no == step_no)
            .order_by(StepResult.version.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def rollback_step(
        self, creation_id: str, step_no: int, version: int, user_id: str
    ) -> StepResult:
        """把某个历史版本的内容复制为新版本（不删除历史）

        Args:
            creation_id: 创作 ID
            step_no: 步骤号（1~3）
            version: 要回滚到的历史版本号
            user_id: 操作用户 ID（写日志）

        Raises:
            NotFoundError: 历史版本不存在
        """
        from app.services.step_service import StepService

        stmt = select(StepResult).where(
            StepResult.creation_id == creation_id,
            StepResult.step_no == step_no,
            StepResult.version == version,
        )
        src = self.db.execute(stmt).scalar_one_or_none()
        if not src:
            raise NotFoundError(
                f"历史版本不存在: step={step_no} version={version}",
                code="CREAT_404_002",
            )
        return StepService(self.db).save_step_result(
            creation_id=creation_id,
            step_no=step_no,
            payload=src.payload,
            user_id=user_id,
        )

    def list_step_history(self, creation_id: str, step_no: int) -> Sequence[StepResult]:
        """某 step 的历史版本（倒序）"""
        stmt = (
            select(StepResult)
            .where(StepResult.creation_id == creation_id, StepResult.step_no == step_no)
            .order_by(StepResult.version.desc())
        )
        return self.db.execute(stmt).scalars().all()

    def check_ownership(self, c: Creation, user_id: str, is_admin: bool) -> None:
        if is_admin:
            return
        if c.user_id != user_id:
            raise ForbiddenError("无权访问该创作", code="CREAT_403_001")
