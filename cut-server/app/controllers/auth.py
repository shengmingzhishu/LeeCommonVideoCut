"""
认证路由
=======
- POST /api/auth/register   注册（自动登录）
- POST /api/auth/login      登录
- POST /api/auth/logout     登出（前端清 token，后端可选记录）
- POST /api/auth/change-password  改密
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.exceptions import AuthError, ValidationError
from app.core.logger import get_logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas import (
    ApiResponse,
    LoginResponse,
    UserChangePasswordRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.utils.safe_path import gen_id

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = get_logger()


@router.post("/register", response_model=ApiResponse[LoginResponse])
def register(req: UserRegisterRequest, db: Annotated[Session, Depends(get_db)]):
    """用户注册（成功后自动登录）"""
    # 检查用户名是否已存在
    stmt = select(User).where(User.username == req.username)
    if db.execute(stmt).scalar_one_or_none():
        raise ValidationError(f"用户名 {req.username} 已被占用", code="USER_409_001")

    user = User(
        id=gen_id("u"),
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        display_name=req.display_name or req.username,
        is_admin=False,
        membership_tier="free",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token, expires_at = create_access_token(
        user_id=user.id, username=user.username, membership_tier=user.membership_tier
    )
    logger.info(
        "用户注册成功",
        extra={"user_id": user.id, "username": user.username},
    )
    return ApiResponse(
        data=LoginResponse(
            user=UserResponse.model_validate(user),
            token=token,
            expires_at=expires_at,
        ),
        msg="注册成功",
    )


@router.post("/login", response_model=ApiResponse[LoginResponse])
def login(req: UserLoginRequest, db: Annotated[Session, Depends(get_db)]):
    """用户登录"""
    stmt = select(User).where(User.username == req.username)
    user = db.execute(stmt).scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise AuthError("用户名或密码错误", code="AUTH_401_005")

    if not user.is_active:
        raise AuthError("账户已被停用", code="AUTH_403_002")

    token, expires_at = create_access_token(
        user_id=user.id,
        username=user.username,
        is_admin=user.is_admin,
        membership_tier=user.membership_tier,
    )
    return ApiResponse(
        data=LoginResponse(
            user=UserResponse.model_validate(user),
            token=token,
            expires_at=expires_at,
        ),
        msg="登录成功",
    )


@router.post("/logout", response_model=ApiResponse[None])
def logout(user: Annotated[User, Depends(get_current_user)]):
    """登出（JWT 无状态，仅前端清 token）"""
    return ApiResponse(msg="登出成功")


@router.post("/change-password", response_model=ApiResponse[None])
def change_password(
    req: UserChangePasswordRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """改密（需要登录）"""
    if not verify_password(req.old_password, user.password_hash):
        raise AuthError("旧密码错误", code="AUTH_401_006")

    user.password_hash = hash_password(req.new_password)
    db.commit()
    return ApiResponse(msg="密码修改成功")
