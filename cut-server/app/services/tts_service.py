"""
TTS 服务
========
- 音色目录（全局/段落可选）
- 音色试听（短文本即时合成，按参数哈希缓存）
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.managers.tts_manager import TTSManager
from app.schemas import TTSPreviewRequest


class TTSService:
    """TTS 目录与试听"""

    def list_voices(self) -> list[dict]:
        """返回可用音色（含默认语速/音调/音量）"""
        return TTSManager.list_voices()

    async def preview(self, req: TTSPreviewRequest) -> Path:
        """合成试听音频并返回本地路径（相同参数命中缓存）

        缓存带 provider 元数据：仅高质量 provider 的缓存可复用，
        避免历史降级产物（pyttsx3）被长期命中。
        """
        key = f"{req.text}|{req.voice_id}|{req.rate}|{req.pitch}|{req.volume}"
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
        cache_dir = settings.workdir_abs / "tts_preview"
        cache_dir.mkdir(parents=True, exist_ok=True)
        target = cache_dir / f"{digest}.mp3"
        meta_path = cache_dir / f"{digest}.json"

        if target.is_file() and target.stat().st_size > 1024 and meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                meta = {}
            if meta.get("provider") == "edge-tts":
                return target

        result = await TTSManager().synthesize(
            script=req.text,
            output_path=target,
            segments=[
                {
                    "text": req.text,
                    "voice_id": req.voice_id,
                    "rate": req.rate,
                    "pitch": req.pitch,
                    "volume": req.volume,
                }
            ],
        )
        if not target.is_file() or target.stat().st_size <= 1024:
            raise ExternalServiceError("试听音频生成失败", code="TTS_502_002")

        meta_path.write_text(
            json.dumps(
                {
                    "provider": result.get("provider"),
                    "provider_label": result.get("provider_label"),
                    "voice_id": result.get("voice_id"),
                    "duration": result.get("duration"),
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return target
