"""
Step3 路由：音视频素材
======================
- GET  /api/step3/media-list   获取音频与视频素材列表
- GET  /api/step3/preview      串播预览（Range 流式，音频/视频内联播放）
- POST /api/step3/remark       对勾选视频重新随机标记
- POST /api/step3/save-state   保存素材选择状态
- POST /api/step3/video-sources 绑定批量上传的视频素材
- GET  /api/step3/subtitle-styles 字幕模板 + 烧录端参数
- POST /api/step3/compose      一键合成（异步任务）
"""
from __future__ import annotations

from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.logger import get_logger
from app.models.creation import Creation
from app.models.user import User
from app.schemas import (
    ApiResponse,
    CoverExportRequest,
    Step3ComposeRequest,
    Step3ComposeResponse,
    Step3RemarkRequest,
    Step3RemarkResponse,
    Step3SaveStateRequest,
    Step3SaveStateResponse,
    Step3VideoSourcesRequest,
    SubtitleStyleSpec,
)
from app.services.creation_service import CreationService
from app.services.step3_service import Step3Service
from app.utils.range_stream import file_response

router = APIRouter(prefix="/step3", tags=["Step3"])
logger = get_logger()


def _load_creation(db: Session, creation_id: str, user: User) -> Creation:
    """加载创作并校验所有权"""
    svc = CreationService(db)
    creation = svc.get(creation_id)
    svc.check_ownership(creation, user.id, user.is_admin)
    return creation


@router.get("/media-list", response_model=ApiResponse[dict[str, Any]])
def media_list(
    creation_id: Annotated[str, Query()],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """获取音频与视频素材列表"""
    creation = _load_creation(db, creation_id, user)
    return ApiResponse(data=Step3Service(db).media_list(creation))


@router.get("/preview")
def preview_media(
    creation_id: Annotated[str, Query()],
    scope: Annotated[Literal["video", "audio"], Query()],
    name: Annotated[str, Query(min_length=1)],
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """串播预览：返回素材文件（支持 Range，供 <video>/<audio> 内联播放）"""
    creation = _load_creation(db, creation_id, user)
    path = Step3Service(db).resolve_preview_path(creation, scope, name)
    return file_response(path, request.headers.get("range"))


@router.post("/remark", response_model=ApiResponse[Step3RemarkResponse])
def remark(
    req: Step3RemarkRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """对勾选视频重新随机标记

    目标时长以音频时长为锚（自动推导），也可由前端显式指定。
    """
    creation = _load_creation(db, req.creation_id, user)
    result = Step3Service(db).remark(
        creation=creation,
        video_files=req.video_files,
        target_duration=req.target_duration,
    )
    return ApiResponse(data=result)


@router.post("/save-state", response_model=ApiResponse[Step3SaveStateResponse])
def save_state(
    req: Step3SaveStateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """保存素材选择状态"""
    creation = _load_creation(db, req.creation_id, user)
    result = Step3Service(db).save_state(
        creation=creation,
        audio_files=[a.model_dump() for a in req.audio_files],
        video_files=[v.model_dump() for v in req.video_files],
        deleted_media=req.deleted_media,
        compose_settings=req.compose_settings,
    )
    return ApiResponse(data=result, msg="保存成功")


@router.post("/video-sources", response_model=ApiResponse[dict[str, Any]])
def bind_video_sources(
    req: Step3VideoSourcesRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """把批量上传的视频绑定为当前创作素材目录，返回最新视频列表"""
    creation = _load_creation(db, req.creation_id, user)
    result = Step3Service(db).bind_video_sources(
        creation=creation, file_ids=req.file_ids
    )
    return ApiResponse(data=result, msg="素材已绑定")


@router.get("/subtitle-styles", response_model=ApiResponse[list[SubtitleStyleSpec]])
def subtitle_styles(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """字幕模板清单 + 烧录端真实参数（字号 / 边距 / 对齐 / 描边）"""
    _ = user
    return ApiResponse(data=[SubtitleStyleSpec(**s) for s in Step3Service(db).subtitle_styles()])


@router.post("/compose", response_model=ApiResponse[Step3ComposeResponse])
def compose(
    req: Step3ComposeRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """一键合成（裁切 + 合并 + 音视频合成 + 字幕烧录）

    长任务异步执行，立即返回 task_id，前端轮询 GET /api/tasks/{task_id}。
    """
    creation = _load_creation(db, req.creation_id, user)
    task_id = Step3Service(db).compose(
        creation=creation,
        audio_files=req.audio_files,
        markers=[m.model_dump() for m in req.markers],
        fast_mode=req.fast_mode,
        resolution=req.resolution,
        subtitle_style=req.subtitle_style,
        global_transition=req.global_transition.model_dump(),
        avatar=req.avatar.model_dump() if req.avatar else None,
        quality=req.quality.model_dump() if req.quality else None,
        bgm=req.bgm.model_dump() if req.bgm else None,
        intro_outro=req.intro_outro.model_dump() if req.intro_outro else None,
    )
    return ApiResponse(data=Step3ComposeResponse(task_id=task_id), msg="合成任务已提交")


@router.post("/cover")
def export_cover(
    req: CoverExportRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """封面帧导出：从成片（或指定时间点）返回 JPEG 封面图"""
    creation = _load_creation(db, req.creation_id, user)
    path = Step3Service(db).export_cover(
        creation=creation,
        output_path=req.output_path,
        time=req.time,
    )
    return FileResponse(
        path,
        media_type="image/jpeg",
        filename=path.name,
        content_disposition_type="inline",
    )
