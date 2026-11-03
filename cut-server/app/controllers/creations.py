"""
创作路由（含 Step 结果查询）
===========================
- GET    /api/projects/{pid}/creations                  列表
- POST   /api/projects/{pid}/creations                  创建
- GET    /api/projects/{pid}/creations/{cid}            详情（含各 Step 结果）
- DELETE /api/projects/{pid}/creations/{cid}            删除
- GET    /api/projects/{pid}/creations/{cid}/step-results/{step_no}    单 Step 结果
- GET    /api/projects/{pid}/creations/{cid}/history/{step_no}         历史版本列表
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.episode import Episode
from app.models.user import User
from app.schemas import (
    ApiResponse,
    CreationCreateRequest,
    CreationDetailResponse,
    CreationResponse,
    StepResultResponse,
)
from app.services.creation_service import CreationService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects/{project_id}/creations", tags=["Creations"])


@router.get("", response_model=ApiResponse[list[CreationResponse]])
def list_creations(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """项目下的创作列表"""
    svc = CreationService(db)
    items = svc.list_by_project(project_id, user.id)
    return ApiResponse(data=[CreationResponse.model_validate(i) for i in items])


@router.post("", response_model=ApiResponse[CreationResponse])
def create_creation(
    project_id: str,
    req: CreationCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """创建创作（归属项目下的某个剧集）"""
    svc = CreationService(db)
    proj_svc = ProjectService(db)
    project = proj_svc.get(project_id)
    proj_svc.check_ownership(project, user.id, user.is_admin)

    episode = db.get(Episode, req.episode_id)
    if not episode:
        raise NotFoundError(f"剧集不存在: {req.episode_id}", code="EPIS_404_001")
    if episode.project_id != project_id:
        raise ValidationError("剧集不属于该项目", code="CREAT_422_001")

    creation = svc.create(episode.id, user.id, req)
    return ApiResponse(data=CreationResponse.model_validate(creation), msg="创建成功")


@router.get("/{creation_id}", response_model=ApiResponse[CreationDetailResponse])
def get_creation(
    project_id: str,
    creation_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """创作详情（含所有 Step 结果）"""
    svc = CreationService(db)
    detail = svc.get_detail(creation_id, user.id, user.is_admin)
    return ApiResponse(data=detail)


@router.delete("/{creation_id}", response_model=ApiResponse[None])
def delete_creation(
    project_id: str,
    creation_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """删除创作"""
    svc = CreationService(db)
    c = svc.get(creation_id)
    svc.check_ownership(c, user.id, user.is_admin)
    svc.delete(creation_id)
    return ApiResponse(msg="删除成功")


@router.get(
    "/{creation_id}/step-results/{step_no}",
    response_model=ApiResponse[StepResultResponse | None],
)
def get_step_result(
    project_id: str,
    creation_id: str,
    step_no: Annotated[int, Path(ge=1, le=3)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """获取某 Step 当前最新结果"""
    svc = CreationService(db)
    c = svc.get(creation_id)
    svc.check_ownership(c, user.id, user.is_admin)
    sr = svc.get_step_result(creation_id, step_no)
    if not sr:
        return ApiResponse(data=None, msg="该步骤暂无结果")
    return ApiResponse(data=StepResultResponse.model_validate(sr))


@router.get(
    "/{creation_id}/history/{step_no}",
    response_model=ApiResponse[list[StepResultResponse]],
)
def get_step_history(
    project_id: str,
    creation_id: str,
    step_no: Annotated[int, Path(ge=1, le=3)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """获取某 Step 的历史版本列表（倒序）"""
    svc = CreationService(db)
    c = svc.get(creation_id)
    svc.check_ownership(c, user.id, user.is_admin)
    history = svc.list_step_history(creation_id, step_no)
    return ApiResponse(data=[StepResultResponse.model_validate(h) for h in history])


@router.post(
    "/{creation_id}/rollback/{step_no}/{version}",
    response_model=ApiResponse[StepResultResponse],
)
def rollback_step(
    project_id: str,
    creation_id: str,
    step_no: Annotated[int, Path(ge=1, le=3)],
    version: Annotated[int, Path(ge=1)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """回滚到指定历史版本（复制为最新版本，不删除历史）"""
    svc = CreationService(db)
    c = svc.get(creation_id)
    svc.check_ownership(c, user.id, user.is_admin)
    result = svc.rollback_step(creation_id, step_no, version, user.id)
    return ApiResponse(data=StepResultResponse.model_validate(result), msg="回滚成功")
