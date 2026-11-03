"""
剧集服务
"""
from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.episode import Episode
from app.models.project import Project
from app.schemas import EpisodeCreateRequest, EpisodeUpdateRequest
from app.utils.safe_path import gen_id


class EpisodeService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project_id: str, user_id: str, req: EpisodeCreateRequest) -> Episode:
        # 校验项目归属
        project = self.db.get(Project, project_id)
        if not project:
            raise NotFoundError(f"项目不存在: {project_id}", code="PROJ_404_001")

        ep = Episode(
            id=gen_id("e"),
            project_id=project_id,
            user_id=user_id,
            title=req.title,
            description=req.description,
            status="active",
        )
        self.db.add(ep)
        self.db.commit()
        self.db.refresh(ep)
        return ep

    def get(self, episode_id: str) -> Episode:
        ep = self.db.get(Episode, episode_id)
        if not ep:
            raise NotFoundError(f"剧集不存在: {episode_id}", code="EPIS_404_001")
        return ep

    def list_by_project(self, project_id: str, user_id: str) -> Sequence[Episode]:
        stmt = (
            select(Episode)
            .where(Episode.project_id == project_id, Episode.user_id == user_id)
            .order_by(Episode.created_at.desc())
        )
        return self.db.execute(stmt).scalars().all()

    def update(self, episode_id: str, req: EpisodeUpdateRequest) -> Episode:
        ep = self.get(episode_id)
        data = req.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(ep, k, v)
        self.db.commit()
        self.db.refresh(ep)
        return ep

    def delete(self, episode_id: str) -> None:
        ep = self.get(episode_id)
        self.db.delete(ep)
        self.db.commit()

    def check_ownership(self, ep: Episode, user_id: str, is_admin: bool) -> None:
        if is_admin:
            return
        if ep.user_id != user_id:
            raise ForbiddenError("无权访问该剧集", code="EPIS_403_001")
