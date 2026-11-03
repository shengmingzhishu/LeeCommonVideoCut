"""
edge-tts 端点补丁
=================
旧端点 `speech.platform.bing.com` 在部分网络（含本机）返回 WebSocket 403。
微软新版端点 `api.msedgeservices.com` 需要同时携带 TrustedClientToken 与
Ocp-Apim-Subscription-Key（值相同），并将 Origin 设为 edge.microsoft.com。

在 import TTSManager 时调用 `apply_edge_patch()`，使 edge_tts.Communicate 走新端点。
可通过 `.env` 的 TTS_EDGE_ENDPOINT=bing 回退到旧端点。
"""
from __future__ import annotations

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()

_EDGE_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
)


def apply_edge_patch() -> None:
    """把 edge_tts 的 WSS 端点切到新版（幂等）"""
    if (settings.tts_edge_endpoint or "").lower() == "bing":
        logger.info("TTS 使用 edge-tts 旧端点（bing）")
        return

    try:
        import edge_tts.communicate as communicate
        from edge_tts.constants import TRUSTED_CLIENT_TOKEN

        base = settings.tts_edge_wss_base.rstrip("?")
        sep = "&" if "?" in base else "?"
        url = (
            f"{base}{sep}TrustedClientToken={TRUSTED_CLIENT_TOKEN}"
            f"&Ocp-Apim-Subscription-Key={TRUSTED_CLIENT_TOKEN}"
        )
        headers = {
            "Origin": "https://edge.microsoft.com",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": _EDGE_UA,
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        communicate.WSS_URL = url
        communicate.WSS_HEADERS = headers
        logger.info("TTS 使用 edge-tts 新版端点", extra={"endpoint": base})
    except Exception as e:  # 补丁失败不应阻断启动，运行时自然降级
        logger.warning(f"edge-tts 端点补丁失败: {e}")
