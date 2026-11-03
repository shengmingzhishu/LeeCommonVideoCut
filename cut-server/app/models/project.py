"""
项目表
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.episode import Episode
    from app.models.user import User


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    author: Mapped[str | None] = mapped_column(String(128), nullable=True)
    intro: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover: Mapped[str] = mapped_column(String(8), nullable=False, default="🎬")
    video_dir: Mapped[str | None] = mapped_column(String(512), nullable=True)
    intro_dir: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship("User", back_populates="projects")
    episodes: Mapped[list[Episode]] = relationship(
        "Episode", back_populates="project", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_projects_created_at", "created_at"),)
