"""
健康检查 + 系统状态
"""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.core.database import session_scope
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/health")
def health_check():
    """健康检查：返回 ffmpeg / PostgreSQL / MiniMax 可用性"""
    from app.utils.ffmpeg import ffmpeg_available, ffprobe_available

    # PostgreSQL 连接测试
    pg_ok = False
    try:
        with session_scope() as db:
            db.execute(text("SELECT 1"))
            pg_ok = True
    except Exception as e:
        logger.warning(f"PostgreSQL 连接失败: {e}")

    minimax_ok = settings.minimax_api_key != "sk-cp-PUT-YOUR-REAL-KEY-HERE"

    return {
        "code": 0,
        "msg": "success",
        "data": {
            "status": "ok" if pg_ok else "degraded",
            "ffmpeg_available": ffmpeg_available(),
            "ffprobe_available": ffprobe_available(),
            "postgres_available": pg_ok,
            "minimax_configured": minimax_ok,
            "version": settings.app_version,
        },
        "traceId": None,  # 中间件会回填
    }
