"""
日志
====
JSON 格式 + traceId 自动注入。
基于 loguru，简化配置。
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from loguru import logger

from app.core.config import settings


def _json_formatter(record) -> str:
    """loguru 回调：把日志记录转为 JSON 字符串。

    loguru 会把 format 返回值当作格式模板再解析一次，
    所以 JSON 不能直接 return，必须挂到 extra 上、由模板引用，否则花括号会被误当占位符。
    """
    payload = {
        "log_ts": datetime.now(timezone.utc).isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }
    # 透传 extra 字段（避开 loguru 内部保留字段）
    extras = record.get("extra", {})
    safe_extras = {k: v for k, v in extras.items() if k not in ("ts", "time", "timestamp", "serialized")}
    payload.update(safe_extras)
    record["extra"]["serialized"] = json.dumps(payload, ensure_ascii=False, default=str)
    return "{extra[serialized]}\n"


def setup_logging() -> None:
    """初始化日志（main.py 启动时调用一次）"""
    logger.remove()

    if settings.log_json:
        logger.add(
            sys.stdout,
            format=_json_formatter,
            level=settings.log_level,
            serialize=False,
            backtrace=True,
            diagnose=settings.debug,
        )
    else:
        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.log_level,
            backtrace=True,
            diagnose=settings.debug,
        )

    # 文件日志（开发环境可选）
    log_file = settings.workdir_abs.parent / "logs" / "app.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(log_file),
        format=_json_formatter,
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8",
    )


def get_logger():
    """获取 logger 实例（其他模块 import 用）"""
    return logger
