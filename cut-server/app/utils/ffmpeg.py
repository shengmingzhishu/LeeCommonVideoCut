"""
ffmpeg / ffprobe 定位与能力检测
==============================
优先级：
1. 环境变量 FFMPEG_BIN（推荐，指向项目 tools/ffmpeg/bin/ffmpeg.exe）
2. 环境变量 FFMPEG_HOME（自动拼接 bin/ffmpeg.exe 与 bin/ffprobe.exe）
3. 系统 PATH

本机 TRAE 自带 ffmpeg 为极限精简版（--disable-everything），
缺少 rawvideo/lavfi/subtitles/trim/concat 等关键能力，
因此项目内置完整版于 <repo>/tools/ffmpeg/bin/。
"""
from __future__ import annotations

import os
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

# 项目内置 ffmpeg（相对本文件上溯到仓库根）
_REPO_ROOT = Path(__file__).resolve().parents[3]
_BUNDLED_BIN = _REPO_ROOT / "tools" / "ffmpeg" / "bin"

# 关键能力清单（完整版必须具备）
REQUIRED_FILTERS = ("trim", "concat", "scale", "fps", "subtitles")


@lru_cache(maxsize=1)
def _resolve_bin(name: str) -> str | None:
    """定位可执行文件（ffmpeg / ffprobe）"""
    exe = f"{name}.exe" if os.name == "nt" else name

    # 1. 显式指定
    explicit = os.environ.get("FFMPEG_BIN")
    if explicit:
        p = Path(explicit)
        candidate = p / exe if p.is_dir() else p
        if candidate.exists():
            return str(candidate)

    # 2. FFMPEG_HOME
    home = os.environ.get("FFMPEG_HOME")
    if home:
        candidate = Path(home) / "bin" / exe
        if candidate.exists():
            return str(candidate)
        candidate = Path(home) / exe
        if candidate.exists():
            return str(candidate)

    # 3. 项目内置
    bundled = _BUNDLED_BIN / exe
    if bundled.exists():
        return str(bundled)

    # 4. 系统 PATH
    return shutil.which(name)


def ffmpeg_bin() -> str:
    """ffmpeg 可执行路径（找不到时返回 "ffmpeg" 交给系统处理）"""
    return _resolve_bin("ffmpeg") or "ffmpeg"


def ffprobe_bin() -> str:
    """ffprobe 可执行路径"""
    return _resolve_bin("ffprobe") or "ffprobe"


def ffmpeg_available() -> bool:
    """ffmpeg 是否可用"""
    return _resolve_bin("ffmpeg") is not None


def ffprobe_available() -> bool:
    """ffprobe 是否可用"""
    return _resolve_bin("ffprobe") is not None


def ffmpeg_version() -> str | None:
    """ffmpeg 版本号"""
    if not ffmpeg_available():
        return None
    try:
        out = subprocess.run(
            [ffmpeg_bin(), "-version"], capture_output=True, text=True, timeout=10
        )
        return out.stdout.split("\n")[0] if out.returncode == 0 else None
    except Exception:
        return None


def missing_capabilities() -> list[str]:
    """检测缺失的关键滤镜（返回空列表表示能力完整）"""
    if not ffmpeg_available():
        return ["ffmpeg"]
    try:
        out = subprocess.run(
            [ffmpeg_bin(), "-hide_banner", "-filters"],
            capture_output=True, text=True, timeout=15,
        )
        text = out.stdout + out.stderr
    except Exception:
        return list(REQUIRED_FILTERS)

    missing = [f for f in REQUIRED_FILTERS if f not in text]
    return missing
