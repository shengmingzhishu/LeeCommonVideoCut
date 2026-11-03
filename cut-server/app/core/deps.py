"""
依赖注入
========
- get_db：数据库 Session
- get_current_user：解析 JWT，注入当前用户
- get_admin_user：仅管理员
- check_quota：会员配额检查（Step 调用前）
"""
from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AdminOnlyError, AuthError, ForbiddenError, QuotaExceededError
from app.core.security import decode_access_token
from app.models.user import User  # 延迟引用避免循环


def _extract_token(authorization: str | None) -> str:
    if not authorization:
        raise AuthError("未登录，请先登录")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError("Authorization 头格式错误")
    return parts[1]


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """注入当前用户（任何需要登录的接口用）"""
    token = _extract_token(authorization)
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError as e:
        raise AuthError("登录已过期，请重新登录", code="AUTH_401_002") from e
    except jwt.InvalidTokenError as e:
        raise AuthError("Token 无效", code="AUTH_401_003") from e

    user_id = payload.get("sub")
    if not user_id:
        raise AuthError("Token 缺少 sub 字段")

    user = db.get(User, user_id)
    if not user:
        raise AuthError("用户不存在", code="AUTH_401_004")
    if not user.is_active:
        raise ForbiddenError("账户已被停用", code="AUTH_403_002")

    return user


def get_admin_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """注入当前管理员（仅管理员接口用）"""
    if not user.is_admin:
        raise AdminOnlyError()
    return user


# 会员配额表（与 .trae/rules/project/01-project-specific.md §5 对齐）
# 实际实现见 app/services/quota_service.py
from app.services.quota_service import (  # noqa: E402
    ACTION_CREATE_PROJECT,
    ACTION_STEP_CALL,
    QUOTA_TABLE,
    check_and_raise,
)


def check_quota(action: str = ACTION_STEP_CALL, amount: int = 1):
    """FastAPI Depends 工厂：检查会员配额

    Usage:
        @router.post("/api/step1/save", dependencies=[Depends(check_quota(ACTION_STEP_CALL))])

    超额抛 QuotaExceededError（HTTP 402 + MEMBER_402_001）
    """
    from app.core.database import get_db

    def _checker(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        check_and_raise(db, user, action, amount)
        return user

    return _checker
