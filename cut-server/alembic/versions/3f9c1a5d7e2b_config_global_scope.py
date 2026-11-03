"""configs: 全局配置用户外键移除

全局配置以 user_id='' 作为哨兵，无法满足 users.id 外键约束，
因此在 configs.user_id 上移除外键（保留索引与复合主键）。

Revision ID: 3f9c1a5d7e2b
Revises: 27bfacfdc952
Create Date: 2026-11-03
"""
from __future__ import annotations

from alembic import op

revision: str = "3f9c1a5d7e2b"
down_revision: str | None = "27bfacfdc952"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("configs_user_id_fkey", "configs", type_="foreignkey")


def downgrade() -> None:
    op.create_foreign_key(
        "configs_user_id_fkey", "configs", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
