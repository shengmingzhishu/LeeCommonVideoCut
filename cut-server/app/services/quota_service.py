"""
会员配额服务
============
- 配额维度：项目数上限 / 月度 Step 调用次数 / 存储空间
- 用量记录：usage_records 表（user_id + year_month 唯一）
- 等级：free / pro / enterprise（-1 表示无限）

对齐 .trae/rules/project/01-project-specific.md §5
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import QuotaExceededError
from app.core.logger import get_logger
from app.models.project import Project
from app.models.usage_record import UsageRecord
from app.models.user import User

logger = get_logger()

# 配额表（-1 = 无限）
QUOTA_TABLE: dict[str, dict[str, int]] = {
    "free":       {"projects": 3,   "monthly_step_calls": 50,   "storage_mb": 500},
    "pro":        {"projects": 20,  "monthly_step_calls": 500,  "storage_mb": 5000},
    "enterprise": {"projects": -1,  "monthly_step_calls": -1,   "storage_mb": -1},
}

# 动作 → 配额键
ACTION_STEP_CALL = "step_call"
ACTION_CREATE_PROJECT = "create_project"
ACTION_STORAGE = "storage"


def current_period() -> str:
    """当前计费周期（YYYY-MM，UTC）"""
    return datetime.now(timezone.utc).strftime("%Y-%m")


def get_quota(tier: str) -> dict[str, int]:
    """取等级配额（未知等级按 free 处理）"""
    return QUOTA_TABLE.get(tier, QUOTA_TABLE["free"])


def get_usage(db: Session, user_id: str) -> UsageRecord | None:
    """取本月用量记录（不存在则返回 None）"""
    stmt = select(UsageRecord).where(
        UsageRecord.user_id == user_id,
        UsageRecord.year_month == current_period(),
    )
    return db.execute(stmt).scalar_one_or_none()


def ensure_usage(db: Session, user_id: str) -> UsageRecord:
    """确保本月用量记录存在（不存在则创建）"""
    record = get_usage(db, user_id)
    if record is None:
        record = UsageRecord(
            user_id=user_id,
            year_month=current_period(),
            step_calls=0,
            storage_bytes=0,
        )
        db.add(record)
        db.flush()
    return record


def count_projects(db: Session, user_id: str) -> int:
    """统计用户当前项目数"""
    stmt = select(func.count(Project.id)).where(
        Project.user_id == user_id,
        Project.status == "active",
    )
    return db.execute(stmt).scalar() or 0


def consume_step_call(db: Session, user_id: str, count: int = 1) -> None:
    """记录一次 Step 调用消耗"""
    record = ensure_usage(db, user_id)
    record.step_calls += count
    db.flush()


def consume_storage(db: Session, user_id: str, size_bytes: int) -> None:
    """记录存储占用"""
    if size_bytes <= 0:
        return
    record = ensure_usage(db, user_id)
    record.storage_bytes += size_bytes
    db.flush()


def check_and_raise(db: Session, user: User, action: str, amount: int = 1) -> None:
    """配额检查（超额抛 QuotaExceededError）

    Args:
        db: 数据库会话
        user: 当前用户
        action: ACTION_STEP_CALL / ACTION_CREATE_PROJECT / ACTION_STORAGE
        amount: 本次消耗量（storage 为字节数）
    """
    quota = get_quota(user.membership_tier)
    tier = user.membership_tier

    if action == ACTION_STEP_CALL:
        limit = quota["monthly_step_calls"]
        if limit == -1:
            return  # 无限
        usage = get_usage(db, user.id)
        used = usage.step_calls if usage else 0
        if used + amount > limit:
            raise QuotaExceededError(
                f"本月 Step 调用次数已达上限（{limit} 次），请联系管理员升级会员",
                detail=f"tier={tier}, used={used}, limit={limit}",
            )

    elif action == ACTION_CREATE_PROJECT:
        limit = quota["projects"]
        if limit == -1:
            return
        used = count_projects(db, user.id)
        if used + amount > limit:
            raise QuotaExceededError(
                f"项目数量已达上限（{limit} 个），请联系管理员升级会员",
                detail=f"tier={tier}, used={used}, limit={limit}",
            )

    elif action == ACTION_STORAGE:
        limit_mb = quota["storage_mb"]
        if limit_mb == -1:
            return
        limit = limit_mb * 1024 * 1024
        usage = get_usage(db, user.id)
        used = usage.storage_bytes if usage else 0
        if used + amount > limit:
            used_mb = used / 1024 / 1024
            raise QuotaExceededError(
                f"存储空间已达上限（{limit_mb} MB），请清理素材或升级会员",
                detail=f"tier={tier}, used={used_mb:.1f}MB, limit={limit_mb}MB",
            )


def quota_snapshot(db: Session, user: User) -> dict[str, int | float | str]:
    """配额快照（供 /api/memberships/me/quota 返回）"""
    quota = get_quota(user.membership_tier)
    usage = get_usage(db, user.id)

    used_steps = usage.step_calls if usage else 0
    used_storage = usage.storage_bytes if usage else 0
    used_projects = count_projects(db, user.id)

    return {
        "tier": user.membership_tier,
        "projects_limit": quota["projects"],
        "projects_used": used_projects,
        "monthly_step_calls_limit": quota["monthly_step_calls"],
        "monthly_step_calls_used": used_steps,
        "storage_limit_mb": quota["storage_mb"],
        "storage_used_mb": round(used_storage / 1024 / 1024, 2),
        "current_period": current_period(),
    }
