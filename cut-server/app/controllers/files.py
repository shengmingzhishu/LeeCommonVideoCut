"""
文件路由
========
- POST   /api/files/upload              上传文件（multipart）
- GET    /api/files                     我的文件列表（分页）
- GET    /api/files/{file_id}           文件详情
- GET    /api/files/{file_id}/preview    预览（Range 流式，video/audio 内联播放）
- GET    /api/files/{file_id}/download  下载
- DELETE /api/files/{file_id}           删除
- GET    /api/dirs/browse                浏览目录（受限）
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, get_db
from app.core.exceptions import ValidationError
from app.core.logger import get_logger
from app.core.pagination import PageParams, page_params
from app.models.user import User
from app.schemas import ApiResponse, FileMetaResponse, FileUploadResponse, PageResponse
from app.services.file_service import FileService

router = APIRouter(tags=["Files"])
logger = get_logger()

# Range 请求解析：bytes=0-1023 / bytes=1024- / bytes=-500
CHUNK_SIZE = 1024 * 1024  # 1 MB


@router.post("/files/upload", response_model=ApiResponse[FileUploadResponse])
async def upload_file(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    file: Annotated[UploadFile, File(description="文件")],
    sub_dir: Annotated[str, Form(description="子目录（可选）")] = "",
):
    """上传文件

    流程：落临时文件 → 校验（大小/扩展名/配额）→ 移动到用户目录 → 写元数据
    """
    svc = FileService(db)

    if not file.filename:
        raise ValidationError("缺少文件名", code="FILE_400_006")

    # 落临时文件（边写边限制大小，避免超大文件占满磁盘）
    # 注意：Windows 上必须显式关闭 fd，否则文件被占用无法移动/删除
    max_bytes = settings.upload_max_mb * 1024 * 1024
    fd, tmp_name = tempfile.mkstemp(prefix="cut_upload_", suffix=".part")
    os.close(fd)  # 关键：关闭 mkstemp 返回的文件描述符
    tmp = Path(tmp_name)

    total = 0
    try:
        with tmp.open("wb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                total += len(chunk)
                if total > max_bytes:
                    raise ValidationError(
                        f"文件超过上限（{settings.upload_max_mb} MB）",
                        code="FILE_400_003",
                    )
                f.write(chunk)

        result = svc.upload(
            user=user,
            filename=file.filename,
            source_path=tmp,
            size_bytes=total,
            sub_dir=sub_dir,
        )
        return ApiResponse(data=FileUploadResponse(**result), msg="上传成功")
    finally:
        # 清理临时文件（可能已被移动走）
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


@router.get("/files", response_model=ApiResponse[PageResponse[FileMetaResponse]])
def list_files(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    pg: Annotated[PageParams, Depends(page_params)],
    sub_dir: str | None = Query(default=None),
):
    """我的文件列表"""
    svc = FileService(db)
    items, total = svc.list_files(user, sub_dir=sub_dir, page=pg.page, page_size=pg.page_size)

    return ApiResponse(
        data=PageResponse[FileMetaResponse](
            page=pg.page,
            page_size=pg.page_size,
            total=total,
            items=[
                FileMetaResponse(
                    id=f.id,
                    filename=Path(f.path).name,
                    path=svc.to_rel_path(user.id, Path(f.path)),
                    size_bytes=f.size_bytes,
                    mime_type=f.mime_type,
                    created_at=f.created_at,
                )
                for f in items
            ],
        )
    )


@router.get("/files/{file_id}", response_model=ApiResponse[FileMetaResponse])
def get_file(
    file_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """文件详情"""
    svc = FileService(db)
    record = svc.get_owned_file(file_id, user)
    return ApiResponse(
        data=FileMetaResponse(
            id=record.id,
            filename=Path(record.path).name,
            path=svc.to_rel_path(user.id, Path(record.path)),
            size_bytes=record.size_bytes,
            mime_type=record.mime_type,
            created_at=record.created_at,
        )
    )


@router.get("/files/{file_id}/preview")
def preview_file(
    file_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    range_header: Annotated[str | None, Query(alias="range")] = None,
):
    """预览文件（支持 Range 请求，供 <video>/<audio> 内联播放与拖拽定位）"""
    svc = FileService(db)
    path, mime, filename = svc.preview_path(file_id, user)
    size = path.stat().st_size

    range_spec = _parse_range(range_header, size)

    if range_spec is None:
        # 完整响应
        return FileResponse(
            path,
            media_type=mime,
            filename=filename,
            content_disposition_type="inline",
            headers={"Accept-Ranges": "bytes"},
        )

    start, end = range_spec
    length = end - start + 1

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
        media_type=mime,
        headers={
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Content-Length": str(length),
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )


@router.get("/files/{file_id}/download")
def download_file(
    file_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """下载文件（attachment，触发浏览器保存）"""
    svc = FileService(db)
    path, filename = svc.download_path(file_id, user)

    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=filename,
        content_disposition_type="attachment",
    )


@router.delete("/files/{file_id}", response_model=ApiResponse[None])
def delete_file(
    file_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """删除文件（仅本人或管理员）"""
    svc = FileService(db)
    svc.delete(file_id, user)
    return ApiResponse(msg="文件已删除")


@router.get("/dirs/browse", response_model=ApiResponse[dict[str, Any]])
def browse_dir(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    path: str = Query(default="", description="相对 workdir 的目录路径"),
):
    """浏览目录（受限在 workdir 内）"""
    svc = FileService(db)
    result = svc.browse_dir(user, path)
    return ApiResponse(data=result)


def _parse_range(range_header: str | None, size: int) -> tuple[int, int] | None:
    """解析 Range 头

    Returns:
        (start, end) 闭区间；None 表示无 Range 或格式非法
    """
    if not range_header:
        return None

    # 只处理 bytes=
    if not range_header.startswith("bytes="):
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

    if start >= size or start < 0:
        return None
    end = min(end, size - 1)
    if end < start:
        return None

    return start, end
