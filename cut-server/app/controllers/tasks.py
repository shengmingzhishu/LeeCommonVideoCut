"""
异步任务路由
============
- GET    /api/tasks          我的任务列表（分页）
- GET    /api/tasks/{id}     任务详情（前端轮询）
- POST   /api/tasks/{id}/retry  重试失败/已取消任务（重新入队）
- DELETE /api/tasks/{id}     取消任务
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logger import get_logger
from app.core.pagination import PageParams, page_params
from app.models.task import Task
from app.models.user import User
from app.schemas import ApiResponse, PageResponse, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])
logger = get_logger()


@router.get("", response_model=ApiResponse[PageResponse[TaskResponse]])
def list_tasks(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    pg: Annotated[PageParams, Depends(page_params)],
    status: Annotated[str | None, Query()] = None,
):
    """我的任务列表（分页）"""
    stmt = select(Task).where(Task.user_id == user.id)
    count_stmt = select(func.count(Task.id)).where(Task.user_id == user.id)

    if status:
        stmt = stmt.where(Task.status == status)
        count_stmt = count_stmt.where(Task.status == status)

    stmt = stmt.order_by(Task.created_at.desc()).limit(pg.page_size).offset(pg.offset)

    items = list(db.execute(stmt).scalars().all())
    total = db.execute(count_stmt).scalar() or 0

    return ApiResponse(
        data=PageResponse[TaskResponse](
            page=pg.page,
            page_size=pg.page_size,
            total=total,
            items=[TaskResponse.model_validate(t) for t in items],
        )
    )


@router.get("/{task_id}", response_model=ApiResponse[TaskResponse])
def get_task(
    task_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """任务详情（前端每 2 秒轮询）"""
    task = db.get(Task, task_id)
    if not task:
        raise NotFoundError(f"任务不存在: {task_id}", code="TASK_404_001")
    if task.user_id != user.id and not user.is_admin:
        raise NotFoundError(f"任务不存在: {task_id}", code="TASK_404_001")
    return ApiResponse(data=TaskResponse.model_validate(task))


@router.post("/{task_id}/retry", response_model=ApiResponse[TaskResponse])
def retry_task(
    task_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """重试失败 / 已取消任务：沿用原 type 与 payload 重新入队，返回新任务"""
    from app.tasks.task_queue import STATUS_CANCELLED, STATUS_FAILED, task_queue

    task = db.get(Task, task_id)
    if not task:
        raise NotFoundError(f"任务不存在: {task_id}", code="TASK_404_001")
    if task.user_id != user.id and not user.is_admin:
        raise NotFoundError(f"任务不存在: {task_id}", code="TASK_404_001")
    if task.status not in (STATUS_FAILED, STATUS_CANCELLED):
        raise ValidationError("只有失败或已取消的任务可以重试", code="TASK_422_001")

    try:
        new_task_id = task_queue.submit(
            task_type=task.type,
            user_id=task.user_id,
            payload=task.payload or {},
        )
    except ValueError as e:
        raise ValidationError(str(e), code="TASK_422_002") from e

    db.expire_all()
    new_task = db.get(Task, new_task_id)
    return ApiResponse(
        data=TaskResponse.model_validate(new_task), msg=f"已重新提交（原任务 {task_id}）"
    )


@router.delete("/{task_id}", response_model=ApiResponse[None])
def cancel_task(
    task_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """取消任务"""
    from app.tasks.task_queue import task_queue

    task = db.get(Task, task_id)
    if not task:
        raise NotFoundError(f"任务不存在: {task_id}", code="TASK_404_001")
    if task.user_id != user.id and not user.is_admin:
        raise NotFoundError(f"任务不存在: {task_id}", code="TASK_404_001")

    task_queue.cancel(task_id)
    return ApiResponse(msg="任务已取消")
