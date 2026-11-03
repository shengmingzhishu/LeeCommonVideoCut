"""
项目路由
=======
- GET    /api/projects                列表
- POST   /api/projects                创建
- GET    /api/projects/{id}           详情
- PUT    /api/projects/{id}           更新
- DELETE /api/projects/{id}           删除
- POST   /api/projects/{id}/copy      复制
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.pagination import PageParams, page_params
from app.models.user import User
from app.schemas import (
    ApiResponse,
    PageResponse,
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=ApiResponse[PageResponse[ProjectResponse]])
def list_projects(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    pg: Annotated[PageParams, Depends(page_params)],
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
):
    """我的项目列表"""
    svc = ProjectService(db)
    items, total = svc.list(
        user.id, page=pg.page, page_size=pg.page_size, keyword=keyword, status=status
    )
    return ApiResponse(
        data=PageResponse[ProjectResponse](
            page=pg.page,
            page_size=pg.page_size,
            total=total,
            items=[ProjectResponse.model_validate(i) for i in items],
        )
    )


@router.post("", response_model=ApiResponse[ProjectResponse])
def create_project(
    req: ProjectCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """创建项目（受会员配额限制）"""
    from app.services.quota_service import ACTION_CREATE_PROJECT, check_and_raise

    check_and_raise(db, user, ACTION_CREATE_PROJECT, 1)

    svc = ProjectService(db)
    p = svc.create(user.id, req)
    return ApiResponse(data=ProjectResponse.model_validate(p))


@router.get("/{project_id}", response_model=ApiResponse[ProjectResponse])
def get_project(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """项目详情"""
    svc = ProjectService(db)
    p = svc.get(project_id)
    svc.check_ownership(p, user.id, user.is_admin)
    return ApiResponse(data=ProjectResponse.model_validate(p))


@router.put("/{project_id}", response_model=ApiResponse[ProjectResponse])
def update_project(
    project_id: str,
    req: ProjectUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """更新项目"""
    svc = ProjectService(db)
    p = svc.get(project_id)
    svc.check_ownership(p, user.id, user.is_admin)
    p = svc.update(project_id, req)
    return ApiResponse(data=ProjectResponse.model_validate(p))


@router.delete("/{project_id}", response_model=ApiResponse[None])
def delete_project(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """删除项目（含剧集/创作级联删除）"""
    svc = ProjectService(db)
    p = svc.get(project_id)
    svc.check_ownership(p, user.id, user.is_admin)
    svc.delete(project_id)
    return ApiResponse(msg="删除成功")


@router.post("/{project_id}/copy", response_model=ApiResponse[ProjectResponse])
def copy_project(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """复制项目（仅元数据，不含剧集和创作）"""
    svc = ProjectService(db)
    p = svc.get(project_id)
    svc.check_ownership(p, user.id, user.is_admin)
    new_p = svc.copy(project_id, user.id)
    return ApiResponse(data=ProjectResponse.model_validate(new_p), msg="复制成功")
