"""
配置表
======
设计要点：
- 全局配置：user_id = ''（空字符串，代替 NULL，因为 user_id 是复合主键的一部分）
- 用户级配置：user_id = <用户 id>
- 用哨兵值 '' 代替 NULL，避免 PostgreSQL 复合主键中 NULL 的语义问题
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# 全局配置的哨兵 user_id
GLOBAL_SCOPE = ""


class Config(Base):
    __tablename__ = "configs"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    # 全局配置用 '' 表示（复合主键不允许 NULL，因此不能加 users 外键）
    user_id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=GLOBAL_SCOPE
    )
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (Index("ix_configs_user_id", "user_id"),)

    @staticmethod
    def is_global(user_id: str | None) -> bool:
        """判断是否全局配置"""
        return not user_id
