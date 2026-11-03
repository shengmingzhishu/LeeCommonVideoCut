"""
JWT + 密码哈希
==============
- 密码用 bcrypt（直接用 bcrypt 库，避开 passlib 的版本不兼容问题）
- JWT HS256，30 天有效
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def _truncate_password(plain: str) -> bytes:
    """bcrypt 限制 72 字节，超长密码需手动截断"""
    return plain.encode("utf-8")[:72]


def hash_password(plain: str) -> str:
    """bcrypt 哈希密码（默认 cost=12）"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(_truncate_password(plain), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验密码"""
    try:
        return bcrypt.checkpw(_truncate_password(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    *,
    user_id: str,
    username: str,
    is_admin: bool = False,
    membership_tier: str = "free",
) -> tuple[str, datetime]:
    """生成 JWT，返回 (token, expires_at)"""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=settings.jwt_expire_days)

    payload = {
        "sub": user_id,
        "username": username,
        "is_admin": is_admin,
        "membership_tier": membership_tier,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "jti": uuid.uuid4().hex,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires


def decode_access_token(token: str) -> dict:
    """解码 JWT"""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
