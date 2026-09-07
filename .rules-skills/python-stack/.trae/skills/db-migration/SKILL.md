---
name: db-migration
version: 1.0.0
description: 数据库迁移管理。Alembic 迁移脚本生成、数据迁移、回滚策略、零停机迁移。涉及表结构变更、字段增删改时使用。
---

# 数据库迁移技能

## 定位

管理 SQLAlchemy + MySQL 的数据库 schema 变更全生命周期，确保迁移可追溯、可回滚、可安全执行。

## 核心能力

### 1. Alembic 迁移脚本生成

```bash
# 初始化 Alembic（首次）
alembic init alembic

# 生成自动迁移（从模型差异）
alembic revision --autogenerate -m "add_eval_case_table"

# 手动编写迁移
alembic revision -m "add_index_to_eval_result"
```

### 2. 迁移脚本规范

```python
"""add eval_case table

Revision ID: a1b2c3d4e5f6
Revises: previous_revision_id
Create Date: 2026-09-07
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'eval_cases',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('direction', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    # 数据迁移（如有）
    op.execute("UPDATE eval_cases SET direction = 'text_qa' WHERE direction IS NULL")

def downgrade():
    op.drop_table('eval_cases')
```

### 3. 迁移命名规范

| 类型 | 前缀 | 示例 |
|------|------|------|
| 新增表 | `add_table_` | `add_table_eval_cases` |
| 删除表 | `drop_table_` | `drop_table_old_logs` |
| 新增字段 | `add_column_` | `add_column_eval_status` |
| 删除字段 | `drop_column_` | `drop_column_legacy_field` |
| 修改字段 | `alter_column_` | `alter_column_eval_title_length` |
| 新增索引 | `add_index_` | `add_index_eval_result_suite_id` |
| 数据迁移 | `data_` | `data_migrate_eval_direction_enum` |

### 4. 迁移执行流程

```bash
# 1. 生成迁移脚本
alembic revision --autogenerate -m "add_eval_case_table"

# 2. 检查生成的脚本（手动审查 upgrade() 和 downgrade()）

# 3. 在开发环境执行
alembic upgrade head

# 4. 验证表结构
alembic current
alembic history

# 5. 回滚测试
alembic downgrade -1

# 6. 重新升级
alembic upgrade head
```

### 5. 零停机迁移策略

**安全规则**：
- 新增字段必须设为 nullable 或有 default 值
- 删除字段分两步：先标记 deprecated → 下个版本删除
- 修改字段类型分两步：先新增新字段+双写 → 数据迁移 → 删除旧字段
- 新增索引使用 `CREATE INDEX CONCURRENTLY`（MySQL 用 `ALGORITHM=INPLACE`）

```python
# 零停机新增字段示例
def upgrade():
    # Step 1: 新增 nullable 字段
    op.add_column('eval_suites', sa.Column('status', sa.String(20), nullable=True))

    # Step 2: 回填数据
    op.execute("UPDATE eval_suites SET status = 'draft' WHERE status IS NULL")

    # Step 3: 设置非空约束
    op.alter_column('eval_suites', 'status', nullable=False)
```

### 6. 回滚策略

```bash
# 回滚到上一版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade a1b2c3d4e5f6

# 回滚到初始状态
alembic downgrade base

# 查看当前版本
alembic current
```

## 使用时机

- 新增数据库表
- 新增/删除/修改字段
- 新增/删除索引
- 数据迁移
- 架构重构涉及数据库
