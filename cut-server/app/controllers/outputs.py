"""
完成页路由（多次合成列表 + 成片预览/下载）
==========================================
- GET /api/creations/{creation_id}/outputs                 该创作的合成记录（最新置顶）
- GET /api/creations/{creation_id}/outputs/{output_id}/file 成片在线预览 / 下载
"""
from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, get_db
from app.core.exceptions import NotFoundError, PathTraversalError
from app.core.logger import get_logger
from app.models.user import User
from app.schemas import ApiResponse, OutputResponse
from app.services.creation_service import CreationService
from app.services.step3_service import Step3Service
from app.utils.safe_path import format_duration

router = APIRouter(prefix="/creations", tags=["Outputs"])
logger = get_logger()


@router.get("/{creation_id}/outputs", response_model=ApiResponse[list[OutputResponse]])
def list_outputs(
    creation_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """完成页：多次合成列表（最新置顶）"""
    creation_svc = CreationService(db)
    creation = creation_svc.get(creation_id)
    creation_svc.check_ownership(creation, user.id, user.is_admin)

    outputs = Step3Service(db).list_outputs(creation)
    items = [
        OutputResponse(
            id=o.id,
            creation_id=o.creation_id,
            version=o.version,
            output_path=o.output_path,
            duration=o.duration,
            duration_str=format_duration(o.duration),
            file_size=o.file_size,
            resolution=o.resolution,
            is_latest=(idx == 0),
            created_at=o.created_at,
        )
        for idx, o in enumerate(outputs)
    ]
    return ApiResponse(data=items)


@router.get("/{creation_id}/outputs/{output_id}/file")
def get_output_file(
    creation_id: str,
    output_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    download: Annotated[bool, Query(description="true = 附件下载，false = 在线预览")] = False,
):
    """成片预览 / 下载（校验创作归属，限制在 workdir 内）"""
    creation_svc = CreationService(db)
    creation = creation_svc.get(creation_id)
    creation_svc.check_ownership(creation, user.id, user.is_admin)

    output = next(
        (o for o in Step3Service(db).list_outputs(creation) if o.id == output_id),
        None,
    )
    if not output:
        raise NotFoundError(f"成品不存在: {output_id}", code="OUTPUT_404_001")

    path = _resolve_output_path(output.output_path)
    filename = f"{creation_id}_v{output.version}{path.suffix or '.mp4'}"
    disposition = "attachment" if download else "inline"

    return FileResponse(
        path,
        media_type="video/mp4",
        filename=filename,
        content_disposition_type=disposition,
        headers={"Accept-Ranges": "bytes"},
    )


def _resolve_output_path(output_path: str) -> Path:
    """成品相对路径 → 绝对路径（限制在 workdir 内，防路径穿越）"""
    p = Path(output_path)
    if not p.is_absolute():
        p = settings.workdir_abs / p
    p = p.resolve()
    root = settings.workdir_abs.resolve()

    try:
        p.relative_to(root)
    except ValueError as e:
        raise PathTraversalError("成品路径越界", detail=str(p)) from e

    if not p.is_file():
        raise NotFoundError(f"成品文件不存在: {output_path}", code="OUTPUT_404_002")
    return p
