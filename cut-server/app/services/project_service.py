"""
项目服务
========
"""
from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.logger import get_logger
from app.models.project import Project
from app.schemas import ProjectCreateRequest, ProjectUpdateRequest

logger = get_logger()


class ProjectService:
    """项目业务逻辑（不涉及权限校验，权限在 controller 层）"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, req: ProjectCreateRequest) -> Project:
        """创建项目"""
        from app.utils.safe_path import gen_id

        video_dir = (
            self._resolve_video_dir(user_id, req.video_file_ids)
            if req.video_file_ids
            else req.video_dir
        )

        project = Project(
            id=gen_id("p"),
            user_id=user_id,
            title=req.title,
            author=req.author,
            intro=req.intro,
            video_dir=video_dir,
            intro_dir=req.intro_dir,
            cover=req.cover,
            status="active",
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        logger.info(
            "项目创建成功",
            extra={"project_id": project.id, "user_id": user_id, "title": project.title},
        )
        return project

    def get(self, project_id: str) -> Project:
        project = self.db.get(Project, project_id)
        if not project:
            raise NotFoundError(f"项目不存在: {project_id}", code="PROJ_404_001")
        return project

    def list(
        self,
        user_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        status: str | None = None,
    ) -> tuple[Sequence[Project], int]:
        """用户项目列表（分页）"""
        stmt = select(Project).where(Project.user_id == user_id)
        count_stmt = select(func.count(Project.id)).where(Project.user_id == user_id)

        if keyword:
            kw = f"%{keyword}%"
            kw_cond = or_(Project.title.ilike(kw), Project.author.ilike(kw))
            stmt = stmt.where(kw_cond)
            count_stmt = count_stmt.where(kw_cond)
        if status:
            stmt = stmt.where(Project.status == status)
            count_stmt = count_stmt.where(Project.status == status)

        stmt = stmt.order_by(Project.created_at.desc()).limit(page_size).offset((page - 1) * page_size)

        items = self.db.execute(stmt).scalars().all()
        total = self.db.execute(count_stmt).scalar() or 0
        return items, total

    def update(self, project_id: str, req: ProjectUpdateRequest) -> Project:
        project = self.get(project_id)
        data = req.model_dump(exclude_unset=True)

        # video_file_ids 优先于 video_dir：由服务端解析为实际素材目录
        if "video_file_ids" in data:
            file_ids = data.pop("video_file_ids") or []
            data["video_dir"] = (
                self._resolve_video_dir(project.user_id, file_ids) if file_ids else None
            )

        for k, v in data.items():
            setattr(project, k, v)
        self.db.commit()
        self.db.refresh(project)
        return project

    def _resolve_video_dir(self, user_id: str, file_ids: list[str]) -> str:
        """把已上传的视频文件 ID 解析为素材目录（取这些文件的公共父目录）

        Raises:
            NotFoundError: 文件不存在或不属于当前用户
            ValidationError: 文件已丢失或跨盘无法推导公共目录
        """
        from app.models.file import File

        parents: list[Path] = []
        for file_id in file_ids:
            record = self.db.get(File, file_id)
            if not record or record.user_id != user_id:
                raise NotFoundError(f"文件不存在: {file_id}", code="FILE_404_001")
            path = Path(record.path)
            if not path.is_file():
                raise NotFoundError(f"文件已被移除: {record.path}", code="FILE_404_002")
            parents.append(path.parent.resolve())

        try:
            common = Path(os.path.commonpath([str(p) for p in parents]))
        except ValueError as e:
            raise ValidationError(
                "选择的视频文件不在同一磁盘，无法作为同一素材目录",
                code="FILE_422_007",
            ) from e

        return str(common)

    def delete(self, project_id: str) -> None:
        project = self.get(project_id)
        self.db.delete(project)
        self.db.commit()

    def copy(self, project_id: str, user_id: str) -> Project:
        """复制项目（仅复制项目元数据，不复制剧集与创作，遵循旧版行为）"""
        from app.utils.safe_path import gen_id

        src = self.get(project_id)
        new = Project(
            id=gen_id("p"),
            user_id=user_id,
            title=f"{src.title} (副本)",
            author=src.author,
            intro=src.intro,
            cover=src.cover,
            video_dir=src.video_dir,
            intro_dir=src.intro_dir,
            status="active",
        )
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new

    def check_ownership(self, project: Project, user_id: str, is_admin: bool) -> None:
        """校验项目所有权（仅管理员或 owner 可操作）"""
        if is_admin:
            return
        if project.user_id != user_id:
            raise ForbiddenError("无权访问该项目", code="PROJ_403_001")
