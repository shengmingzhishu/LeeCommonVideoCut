"""
历史快照表（每次执行都 INSERT 一条，用于回滚/对比）
====================================================
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.creation import Creation


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    creation_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("creations.id", ondelete="CASCADE"), nullable=False
    )
    step_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    creation: Mapped[Creation] = relationship("Creation")

    __table_args__ = (
        Index("ix_history_creation_step", "creation_id", "step_no", "version"),
    )
