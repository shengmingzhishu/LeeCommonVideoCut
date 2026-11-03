"""
创作表
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.episode import Episode
    from app.models.step_result import StepResult
    from app.models.user import User


class Creation(Base):
    __tablename__ = "creations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    episode_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    current_step: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
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

    episode: Mapped[Episode] = relationship("Episode", back_populates="creations")
    user: Mapped[User] = relationship("User")
    step_results: Mapped[list[StepResult]] = relationship(
        "StepResult", back_populates="creation", cascade="all, delete-orphan"
    )
