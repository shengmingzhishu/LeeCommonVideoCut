"""
文件类型与 MIME 工具
====================
- 扩展名白名单校验
- MIME 推断
- 文件名清理
"""
from __future__ import annotations

import re
from pathlib import Path

# 扩展名 → MIME
MIME_MAP: dict[str, str] = {
    # 视频
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
    ".flv": "video/x-flv",
    ".wmv": "video/x-ms-wmv",
    # 音频
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    # 图片
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    # 文本
    ".srt": "application/x-subrip",
    ".txt": "text/plain; charset=utf-8",
    ".md": "text/markdown; charset=utf-8",
    ".json": "application/json",
}

DEFAULT_MIME = "application/octet-stream"

# 非法文件名字符（Windows 保留）
_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|\r\n\t]')


def guess_mime(path: str | Path) -> str:
    """根据扩展名推断 MIME 类型"""
    ext = Path(path).suffix.lower()
    return MIME_MAP.get(ext, DEFAULT_MIME)


def sanitize_filename(name: str, default: str = "upload") -> str:
    """文件名清理：去非法字符 + 防路径穿越 + 限长"""
    # 只取最后一段（防止 ../../etc/passwd）
    base = Path(name.replace("\\", "/")).name
    cleaned = _ILLEGAL_CHARS.sub("_", base).strip(" .")
    if not cleaned:
        cleaned = default
    if len(cleaned) > 96:
        stem, dot, ext = cleaned.rpartition(".")
        if dot:
            cleaned = f"{stem[:80]}{dot}{ext[:16]}"
        else:
            cleaned = cleaned[:96]
    return cleaned


def unique_path(directory: Path, filename: str) -> Path:
    """生成不冲突的路径：name.txt → name (1).txt → name (2).txt"""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / filename
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    i = 1
    while True:
        candidate = directory / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1
        if i > 9999:
            raise RuntimeError(f"无法为 {filename} 生成唯一文件名")


def is_ext_allowed(path: str | Path, allowed: list[str]) -> bool:
    """扩展名是否在白名单内"""
    ext = Path(path).suffix.lower()
    return ext in {e.lower() for e in allowed}
