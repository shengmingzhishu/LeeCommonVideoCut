"""
TTS 路由
========
- GET  /api/tts/voices   音色目录（13 个中文风格）
- POST /api/tts/preview  音色试听（返回 audio/mpeg）
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas import ApiResponse, TTSPreviewRequest
from app.services.tts_service import TTSService

router = APIRouter(prefix="/tts", tags=["TTS"])


@router.get("/voices", response_model=ApiResponse[list[dict]])
def list_voices(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """音色目录"""
    return ApiResponse(data=TTSService().list_voices())


@router.post("/preview")
async def preview(
    req: TTSPreviewRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """试听（短文本即时合成，返回音频流）"""
    path = await TTSService().preview(req)
    return FileResponse(path, media_type="audio/mpeg", filename="tts_preview.mp3")
