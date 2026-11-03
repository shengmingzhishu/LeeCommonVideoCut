"""
会员配额单元测试
================
覆盖 quota_service 的三个维度：
- 项目数上限
- 月度 Step 调用次数
- 存储空间
"""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.core.exceptions import QuotaExceededError
from app.models.project import Project
from app.models.usage_record import UsageRecord
from app.models.user import User
from app.services import quota_service as qs


@pytest.fixture
def db():
    """真实 PostgreSQL 独立测试库（JSONB 等 PG 特性需要）"""
    engine = create_engine(settings.database_url, poolclass=None)
    schema = f"test_{uuid.uuid4().hex[:8]}"

    with engine.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
        conn.commit()

    # 把 search_path 指向测试 schema
    scoped_engine = create_engine(
        settings.database_url,
        connect_args={"options": f"-csearch_path={schema}"},
    )
    Base.metadata.create_all(scoped_engine)
    Session = sessionmaker(bind=scoped_engine)

    try:
        with Session() as session:
            yield session
    finally:
        scoped_engine.dispose()
        with engine.connect() as conn:
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            conn.commit()
        engine.dispose()


def _make_user(db, tier="free", is_admin=False):
    user = User(
        id="u_test",
        username="tester",
        password_hash="x",
        is_admin=is_admin,
        membership_tier=tier,
        is_active=True,
    )
    db.add(user)
    db.commit()
    return user


class TestQuotaTable:
    """配额表定义"""

    def test_three_tiers(self):
        assert set(qs.QUOTA_TABLE) == {"free", "pro", "enterprise"}

    def test_enterprise_is_unlimited(self):
        q = qs.QUOTA_TABLE["enterprise"]
        assert q["projects"] == -1
        assert q["monthly_step_calls"] == -1
        assert q["storage_mb"] == -1

    def test_free_tier_values(self):
        q = qs.QUOTA_TABLE["free"]
        assert q["projects"] == 3
        assert q["monthly_step_calls"] == 50
        assert q["storage_mb"] == 500

    def test_pro_tier_values(self):
        q = qs.QUOTA_TABLE["pro"]
        assert q["projects"] == 20
        assert q["monthly_step_calls"] == 500
        assert q["storage_mb"] == 5000

    def test_unknown_tier_falls_back_to_free(self):
        assert qs.get_quota("nonexistent") == qs.QUOTA_TABLE["free"]


class TestStepCallQuota:
    """月度 Step 调用配额"""

    def test_under_limit_passes(self, db):
        user = _make_user(db, "free")
        qs.check_and_raise(db, user, qs.ACTION_STEP_CALL, 1)  # 不抛异常

    def test_at_limit_raises(self, db):
        user = _make_user(db, "free")
        record = qs.ensure_usage(db, user.id)
        record.step_calls = 50
        db.commit()

        with pytest.raises(QuotaExceededError) as exc:
            qs.check_and_raise(db, user, qs.ACTION_STEP_CALL, 1)
        assert exc.value.code == "MEMBER_402_001"

    def test_enterprise_unlimited(self, db):
        user = _make_user(db, "enterprise")
        record = qs.ensure_usage(db, user.id)
        record.step_calls = 99999
        db.commit()

        qs.check_and_raise(db, user, qs.ACTION_STEP_CALL, 1)  # 不抛异常

    def test_consume_increments(self, db):
        user = _make_user(db, "free")
        qs.consume_step_call(db, user.id, 1)
        qs.consume_step_call(db, user.id, 2)
        db.commit()

        record = qs.get_usage(db, user.id)
        assert record.step_calls == 3

    def test_consume_same_month_reuses_record(self, db):
        user = _make_user(db, "free")
        qs.consume_step_call(db, user.id, 1)
        db.commit()
        qs.consume_step_call(db, user.id, 1)
        db.commit()

        records = db.query(UsageRecord).filter(UsageRecord.user_id == user.id).all()
        assert len(records) == 1
        assert records[0].step_calls == 2


class TestProjectQuota:
    """项目数配额"""

    def test_under_limit_passes(self, db):
        user = _make_user(db, "free")
        qs.check_and_raise(db, user, qs.ACTION_CREATE_PROJECT, 1)

    def test_at_limit_raises(self, db):
        user = _make_user(db, "free")
        for i in range(3):
            db.add(Project(id=f"p_{i}", user_id=user.id, title="t", status="active"))
        db.commit()

        with pytest.raises(QuotaExceededError):
            qs.check_and_raise(db, user, qs.ACTION_CREATE_PROJECT, 1)

    def test_archived_not_counted(self, db):
        """归档项目不占配额"""
        user = _make_user(db, "free")
        for i in range(3):
            db.add(Project(id=f"p_{i}", user_id=user.id, title="t", status="archived"))
        db.commit()

        qs.check_and_raise(db, user, qs.ACTION_CREATE_PROJECT, 1)  # 不抛异常

    def test_enterprise_unlimited(self, db):
        user = _make_user(db, "enterprise")
        for i in range(10):
            db.add(Project(id=f"p_{i}", user_id=user.id, title="t", status="active"))
        db.commit()

        qs.check_and_raise(db, user, qs.ACTION_CREATE_PROJECT, 1)


class TestStorageQuota:
    """存储配额"""

    def test_under_limit_passes(self, db):
        user = _make_user(db, "free")
        qs.check_and_raise(db, user, qs.ACTION_STORAGE, 1024)

    def test_over_limit_raises(self, db):
        user = _make_user(db, "free")
        record = qs.ensure_usage(db, user.id)
        record.storage_bytes = 500 * 1024 * 1024  # 已满
        db.commit()

        with pytest.raises(QuotaExceededError):
            qs.check_and_raise(db, user, qs.ACTION_STORAGE, 1024)

    def test_enterprise_unlimited(self, db):
        user = _make_user(db, "enterprise")
        record = qs.ensure_usage(db, user.id)
        record.storage_bytes = 999 * 1024 * 1024 * 1024
        db.commit()

        qs.check_and_raise(db, user, qs.ACTION_STORAGE, 1024)

    def test_consume_storage(self, db):
        user = _make_user(db, "free")
        qs.consume_storage(db, user.id, 2048)
        db.commit()

        record = qs.get_usage(db, user.id)
        assert record.storage_bytes == 2048

    def test_consume_zero_is_noop(self, db):
        user = _make_user(db, "free")
        qs.consume_storage(db, user.id, 0)
        db.commit()

        assert qs.get_usage(db, user.id) is None


class TestQuotaSnapshot:
    """配额快照"""

    def test_snapshot_shape(self, db):
        user = _make_user(db, "pro")
        qs.consume_step_call(db, user.id, 5)
        db.add(Project(id="p_1", user_id=user.id, title="t", status="active"))
        db.commit()

        snap = qs.quota_snapshot(db, user)
        assert snap["tier"] == "pro"
        assert snap["monthly_step_calls_limit"] == 500
        assert snap["monthly_step_calls_used"] == 5
        assert snap["projects_used"] == 1
        assert snap["current_period"] == qs.current_period()

    def test_current_period_format(self):
        p = qs.current_period()
        assert len(p) == 7
        assert p[4] == "-"
