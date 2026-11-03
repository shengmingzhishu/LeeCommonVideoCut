"""
剧集路由
=======
- GET    /api/projects/{pid}/episodes        列表
- POST   /api/projects/{pid}/episodes        创建
- GET    /api/projects/{pid}/episodes/{eid}  详情
- PUT    /api/projects/{pid}/episodes/{eid}  更新
- DELETE /api/projects/{pid}/episodes/{eid}  删除
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas import (
    ApiResponse,
    EpisodeCreateRequest,
    EpisodeResponse,
    EpisodeUpdateRequest,
)
from app.services.episode_service import EpisodeService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects/{project_id}/episodes", tags=["Episodes"])


def _check_project_owner(db: Session, project_id: str, user: User) -> None:
    proj_svc = ProjectService(db)
    proj = proj_svc.get(project_id)
    proj_svc.check_ownership(proj, user.id, user.is_admin)


@router.get("", response_model=ApiResponse[list[EpisodeResponse]])
def list_episodes(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """项目下的剧集列表"""
    _check_project_owner(db, project_id, user)
    svc = EpisodeService(db)
    items = svc.list_by_project(project_id, user.id)
    return ApiResponse(data=[EpisodeResponse.model_validate(i) for i in items])


@router.post("", response_model=ApiResponse[EpisodeResponse])
def create_episode(
    project_id: str,
    req: EpisodeCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """创建剧集"""
    _check_project_owner(db, project_id, user)
    svc = EpisodeService(db)
    ep = svc.create(project_id, user.id, req)
    return ApiResponse(data=EpisodeResponse.model_validate(ep))


@router.get("/{episode_id}", response_model=ApiResponse[EpisodeResponse])
def get_episode(
    project_id: str,
    episode_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """剧集详情"""
    svc = EpisodeService(db)
    ep = svc.get(episode_id)
    svc.check_ownership(ep, user.id, user.is_admin)
    return ApiResponse(data=EpisodeResponse.model_validate(ep))


@router.put("/{episode_id}", response_model=ApiResponse[EpisodeResponse])
def update_episode(
    project_id: str,
    episode_id: str,
    req: EpisodeUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """更新剧集"""
    svc = EpisodeService(db)
    ep = svc.get(episode_id)
    svc.check_ownership(ep, user.id, user.is_admin)
    ep = svc.update(episode_id, req)
    return ApiResponse(data=EpisodeResponse.model_validate(ep))


@router.delete("/{episode_id}", response_model=ApiResponse[None])
def delete_episode(
    project_id: str,
    episode_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """删除剧集（含创作级联删除）"""
    svc = EpisodeService(db)
    ep = svc.get(episode_id)
    svc.check_ownership(ep, user.id, user.is_admin)
    svc.delete(episode_id)
    return ApiResponse(msg="删除成功")
