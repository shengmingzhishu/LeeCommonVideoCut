"""
步骤结果表（每步当前版本）
==========================
UNIQUE (creation_id, step_no, version) 保证版本号唯一。
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.creation import Creation


class StepResult(Base):
    __tablename__ = "step_results"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    creation_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("creations.id", ondelete="CASCADE"), nullable=False
    )
    step_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    creation: Mapped[Creation] = relationship("Creation", back_populates="step_results")

    __table_args__ = (
        UniqueConstraint("creation_id", "step_no", "version", name="uk_step_result_version"),
    )
