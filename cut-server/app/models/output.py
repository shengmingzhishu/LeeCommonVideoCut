"""
成品表（完成页：多次合成记录）
==============================
同一创作可多次合成，每次生成一条记录，version 自增，最新置顶。
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.creation import Creation


class Output(Base):
    __tablename__ = "outputs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    creation_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("creations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    output_path: Mapped[str] = mapped_column(String(512), nullable=False)
    duration: Mapped[float] = mapped_column(nullable=False, default=0.0)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    resolution: Mapped[str] = mapped_column(String(32), nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    creation: Mapped[Creation] = relationship("Creation")
