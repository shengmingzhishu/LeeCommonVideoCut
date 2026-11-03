"""
文件服务
========
职责：
- 上传（分块落盘 + 配额校验 + 白名单 + 大小限制）
- 预览（Range 流式，支持 video/audio 内联播放）
- 下载（attachment）
- 列表 / 删除（仅限本人）
- 目录浏览（仅限用户可访问的根目录）

安全设计：
1. **用户隔离**：所有文件归属于 user_id，查询/下载/删除都校验 owner
2. **路径遍历防护**：用户上传的路径必须解析后仍在 workdir 内
3. **扩展名白名单**：只允许配置的白名单类型
4. **大小限制**：单文件 ≤ upload_max_mb
5. **配额联动**：上传计入 storage 配额
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    QuotaExceededError,
    ValidationError,
)
from app.core.logger import get_logger
from app.models.file import File
from app.models.user import User
from app.services.quota_service import ACTION_STORAGE, check_and_raise, consume_storage
from app.utils.file_types import (
    guess_mime,
    is_ext_allowed,
    sanitize_filename,
    unique_path,
)
from app.utils.safe_path import gen_id

logger = get_logger()


class FileService:
    """文件业务逻辑"""

    def __init__(self, db: Session, upload_root: Path | None = None):
        self.db = db
        # upload_root 可注入（测试隔离用），默认取配置的 upload_dir
        self._upload_root = upload_root

    # ---------- 目录 ----------

    @property
    def upload_root(self) -> Path:
        """用户上传根目录"""
        if self._upload_root is not None:
            p = Path(self._upload_root)
        else:
            p = settings.workdir_abs / settings.upload_dir
        p.mkdir(parents=True, exist_ok=True)
        return p

    def user_upload_dir(self, user_id: str) -> Path:
        """用户专属上传目录"""
        p = self.upload_root / user_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    def resolve_user_path(self, user_id: str, rel_path: str) -> Path:
        """解析用户传入的相对路径，确保落在该用户目录内

        Raises:
            ValidationError: 路径越界
        """
        if not rel_path:
            raise ValidationError("路径不能为空", code="FILE_400_002")

        user_root = self.user_upload_dir(user_id).resolve()
        target = (user_root / rel_path).resolve()

        try:
            target.relative_to(user_root)
        except ValueError as e:
            raise ValidationError(
                "路径越界：不允许访问其他用户的文件",
                code="FILE_403_001",
                detail=f"target={target}",
            ) from e

        return target

    # ---------- 上传 ----------

    def upload(
        self,
        *,
        user: User,
        filename: str,
        source_path: Path,
        size_bytes: int,
        sub_dir: str = "",
        mime_type: str | None = None,
    ) -> dict[str, Any]:
        """登记一个已落盘的文件

        Args:
            user: 所属用户
            filename: 原始文件名
            source_path: 已落盘的临时文件路径
            size_bytes: 文件大小
            sub_dir: 子目录（如 "audio" / "video"）
        """
        max_bytes = settings.upload_max_mb * 1024 * 1024
        if size_bytes > max_bytes:
            raise ValidationError(
                f"文件超过上限（{settings.upload_max_mb} MB）",
                code="FILE_400_003",
                detail=f"size={size_bytes}, max={max_bytes}",
            )

        safe_name = sanitize_filename(filename)
        if not is_ext_allowed(safe_name, settings.allowed_upload_exts):
            ext = Path(safe_name).suffix.lower()
            raise ValidationError(
                f"不支持的文件类型：{ext}",
                code="FILE_400_004",
                detail=f"allowed={settings.allowed_upload_exts}",
            )

        # 存储配额检查
        check_and_raise(self.db, user, ACTION_STORAGE, size_bytes)

        # 目标路径（用户隔离 + 子目录 + 唯一命名）
        target_dir = self.user_upload_dir(user.id)
        if sub_dir:
            safe_sub = sanitize_filename(sub_dir, "misc").replace(".", "_")
            target_dir = target_dir / safe_sub
            target_dir.mkdir(parents=True, exist_ok=True)

        target = unique_path(target_dir, safe_name)

        # 移动到目标位置（跨盘时 shutil.move 会自动退化为复制）
        moved = False
        try:
            shutil.move(str(source_path), str(target))
            moved = True
        except (OSError, shutil.Error):
            # 回退：复制后删除源
            try:
                shutil.copy2(str(source_path), str(target))
                moved = True
            except (OSError, shutil.Error) as e:
                raise ValidationError(
                    f"文件保存失败: {e}",
                    code="FILE_500_001",
                    detail=str(e),
                ) from e

        if moved:
            try:
                source_path.unlink(missing_ok=True)
            except OSError:
                pass  # 源文件可能已被移动走或被占用，忽略

        # 写元数据
        mime = mime_type or guess_mime(target)
        record = File(
            id=gen_id("f"),
            user_id=user.id,
            path=str(target),
            size_bytes=size_bytes,
            mime_type=mime,
        )
        self.db.add(record)

        # 计入存储用量
        consume_storage(self.db, user.id, size_bytes)
        self.db.commit()
        self.db.refresh(record)

        logger.info(
            "文件上传完成",
            extra={
                "user_id": user.id,
                "file_id": record.id,
                "filename": target.name,
                "size": size_bytes,
            },
        )

        return {
            "id": record.id,
            "filename": target.name,
            "path": self.to_rel_path(user.id, target),
            "size_bytes": size_bytes,
            "mime_type": mime,
        }

    # ---------- 查询 ----------

    def get_owned_file(self, file_id: str, user: User) -> File:
        """取文件并校验归属（管理员可访问任意文件）"""
        record = self.db.get(File, file_id)
        if not record:
            raise NotFoundError(f"文件不存在: {file_id}", code="FILE_404_001")
        if record.user_id != user.id and not user.is_admin:
            raise ForbiddenError("无权访问该文件", code="FILE_403_002")
        return record

    def list_files(
        self,
        user: User,
        *,
        sub_dir: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[File], int]:
        """列出我的文件（分页）"""
        stmt = select(File).where(File.user_id == user.id)
        if sub_dir:
            stmt = stmt.where(File.path.like(f"%{sub_dir}%"))
        stmt = stmt.order_by(File.created_at.desc())

        all_files = list(self.db.execute(stmt).scalars().all())
        total = len(all_files)
        start = (page - 1) * page_size
        return all_files[start:start + page_size], total

    def to_rel_path(self, user_id: str, abs_path: Path) -> str:
        """绝对路径 → 用户目录下的相对路径（用于 API 返回，避免泄露绝对路径）"""
        try:
            user_root = self.user_upload_dir(user_id).resolve()
            return abs_path.resolve().relative_to(user_root).as_posix()
        except ValueError:
            return abs_path.name

    # ---------- 删除 ----------

    def delete(self, file_id: str, user: User) -> None:
        """删除文件（仅本人或管理员）"""
        record = self.get_owned_file(file_id, user)

        path = Path(record.path)
        try:
            if path.is_file():
                path.unlink()
        except OSError as e:
            logger.warning(f"文件删除失败: {path}", extra={"error": str(e)})

        # 释放存储配额
        from app.services.quota_service import current_period, get_usage

        usage = get_usage(self.db, user.id)
        if usage and usage.storage_bytes >= record.size_bytes:
            usage.storage_bytes = max(0, usage.storage_bytes - record.size_bytes)

        self.db.delete(record)
        self.db.commit()

        logger.info("文件已删除", extra={"file_id": file_id, "user_id": user.id})

    # ---------- 预览 / 下载 ----------

    def preview_path(self, file_id: str, user: User) -> tuple[Path, str, str]:
        """取预览文件路径 + MIME + 文件名"""
        record = self.get_owned_file(file_id, user)
        path = Path(record.path)

        if not path.is_file():
            raise NotFoundError(f"文件已被移除: {record.path}", code="FILE_404_002")

        if not is_ext_allowed(path, settings.allowed_preview_exts):
            raise ValidationError(
                f"该文件类型不支持在线预览：{path.suffix}",
                code="FILE_400_005",
            )

        mime = record.mime_type or guess_mime(path)
        return path, mime, path.name

    def download_path(self, file_id: str, user: User) -> tuple[Path, str]:
        """取下载文件路径 + 文件名"""
        record = self.get_owned_file(file_id, user)
        path = Path(record.path)
        if not path.is_file():
            raise NotFoundError(f"文件已被移除: {record.path}", code="FILE_404_002")
        return path, path.name

    # ---------- 目录浏览（受限） ----------

    def browse_dir(self, user: User, path: str = "") -> dict[str, Any]:
        """浏览用户可访问的目录

        受限策略：只能浏览 workdir 内的目录（用户上传目录 + 用户工作目录）。
        """
        workdir = settings.workdir_abs.resolve()

        if not path:
            current = workdir
        else:
            current = (workdir / path).resolve()
            try:
                current.relative_to(workdir)
            except ValueError as e:
                raise ValidationError(
                    "路径越界", code="FILE_403_003", detail=f"target={current}"
                ) from e

        if not current.is_dir():
            raise NotFoundError(f"目录不存在: {current}", code="FILE_404_003")

        items: list[dict[str, Any]] = []

        # 上一级
        parent = current.parent
        if parent != current and workdir in parent.parents or parent == workdir:
            items.append({"name": "..", "path": str(parent), "type": "parent"})

        try:
            for entry in sorted(current.iterdir()):
                try:
                    if entry.is_dir():
                        items.append({
                            "name": entry.name,
                            "path": str(entry),
                            "type": "dir",
                        })
                    elif entry.is_file():
                        ext = entry.suffix.lower()
                        if not is_ext_allowed(entry, settings.allowed_preview_exts):
                            continue
                        items.append({
                            "name": entry.name,
                            "path": str(entry),
                            "type": "file",
                            "size": entry.stat().st_size,
                            "ext": ext,
                        })
                except OSError:
                    continue
        except PermissionError as e:
            raise ForbiddenError("无权限访问该目录", code="FILE_403_004") from e

        return {"current": str(current), "items": items}
