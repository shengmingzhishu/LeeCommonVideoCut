"""
文件服务单元测试
================
重点覆盖安全边界：
- 路径遍历防护（跨用户访问）
- 扩展名白名单
- 大小限制
- 用户隔离
- Range 解析
- 文件名清理
"""
from __future__ import annotations

import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    QuotaExceededError,
    ValidationError,
)
from app.models.user import User
from app.services.file_service import FileService
from app.utils.file_types import (
    guess_mime,
    is_ext_allowed,
    sanitize_filename,
    unique_path,
)


@pytest.fixture
def db():
    """真实 PostgreSQL 独立 schema"""
    engine = create_engine(settings.database_url, poolclass=None)
    schema = f"test_{uuid.uuid4().hex[:8]}"

    with engine.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
        conn.commit()

    scoped = create_engine(
        settings.database_url,
        connect_args={"options": f"-csearch_path={schema}"},
    )
    Base.metadata.create_all(scoped)
    Session = sessionmaker(bind=scoped)

    try:
        with Session() as session:
            yield session
    finally:
        scoped.dispose()
        with engine.connect() as conn:
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            conn.commit()
        engine.dispose()


@pytest.fixture
def user(db):
    u = User(
        id="u_file_test",
        username="filetester",
        password_hash="x",
        is_admin=False,
        membership_tier="enterprise",  # 避免配额干扰安全测试
        is_active=True,
    )
    db.add(u)
    db.commit()
    return u


@pytest.fixture
def other_user(db):
    u = User(
        id="u_other",
        username="othertester",
        password_hash="x",
        is_admin=False,
        membership_tier="enterprise",
        is_active=True,
    )
    db.add(u)
    db.commit()
    return u


@pytest.fixture
def svc(db, tmp_path):
    """每个测试独立的文件服务（隔离上传目录，避免测试间干扰）"""
    return FileService(db, upload_root=tmp_path / "uploads")


class TestFilenameSanitize:
    """文件名清理"""

    def test_strips_path_components(self):
        assert sanitize_filename("../../etc/passwd") == "passwd"
        assert sanitize_filename(r"C:\Windows\System32\cmd.exe") == "cmd.exe"

    def test_replaces_illegal_chars(self):
        result = sanitize_filename('a<b>c:d"e|f?g*h.mp4')
        assert "<" not in result
        assert ":" not in result
        assert result.endswith(".mp4")

    def test_empty_falls_back(self):
        assert sanitize_filename("") == "upload"
        assert sanitize_filename("...") == "upload"

    def test_length_limit(self):
        result = sanitize_filename("a" * 300 + ".mp4")
        assert len(result) <= 96

    def test_keeps_extension_on_truncate(self):
        result = sanitize_filename("a" * 300 + ".mp4")
        assert result.endswith(".mp4")


class TestUniquePath:
    """唯一路径生成"""

    def test_first_is_original(self, tmp_path):
        assert unique_path(tmp_path, "a.txt") == tmp_path / "a.txt"

    def test_increments_on_conflict(self, tmp_path):
        (tmp_path / "a.txt").write_text("x")
        assert unique_path(tmp_path, "a.txt") == tmp_path / "a (1).txt"

    def test_keeps_double_extension(self, tmp_path):
        (tmp_path / "a.tar.gz").write_text("x")
        assert unique_path(tmp_path, "a.tar.gz") == tmp_path / "a.tar (1).gz"


class TestMimeAndExt:
    """MIME 推断与白名单"""

    def test_guess_mime(self):
        assert guess_mime("a.mp4") == "video/mp4"
        assert guess_mime("a.mp3") == "audio/mpeg"
        assert guess_mime("a.unknown") == "application/octet-stream"

    def test_is_ext_allowed(self):
        allowed = [".mp4", ".mp3"]
        assert is_ext_allowed("a.mp4", allowed)
        assert is_ext_allowed("a.MP4", allowed)  # 大小写不敏感
        assert not is_ext_allowed("a.exe", allowed)


