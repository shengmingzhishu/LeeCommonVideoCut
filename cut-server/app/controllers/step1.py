"""
Step1 路由：创作信息
====================
- POST /api/step1/outline  生成大纲（AI，不落库）
- POST /api/step1/save     保存创作信息与大纲
- GET  /api/step1/load     读取已保存的创作信息与大纲
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.logger import get_logger
from app.models.creation import Creation
from app.models.user import User
from app.schemas import (
    ApiResponse,
    Step1OutlineRequest,
    Step1OutlineResponse,
    Step1SaveRequest,
    Step1SaveResponse,
)
from app.services.creation_service import CreationService
from app.services.step1_service import Step1Service

router = APIRouter(prefix="/step1", tags=["Step1"])
logger = get_logger()


def _load_creation(db: Session, creation_id: str, user: User) -> Creation:
    """加载创作并校验所有权"""
    svc = CreationService(db)
    creation = svc.get(creation_id)
    svc.check_ownership(creation, user.id, user.is_admin)
    return creation


@router.post("/outline", response_model=ApiResponse[Step1OutlineResponse])
def generate_outline(
    req: Step1OutlineRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """生成大纲

    流程：
    1. 校验创作归属
    2. 组装关联资料上下文
    3. 调用 AI 生成大纲（不落库，前端可反复重新生成）
    """
    from app.services.quota_service import ACTION_STEP_CALL, check_and_raise, consume_step_call

    creation = _load_creation(db, req.creation_id, user)
    check_and_raise(db, user, ACTION_STEP_CALL, 1)

    svc = Step1Service(db)
    outline = svc.generate_outline(creation=creation, form=req.form)

    consume_step_call(db, user.id, 1)
    db.commit()

    return ApiResponse(data=Step1OutlineResponse(outline=outline))


@router.post("/save", response_model=ApiResponse[Step1SaveResponse])
def save_step1(
    req: Step1SaveRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """保存创作信息与大纲"""
    creation = _load_creation(db, req.creation_id, user)
    result = Step1Service(db).save(creation=creation, form=req.form, outline=req.outline)
    return ApiResponse(data=result, msg="保存成功")


@router.get("/load", response_model=ApiResponse[Step1SaveResponse])
def load_step1(
    creation_id: Annotated[str, Query()],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """读取已保存的创作信息与大纲"""
    creation = _load_creation(db, creation_id, user)
    result = Step1Service(db).load(creation)
    return ApiResponse(data=result)
