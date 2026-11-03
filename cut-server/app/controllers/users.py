"""
用户路由
=======
- GET  /api/users/me         获取当前用户
- PUT  /api/users/me         更新资料
- GET  /api/users/me/projects 我的项目列表（简化为引用 projects）
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
    ProjectResponse,
    UserResponse,
    UserUpdateRequest,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ApiResponse[UserResponse])
def get_me(user: Annotated[User, Depends(get_current_user)]):
    return ApiResponse(data=UserResponse.model_validate(user))


@router.put("/me", response_model=ApiResponse[UserResponse])
def update_me(
    req: UserUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    data = req.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return ApiResponse(data=UserResponse.model_validate(user))


@router.get("/me/projects", response_model=ApiResponse[PageResponse[ProjectResponse]])
def my_projects(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    pg: Annotated[PageParams, Depends(page_params)],
    keyword: str | None = Query(default=None),
):
    """我的项目列表（与 GET /projects 等价，保留契约路径）"""
    svc = ProjectService(db)
    items, total = svc.list(
        user.id, page=pg.page, page_size=pg.page_size, keyword=keyword
    )
    return ApiResponse(
        data=PageResponse[ProjectResponse](
            page=pg.page,
            page_size=pg.page_size,
            total=total,
            items=[ProjectResponse.model_validate(i) for i in items],
        )
    )