class TestPathTraversal:
    """路径遍历防护（核心安全测试）"""

    def test_rejects_parent_escape(self, svc, user):
        with pytest.raises(ValidationError) as exc:
            svc.resolve_user_path(user.id, "../../../etc/passwd")
        assert exc.value.code == "FILE_403_001"

    def test_rejects_absolute_path_escape(self, svc, user):
        with pytest.raises(ValidationError):
            svc.resolve_user_path(user.id, "C:/Windows/System32")

    def test_rejects_sibling_user_dir(self, svc, user, other_user):
        """用户 A 不能访问用户 B 的目录"""
        with pytest.raises(ValidationError):
            svc.resolve_user_path(user.id, f"../{other_user.id}/secret.mp4")

    def test_allows_normal_subpath(self, svc, user):
        result = svc.resolve_user_path(user.id, "video/ep001.mp4")
        assert result.name == "ep001.mp4"
        assert str(user.id) in str(result)

    def test_rejects_empty_path(self, svc, user):
        with pytest.raises(ValidationError):
            svc.resolve_user_path(user.id, "")


class TestUpload:
    """上传"""

    def _tmp_file(self, tmp_path: Path, name: str, size: int = 1024) -> Path:
        p = tmp_path / name
        p.write_bytes(b"x" * size)
        return p

    def test_upload_success(self, svc, user, tmp_path):
        src = self._tmp_file(tmp_path, "demo.mp4")
        result = svc.upload(
            user=user, filename="demo.mp4", source_path=src, size_bytes=1024,
        )
        assert result["filename"] == "demo.mp4"
        assert result["size_bytes"] == 1024
        assert result["mime_type"] == "video/mp4"
        assert not src.exists()  # 已移动

    def test_upload_rejects_bad_ext(self, svc, user, tmp_path):
        src = self._tmp_file(tmp_path, "evil.exe")
        with pytest.raises(ValidationError) as exc:
            svc.upload(user=user, filename="evil.exe", source_path=src, size_bytes=10)
        assert exc.value.code == "FILE_400_004"

    def test_upload_rejects_oversize(self, svc, user, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "upload_max_mb", 0)  # 0 MB
        src = self._tmp_file(tmp_path, "big.mp4", 2048)
        with pytest.raises(ValidationError) as exc:
            svc.upload(user=user, filename="big.mp4", source_path=src, size_bytes=2048)
        assert exc.value.code == "FILE_400_003"

    def test_upload_uses_sub_dir(self, svc, user, tmp_path):
        src = self._tmp_file(tmp_path, "rec.mp3")
        result = svc.upload(
            user=user, filename="rec.mp3", source_path=src, size_bytes=512, sub_dir="audio",
        )
        assert "audio" in result["path"]

    def test_upload_unique_name(self, svc, user, tmp_path):
        s1 = self._tmp_file(tmp_path, "a1.mp4")
        svc.upload(user=user, filename="dup.mp4", source_path=s1, size_bytes=10)
        s2 = self._tmp_file(tmp_path, "a2.mp4")
        result = svc.upload(user=user, filename="dup.mp4", source_path=s2, size_bytes=10)
        assert result["filename"] == "dup (1).mp4"

    def test_upload_sanitizes_traversal_name(self, svc, user, tmp_path):
        src = self._tmp_file(tmp_path, "real.mp4")
        result = svc.upload(
            user=user, filename="../../evil.mp4", source_path=src, size_bytes=10,
        )
        assert ".." not in result["filename"]
        assert result["filename"] == "evil.mp4"


class TestOwnership:
    """用户隔离"""

    def test_other_user_cannot_get(self, svc, user, other_user, tmp_path):
        src = tmp_path / "mine.mp4"
        src.write_bytes(b"x" * 10)
        record = svc.upload(user=user, filename="mine.mp4", source_path=src, size_bytes=10)

        with pytest.raises(ForbiddenError):
            svc.get_owned_file(record["id"], other_user)

    def test_admin_can_get_any(self, svc, user, db, tmp_path):
        src = tmp_path / "mine.mp4"
        src.write_bytes(b"x" * 10)
        record = svc.upload(user=user, filename="mine.mp4", source_path=src, size_bytes=10)

        admin = User(
            id="u_admin_f", username="adminf", password_hash="x",
            is_admin=True, membership_tier="enterprise", is_active=True,
        )
        db.add(admin)
        db.commit()

        found = svc.get_owned_file(record["id"], admin)
        assert found.id == record["id"]

    def test_missing_file_raises(self, svc, user):
        with pytest.raises(NotFoundError):
            svc.get_owned_file("f_nonexistent", user)

    def test_list_only_own_files(self, svc, user, other_user, tmp_path):
        s1 = tmp_path / "a.mp4"
        s1.write_bytes(b"x" * 10)
        svc.upload(user=user, filename="a.mp4", source_path=s1, size_bytes=10)

        s2 = tmp_path / "b.mp4"
        s2.write_bytes(b"x" * 10)
        svc.upload(user=other_user, filename="b.mp4", source_path=s2, size_bytes=10)

        items, total = svc.list_files(user)
        assert total == 1
        assert items[0].user_id == user.id

    def test_delete_by_other_rejected(self, svc, user, other_user, tmp_path):
        src = tmp_path / "mine.mp4"
        src.write_bytes(b"x" * 10)
        record = svc.upload(user=user, filename="mine.mp4", source_path=src, size_bytes=10)

        with pytest.raises(ForbiddenError):
            svc.delete(record["id"], other_user)

    def test_delete_removes_file(self, svc, user, tmp_path):
        src = tmp_path / "gone.mp4"
        src.write_bytes(b"x" * 10)
        record = svc.upload(user=user, filename="gone.mp4", source_path=src, size_bytes=10)

        abs_path = svc.get_owned_file(record["id"], user).path
        assert Path(abs_path).exists()

        svc.delete(record["id"], user)
        assert not Path(abs_path).exists()


