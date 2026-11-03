"""
Step2 路由：口播长文
====================
- POST /api/step2/generate  生成口播长文（AI，不落库）
- POST /api/step2/save     保存长文（可触发异步 TTS）
- GET  /api/step2/load     读取已保存的长文
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
    Step2GenerateRequest,
    Step2GenerateResponse,
    Step2SaveRequest,
    Step2SaveResponse,
)
from app.services.creation_service import CreationService
from app.services.step2_service import Step2Service

router = APIRouter(prefix="/step2", tags=["Step2"])
logger = get_logger()


def _load_creation(db: Session, creation_id: str, user: User) -> Creation:
    """加载创作并校验所有权"""
    svc = CreationService(db)
    creation = svc.get(creation_id)
    svc.check_ownership(creation, user.id, user.is_admin)
    return creation


@router.post("/generate", response_model=ApiResponse[Step2GenerateResponse])
def generate_long_article(
    req: Step2GenerateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """生成口播长文

    基于 Step1 已保存的表单与大纲生成纯文本长文，不落库，前端可反复重新生成。
    受会员配额限制。
    """
    from app.services.quota_service import ACTION_STEP_CALL, check_and_raise, consume_step_call

    creation = _load_creation(db, req.creation_id, user)
    check_and_raise(db, user, ACTION_STEP_CALL, 1)

    result = Step2Service(db).generate(
        creation=creation,
        title=req.title,
        subtitle=req.subtitle,
    )

    consume_step_call(db, user.id, 1)
    db.commit()

    return ApiResponse(data=result)


@router.post("/save", response_model=ApiResponse[Step2SaveResponse])
def save_long_article(
    req: Step2SaveRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """保存口播长文

    skip_tts=false 时提交异步 TTS 任务，返回 tts_task_id 供前端轮询。
    """
    creation = _load_creation(db, req.creation_id, user)
    result = Step2Service(db).save(
        creation=creation,
        title=req.title,
        content=req.content,
        word_count=req.word_count,
        skip_tts=req.skip_tts,
        tts_config=req.tts_config,
    )
    return ApiResponse(data=result, msg="保存成功")


@router.get("/load", response_model=ApiResponse[Step2GenerateResponse | None])
def load_long_article(
    creation_id: Annotated[str, Query()],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """读取已保存的口播长文"""
    creation = _load_creation(db, creation_id, user)
    result = Step2Service(db).load(creation)
    return ApiResponse(data=result)
