"""
HTTP Range 流式响应工具
=======================
浏览器 `<video>` / `<audio>` 拖拽定位依赖 206 Partial Content，
这里统一封装 Range 解析与响应构造，供文件预览、视频素材串播复用。

- parse_range：解析 `bytes=0-1023` / `bytes=1024-` / `bytes=-500`
- file_response：按是否带 Range 返回 200 全量或 206 分段
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from fastapi.responses import FileResponse, StreamingResponse

CHUNK_SIZE = 1024 * 1024  # 1 MB

# 常见媒体后缀 → MIME（视频串播必须准确，否则浏览器不认）
MIME_BY_SUFFIX: dict[str, str] = {
    ".mp4": "video/mp4",
    ".m4v": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".mkv": "video/x-matroska",
    ".avi": "video/x-msvideo",
    ".flv": "video/x-flv",
    ".ts": "video/mp2t",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".wav": "audio/wav",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
}


def guess_mime(path: Path) -> str:
    """按后缀推断媒体 MIME，未知类型回退二进制流"""
    return MIME_BY_SUFFIX.get(path.suffix.lower(), "application/octet-stream")


def parse_range(range_header: str | None, size: int) -> tuple[int, int] | None:
    """解析 Range 头

    Returns:
        (start, end) 闭区间；None 表示无 Range 或格式非法（按全量响应处理）
    """
    if not range_header or not range_header.startswith("bytes="):
        return None

    spec = range_header[6:].split(",")[0].strip()
    if "-" not in spec:
        return None

    start_str, _, end_str = spec.partition("-")

    try:
        if not start_str:
            # bytes=-500 → 最后 500 字节
            length = int(end_str)
            if length <= 0:
                return None
            start = max(0, size - length)
            end = size - 1
        else:
            start = int(start_str)
            end = int(end_str) if end_str else size - 1
    except ValueError:
        return None

    if start < 0 or start >= size or end < start:
        return None

    return start, min(end, size - 1)


def file_response(
    path: Path,
    range_header: str | None = None,
    *,
    inline: bool = True,
    mime: str | None = None,
):
    """构造文件响应（自动处理 Range）

    Args:
        path: 绝对路径
        range_header: 请求头 Range
        inline: True 内联播放，False 触发下载
        mime: 指定 MIME，默认按后缀推断
    """
    size = path.stat().st_size
    media_type = mime or guess_mime(path)
    disposition = "inline" if inline else "attachment"

    range_spec = parse_range(range_header, size)
    if range_spec is None:
        return FileResponse(
            path,
            media_type=media_type,
            filename=path.name,
            content_disposition_type=disposition,
            headers={"Accept-Ranges": "bytes"},
        )

    start, end = range_spec
    length = end - start + 1
    # HTTP 头只能是 latin-1；中文文件名按 RFC 5987 编码，避免 UnicodeEncodeError
    ascii_name = path.name.encode("ascii", "ignore").decode() or f"media{path.suffix}"
    disposition_header = (
        f'{disposition}; filename="{ascii_name}"; '
        f"filename*=UTF-8''{quote(path.name)}"
    )

    def iter_chunks():
        with path.open("rb") as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                data = f.read(min(CHUNK_SIZE, remaining))
                if not data:
                    break
                remaining -= len(data)
                yield data

    return StreamingResponse(
        iter_chunks(),
        status_code=206,
        media_type=media_type,
        headers={
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Content-Length": str(length),
            "Accept-Ranges": "bytes",
            "Content-Disposition": disposition_header,
        },
    )