class TestPreviewDownload:
    """预览与下载"""

    def test_preview_returns_path(self, svc, user, tmp_path):
        src = tmp_path / "v.mp4"
        src.write_bytes(b"x" * 100)
        record = svc.upload(user=user, filename="v.mp4", source_path=src, size_bytes=100)

        path, mime, name = svc.preview_path(record["id"], user)
        assert mime == "video/mp4"
        assert name == "v.mp4"
        assert path.is_file()

    def test_preview_rejects_disallowed_ext(self, svc, user, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "allowed_preview_exts", [".mp4"])
        src = tmp_path / "x.txt"
        src.write_bytes(b"x" * 10)
        record = svc.upload(user=user, filename="x.txt", source_path=src, size_bytes=10)

        with pytest.raises(ValidationError) as exc:
            svc.preview_path(record["id"], user)
        assert exc.value.code == "FILE_400_005"

    def test_download_path(self, svc, user, tmp_path):
        src = tmp_path / "d.mp4"
        src.write_bytes(b"x" * 100)
        record = svc.upload(user=user, filename="d.mp4", source_path=src, size_bytes=100)

        path, name = svc.download_path(record["id"], user)
        assert name == "d.mp4"
        assert path.is_file()


class TestBrowseDir:
    """目录浏览"""

    def test_browse_root(self, svc, user):
        result = svc.browse_dir(user, "")
        assert "current" in result
        assert isinstance(result["items"], list)

    def test_browse_rejects_escape(self, svc, user):
        with pytest.raises(ValidationError) as exc:
            svc.browse_dir(user, "../../../")
        assert exc.value.code == "FILE_403_003"

    def test_browse_missing_dir(self, svc, user):
        with pytest.raises(NotFoundError):
            svc.browse_dir(user, "nonexistent_dir_xyz")


class TestQuotaIntegration:
    """配额联动"""

    def test_storage_quota_blocks_upload(self, db, tmp_path):
        from app.models.usage_record import UsageRecord

        limited = User(
            id="u_limited",
            username="limited",
            password_hash="x",
            membership_tier="free",
            is_active=True,
        )
        db.add(limited)
        db.commit()

        usage = UsageRecord(
            user_id=limited.id,
            year_month="2026-11",
            step_calls=0,
            storage_bytes=500 * 1024 * 1024,  # 已满
        )
        db.add(usage)
        db.commit()

        svc = FileService(db)
        src = tmp_path / "big.mp4"
        src.write_bytes(b"x" * 1024)

        with pytest.raises(QuotaExceededError):
            svc.upload(user=limited, filename="big.mp4", source_path=src, size_bytes=1024)

    def test_storage_quota_decrement_on_delete(self, svc, user, db, tmp_path):
        from app.models.usage_record import UsageRecord
        from app.services.quota_service import current_period, get_usage

        src = tmp_path / "s.mp4"
        src.write_bytes(b"x" * 2048)
        record = svc.upload(user=user, filename="s.mp4", source_path=src, size_bytes=2048)

        usage = get_usage(db, user.id)
        assert usage.storage_bytes == 2048

        svc.delete(record["id"], user)

        db.refresh(usage)
        assert usage.storage_bytes == 0
