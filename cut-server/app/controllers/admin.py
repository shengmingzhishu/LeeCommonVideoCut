"""
管理员路由
==========
- GET    /api/admin/users                  用户列表（分页 + 搜索 + 筛选）
- GET    /api/admin/users/{user_id}        用户详情
- PUT    /api/admin/users/{user_id}        修改用户（角色/状态/等级）
- POST   /api/admin/users/{user_id}/password  重置密码
- GET    /api/admin/memberships            会员列表
- POST   /api/admin/memberships            分配/续期会员
- DELETE /api/admin/memberships/{id}       停用会员
- GET    /api/admin/audit-logs             操作审计日志

所有接口仅 is_admin=true 可访问，所有写操作记录 audit_logs。
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.deps import get_admin_user, get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logger import get_logger
from app.core.pagination import PageParams, page_params
from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.config import GLOBAL_SCOPE
from app.models.membership import Membership
from app.models.user import User
from app.schemas import (
    AdminResetPasswordRequest,
    AdminUserUpdateRequest,
    ApiResponse,
    ConfigResponse,
    ConfigUpdateRequest,
    MembershipAssignRequest,
    MembershipResponse,
    PageResponse,
    UserResponse,
)
from app.services.config_service import ConfigService
from app.utils.safe_path import gen_id

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = get_logger()


def _audit(
    db: Session,
    admin: User,
    action: str,
    target_type: str,
    target_id: str,
    payload: dict[str, Any] | None = None,
) -> None:
    """写操作审计日志"""
    db.add(
        AuditLog(
            admin_user_id=admin.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            payload=payload or {},
        )
    )


# ============================================================
# 用户管理
# ============================================================
@router.get("/users", response_model=ApiResponse[PageResponse[UserResponse]])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
    pg: Annotated[PageParams, Depends(page_params)],
    keyword: str | None = Query(default=None),
    tier: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
):
    """用户列表"""
    stmt = select(User)
    count_stmt = select(func.count(User.id))

    conditions = []
    if keyword:
        kw = f"%{keyword}%"
        cond = or_(User.username.ilike(kw), User.email.ilike(kw))
        conditions.append(cond)
    if tier:
        conditions.append(User.membership_tier == tier)
    if is_active is not None:
        conditions.append(User.is_active == is_active)

    if conditions:
        stmt = stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    stmt = stmt.order_by(User.created_at.desc()).limit(pg.page_size).offset(pg.offset)
    items = db.execute(stmt).scalars().all()
    total = db.execute(count_stmt).scalar() or 0

    return ApiResponse(
        data=PageResponse[UserResponse](
            page=pg.page,
            page_size=pg.page_size,
            total=total,
            items=[UserResponse.model_validate(u) for u in items],
        )
    )


@router.get("/users/{user_id}", response_model=ApiResponse[UserResponse])
def get_user(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
):
    """用户详情"""
    user = db.get(User, user_id)
    if not user:
        raise NotFoundError(f"用户不存在: {user_id}", code="USER_404_001")
    return ApiResponse(data=UserResponse.model_validate(user))


@router.put("/users/{user_id}", response_model=ApiResponse[UserResponse])
def update_user(
    user_id: str,
    req: AdminUserUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
):
    """修改用户（角色 / 状态 / 会员等级）"""
    user = db.get(User, user_id)
    if not user:
        raise NotFoundError(f"用户不存在: {user_id}", code="USER_404_001")

    # 保护：不能把自己降级或停用
    if user.id == admin.id and (req.is_admin is False or req.is_active is False):
        raise ValidationError("不能修改自己的管理员权限或停用自己", code="ADMIN_400_001")

    data = req.model_dump(exclude_unset=True)
    changes: dict[str, Any] = {}
    for k, v in data.items():
        if getattr(user, k) != v:
            changes[k] = {"from": getattr(user, k), "to": v}
            setattr(user, k, v)

    if changes:
        _audit(db, admin, "user.update", "user", user_id, changes)
        db.commit()
        db.refresh(user)

    return ApiResponse(data=UserResponse.model_validate(user), msg="修改成功")


@router.put("/users/{user_id}/status", response_model=ApiResponse[UserResponse])
def set_user_status(
    user_id: str,
    req: AdminUserUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
):
    """管理员 - 启用/停用用户（契约路径）"""
    if req.is_active is None:
        raise ValidationError("缺少 is_active", code="ADMIN_400_002")
    return update_user(user_id, req, db, admin)


@router.post("/users/{user_id}/password", response_model=ApiResponse[None])
def reset_password(
    user_id: str,
    req: AdminResetPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
):
    """重置用户密码"""
    user = db.get(User, user_id)
    if not user:
        raise NotFoundError(f"用户不存在: {user_id}", code="USER_404_001")

    user.password_hash = hash_password(req.new_password)
    _audit(db, admin, "user.reset_password", "user", user_id)
    db.commit()
    return ApiResponse(msg="密码已重置")


# ============================================================
# 会员分配
# ============================================================
@router.get("/memberships", response_model=ApiResponse[list[MembershipResponse]])
def list_memberships(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
    tier: str | None = Query(default=None),
    status: str | None = Query(default=None),
):
    """会员列表"""
    stmt = select(Membership)
    if tier:
        stmt = stmt.where(Membership.tier == tier)
    if status:
        stmt = stmt.where(Membership.status == status)
    stmt = stmt.order_by(Membership.created_at.desc())

    items = db.execute(stmt).scalars().all()
    return ApiResponse(data=[MembershipResponse.model_validate(m) for m in items])


@router.post("/memberships", response_model=ApiResponse[MembershipResponse])
def assign_membership(
    req: MembershipAssignRequest,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
):
    """分配 / 续期会员"""
    user = db.get(User, req.user_id)
    if not user:
        raise NotFoundError(f"用户不存在: {req.user_id}", code="USER_404_001")

    # 停用该用户旧的 active 会员
    old_stmt = select(Membership).where(
        Membership.user_id == req.user_id,
        Membership.status == "active",
    )
    for old in db.execute(old_stmt).scalars().all():
        old.status = "cancelled"

    membership = Membership(
        id=gen_id("ms"),
        user_id=req.user_id,
        tier=req.tier,
        status="active",
        started_at=datetime.now(timezone.utc),
        expires_at=req.expires_at,
        assigned_by=admin.id,
        note=req.note,
    )
    db.add(membership)

    # 同步用户表的等级字段（方便鉴权时快速判断）
    user.membership_tier = req.tier

    _audit(
        db, admin, "membership.assign", "membership", membership.id,
        {"user_id": req.user_id, "tier": req.tier, "expires_at": str(req.expires_at)},
    )
    db.commit()
    db.refresh(membership)

    return ApiResponse(data=MembershipResponse.model_validate(membership), msg="会员已分配")


@router.delete("/memberships/{membership_id}", response_model=ApiResponse[None])
def cancel_membership(
    membership_id: str,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
):
    """停用会员（降级为 free）"""
    membership = db.get(Membership, membership_id)
    if not membership:
        raise NotFoundError(f"会员记录不存在: {membership_id}", code="MEMBER_404_001")

    membership.status = "cancelled"

    user = db.get(User, membership.user_id)
    if user:
        user.membership_tier = "free"

    _audit(db, admin, "membership.cancel", "membership", membership_id,
           {"user_id": membership.user_id})
    db.commit()
    return ApiResponse(msg="会员已停用")


# ============================================================
# 全局配置
# ============================================================
@router.get("/configs", response_model=ApiResponse[list[ConfigResponse]])
def list_global_configs(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
):
    """管理员 - 全局配置列表"""
    return ApiResponse(data=ConfigService(db).list_global())


@router.put("/configs", response_model=ApiResponse[ConfigResponse])
def set_global_config(
    req: ConfigUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
):
    """管理员 - 设置全局配置"""
    svc = ConfigService(db)
    result = svc.set_config(req.key, req.value, req.description, user_id=GLOBAL_SCOPE)
    _audit(db, admin, "config.set_global", "config", req.key,
           {"fields": sorted(req.value.keys())})
    db.commit()
    return ApiResponse(data=result, msg="全局配置已保存")


# ============================================================
# 审计日志
# ============================================================
@router.get("/audit-logs", response_model=ApiResponse[PageResponse[dict[str, Any]]])
def list_audit_logs(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin_user)],
    pg: Annotated[PageParams, Depends(page_params)],
    action: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
):
    """操作审计日志"""
    stmt = select(AuditLog)
    count_stmt = select(func.count(AuditLog.id))

    conditions = []
    if action:
        conditions.append(AuditLog.action == action)
    if target_type:
        conditions.append(AuditLog.target_type == target_type)
    if conditions:
        stmt = stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(pg.page_size).offset(pg.offset)
    items = db.execute(stmt).scalars().all()
    total = db.execute(count_stmt).scalar() or 0

    return ApiResponse(
        data=PageResponse[dict[str, Any]](
            page=pg.page,
            page_size=pg.page_size,
            total=total,
            items=[
                {
                    "id": log.id,
                    "admin_user_id": log.admin_user_id,
                    "action": log.action,
                    "target_type": log.target_type,
                    "target_id": log.target_id,
                    "payload": log.payload,
                    "created_at": log.created_at.isoformat(),
                }
                for log in items
            ],
        )
    )
