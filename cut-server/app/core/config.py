"""
应用配置
========
通过环境变量（含 .env）注入所有配置，避免硬编码。
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用全局配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- 基础 ----------
    app_name: str = "cut-server"
    app_version: str = "4.0.0"
    debug: bool = True
    log_level: str = "INFO"
    log_json: bool = True

    # ---------- 数据库 ----------
    database_url: str = Field(
        default="postgresql+psycopg://postgres:1234@localhost:5432/cut_video",
        description="PostgreSQL DSN",
    )
    db_pool_size: int = 10
    db_max_overflow: int = 10
    db_echo: bool = False

    # ---------- JWT ----------
    jwt_secret: str = "please-change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 30

    # ---------- TTS ----------
    tts_default_engine: str = "edge-tts"  # edge-tts | pyttsx3 | sapi
    tts_provider: str = "edge-tts"  # 首选 provider，与 tts_default_engine 等价
    # 降级链（逗号分隔）：高质量 provider → edge-tts → pyttsx3 → sapi
    tts_fallbacks: str = "edge-tts,pyttsx3,sapi"
    # edge-tts 端点：msedgeservices（新版可用）/ bing（旧版，部分网络 403）
    tts_edge_endpoint: str = "msedgeservices"
    tts_edge_wss_base: str = "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
    # 长文本最短有效语速（字/秒），用于校验产物是否短于文本所需
    tts_min_chars_per_sec: float = 12.0

    # ---------- AI（MiniMax M3 · OpenAI 兼容协议） ----------
    ai_provider: str = "minimax"
    minimax_api_key: str = "sk-cp-PUT-YOUR-REAL-KEY-HERE"
    minimax_base_url: str = "https://api.minimax.cn/v1"
    minimax_model: str = "MiniMax-M3"

    # ---------- 网络搜索 ----------
    search_engine: str = "duckduckgo"  # duckduckgo | bing
    bing_search_key: str = ""

    # ---------- 工作目录与文件 ----------
    workdir: Path = Path("./workspace").resolve()

    # 文件服务
    upload_max_mb: int = Field(default=500, description="单文件上传上限（MB）")
    upload_dir: str = Field(default="uploads", description="用户上传目录（相对 workdir）")
    # 允许预览/下载的扩展名白名单
    allowed_preview_exts: list[str] = Field(
        default_factory=lambda: [
            ".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv",
            ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac",
            ".jpg", ".jpeg", ".png", ".gif", ".webp",
            ".srt", ".txt", ".md",
        ],
    )
    allowed_upload_exts: list[str] = Field(
        default_factory=lambda: [
            ".mp4", ".mov", ".avi", ".mkv", ".webm",
            ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".webm",
            ".jpg", ".jpeg", ".png", ".gif",
            ".txt", ".md", ".srt",
        ],
    )

    # ---------- 异步任务 ----------
    task_max_lifetime_hours: int = 24

    # ---------- 启动引导 ----------
    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "admin123456"

    # ---------- CORS ----------
    cors_origins: list[str] = ["*"]  # 开发用，生产收紧

    @property
    def workdir_abs(self) -> Path:
        """工作目录的绝对路径"""
        p = self.workdir if self.workdir.is_absolute() else (Path.cwd() / self.workdir).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """单例获取配置（避免重复读 .env）"""
    return Settings()


settings = get_settings()
