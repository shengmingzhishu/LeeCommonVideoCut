"""
通用工具函数
============
- ID 生成
- 时间格式化
- 路径安全校验
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path


def gen_id(prefix: str) -> str:
    """生成短 ID：prefix + 16 位 hex（无连字符）

    例：gen_id("u") → "u_a3b9c2d8e1f40712"
    """
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def now_utc() -> datetime:
    """返回 UTC datetime"""
    return datetime.now(timezone.utc)


def iso_now() -> str:
    """返回当前时间的 ISO 8601 UTC 字符串"""
    return now_utc().isoformat()


def safe_join(workdir: Path, user_path: str) -> Path:
    """路径遍历防护：解析后必须仍在 workdir 内"""
    if not user_path:
        raise ValueError("path 不能为空")
    workdir_abs = workdir.resolve()
    target = (workdir_abs / user_path).resolve()
    try:
        target.relative_to(workdir_abs)
    except ValueError as e:
        raise ValueError(f"路径越界: {target}") from e
    return target


def format_duration(seconds: float) -> str:
    """秒 → HH:MM:SS 或 MM:SS"""
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
