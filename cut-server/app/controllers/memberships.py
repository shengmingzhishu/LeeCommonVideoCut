"""
会员路由
========
- GET /api/memberships/me            我的会员状态
- GET /api/memberships/me/quota      我的配额使用
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.logger import get_logger
from app.models.user import User
from app.schemas import ApiResponse, MembershipResponse, QuotaInfoResponse
from app.services.quota_service import quota_snapshot

router = APIRouter(prefix="/memberships", tags=["Memberships"])
logger = get_logger()


@router.get("/me", response_model=ApiResponse[MembershipResponse | None])
def my_membership(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """我的会员状态"""
    from app.models.membership import Membership
    from sqlalchemy import select

    stmt = (
        select(Membership)
        .where(Membership.user_id == user.id)
        .order_by(Membership.created_at.desc())
        .limit(1)
    )
    membership = db.execute(stmt).scalar_one_or_none()

    if not membership:
        # 用户还没被分配过会员记录 → 返回默认 free 状态
        return ApiResponse(
            data=MembershipResponse(
                id="",
                user_id=user.id,
                tier=user.membership_tier,
                status="active",
                started_at=user.created_at,
                expires_at=None,
                assigned_by="",
                note="默认免费用户",
                created_at=user.created_at,
            ),
            msg="默认免费会员",
        )

    return ApiResponse(data=MembershipResponse.model_validate(membership))


@router.get("/me/quota", response_model=ApiResponse[QuotaInfoResponse])
def my_quota(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """我的配额使用情况"""
    snapshot = quota_snapshot(db, user)
    return ApiResponse(data=QuotaInfoResponse(**snapshot))
