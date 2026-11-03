"""
Pydantic Schemas（请求/响应 DTO）
================================
所有请求体与响应体在此定义。命名：
- CreateXxx：创建请求
- UpdateXxx：更新请求（部分字段可选）
- XxxResponse：单项响应
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

# 默认音色 ID（与 tts_manager.VOICE_CATALOG 对齐；schemas 不反向依赖 managers）
DEFAULT_TTS_VOICE_ID = "female_sweet"

# ============================================================
# 公共响应包装
# ============================================================
class ApiResponse(BaseModel, Generic[T]):
    """统一响应包装（成功）"""

    code: int = 0
    msg: str = "success"
    data: T | None = None
    traceId: str | None = None  # noqa: N815 契约字段名（跨端协作约定 §2）


class PageInfo(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)


class PageResponse(BaseModel, Generic[T]):
    """分页响应

    契约字段为 `pageSize`（docs/00-跨端协作约定.md §10、openapi.yaml PageResponse）。
    内部仍以 page_size 构造，序列化时输出 pageSize，避免前后端字段错位。
    """
    model_config = ConfigDict(populate_by_name=True)

    page: int = 1
    page_size: int = Field(default=20, serialization_alias="pageSize")
    total: int = 0
    items: list[T] = []


# 复用 Pydantic 的 ConfigDict 别名（from_attributes 替代 v1 的 orm_mode）
ORM_CONFIG = ConfigDict(from_attributes=True)


# ============================================================
# 用户
# ============================================================
class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6, max_length=64)
    email: str | None = None
    display_name: str | None = Field(default=None, max_length=64)


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=64)


class UserUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=64)
    avatar_url: str | None = Field(default=None, max_length=512)
    bio: str | None = None


class UserResponse(BaseModel):
    model_config = ORM_CONFIG
    id: str
    username: str
    email: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    is_admin: bool
    membership_tier: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LoginResponse(BaseModel):
    user: UserResponse
    token: str
    expires_at: datetime


# ============================================================
# 项目
# ============================================================
class ProjectCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    author: str = Field(min_length=1, max_length=128)
    intro: str = Field(min_length=10, max_length=2000)
    video_dir: str | None = Field(default=None, max_length=512)
    intro_dir: str | None = Field(default=None, max_length=512)
    cover: str = Field(default="🎬", max_length=8)
    video_file_ids: list[str] | None = Field(
        default=None,
        description="已上传的视频文件 ID；提供时由服务端解析为素材目录（优先于 video_dir）",
    )


class ProjectUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=128)
    author: str | None = Field(default=None, min_length=1, max_length=128)
    intro: str | None = Field(default=None, min_length=10, max_length=2000)
    video_dir: str | None = Field(default=None, max_length=512)
    intro_dir: str | None = Field(default=None, max_length=512)
    cover: str | None = Field(default=None, max_length=8)
    status: str | None = Field(default=None, pattern="^(active|archived)$")
    video_file_ids: list[str] | None = Field(
        default=None,
        description="已上传的视频文件 ID；提供时由服务端解析为素材目录（优先于 video_dir）",
    )


class ProjectResponse(BaseModel):
    model_config = ORM_CONFIG
    id: str
    user_id: str
    title: str
    author: str | None = None
    intro: str | None = None
    cover: str
    video_dir: str | None = None
    intro_dir: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


# ============================================================
# 剧集
# ============================================================
class EpisodeCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    description: str | None = None


class EpisodeUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    status: str | None = Field(default=None, pattern="^(active|archived)$")


class EpisodeResponse(BaseModel):
    model_config = ORM_CONFIG
    id: str
    project_id: str
    user_id: str
    title: str
    description: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


# ============================================================
# 创作
# ============================================================
class CreationCreateRequest(BaseModel):
    episode_id: str = Field(min_length=1, max_length=32, description="归属剧集 ID")
    title: str | None = Field(default=None, max_length=128)


class CreationResponse(BaseModel):
    model_config = ORM_CONFIG
    id: str
    episode_id: str
    user_id: str
    title: str | None = None
    current_step: int
    status: str
    created_at: datetime
    updated_at: datetime


class StepResultResponse(BaseModel):
    model_config = ORM_CONFIG
    id: str
    creation_id: str
    step_no: int
    version: int
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class CreationDetailResponse(CreationResponse):
    """创作详情（含各 Step 当前结果，key=step_no）"""
    step_results: dict[int, StepResultResponse] = Field(default_factory=dict)


# ============================================================
# Step1 创作信息
# ============================================================
class Step1Form(BaseModel):
    """创作信息表单"""

    title: str | None = Field(default=None, max_length=128)
    author: str | None = Field(default=None, max_length=128)
    intro: str | None = Field(default=None, max_length=2000)
    style: str = Field(default="热血安利", max_length=32)
    target_duration: int = Field(default=70, ge=20, le=300)
    episode_ids: list[str] = Field(default_factory=list)
    text_files: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    ref_titles: list[str] = Field(default_factory=list)
    value_points: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)


class Step1Outline(BaseModel):
    """AI 生成的大纲"""

    core_keywords: list[str] = Field(default_factory=list)
    core_words: list[str] = Field(default_factory=list)
    ref_titles: list[dict[str, str]] = Field(default_factory=list)
    main_task: str = ""
    core_value: list[str] = Field(default_factory=list)
    keypoints: list[str] = Field(default_factory=list)


class Step1OutlineRequest(BaseModel):
    creation_id: str
    form: Step1Form = Field(default_factory=Step1Form)


class Step1OutlineResponse(BaseModel):
    outline: Step1Outline


class Step1SaveRequest(BaseModel):
    creation_id: str
    form: Step1Form = Field(default_factory=Step1Form)
    outline: Step1Outline = Field(default_factory=Step1Outline)


class Step1SaveResponse(BaseModel):
    creation_id: str
    current_step: int
    form: Step1Form | None = None
    outline: Step1Outline | None = None


# ============================================================
# TTS 语音
# ============================================================
class TTSVoice(BaseModel):
    """音色目录项"""

    id: str
    name: str
    gender: str
    style: str
    voice: str
    rate: int = 0
    pitch: int = 0
    volume: int = 0
    description: str = ""


class TTSSegment(BaseModel):
    """段落音色配置"""

    index: int = 0
    text: str = Field(min_length=1, max_length=4000)
    voice_id: str | None = None
    rate: int = Field(default=0, ge=-100, le=200)
    pitch: int = Field(default=0, ge=-50, le=50)
    volume: int = Field(default=0, ge=-100, le=100)
    pause_after_ms: int = Field(default=0, ge=0, le=3000)


class TTSConfig(BaseModel):
    """整篇 TTS 配置（全局音色 + 段落覆盖）"""

    provider: str = Field(default="edge-tts", max_length=32)
    global_voice_id: str = DEFAULT_TTS_VOICE_ID
    rate: int = Field(default=0, ge=-100, le=200)
    pitch: int = Field(default=0, ge=-50, le=50)
    volume: int = Field(default=0, ge=-100, le=100)
    paragraph_gap_ms: int = Field(default=300, ge=0, le=3000)
    segments: list[TTSSegment] = Field(default_factory=list)


class TTSPreviewRequest(BaseModel):
    """音色试听"""

    text: str = Field(default="这是一段音色试听，欢迎使用漫剧推广素材剪辑师。", min_length=1, max_length=200)
    voice_id: str = DEFAULT_TTS_VOICE_ID
    rate: int = Field(default=0, ge=-100, le=200)
    pitch: int = Field(default=0, ge=-50, le=50)
    volume: int = Field(default=0, ge=-100, le=100)


# ============================================================
# Step2 口播长文
# ============================================================
class Step2GenerateRequest(BaseModel):
    creation_id: str
    title: str | None = Field(default=None, max_length=200)
    subtitle: str | None = Field(default=None, max_length=200)


class Step2GenerateResponse(BaseModel):
    title: str
    content: str
    word_count: int
    tts_config: TTSConfig | None = None


class Step2SaveRequest(BaseModel):
    creation_id: str
    title: str = Field(default="", max_length=200)
    content: str = Field(min_length=1)
    word_count: int = Field(default=0, ge=0)
    skip_tts: bool = False
    tts_config: TTSConfig | None = None


class Step2SaveResponse(BaseModel):
    creation_id: str
    current_step: int
    tts_task_id: str | None = None


# ============================================================
# Step3 音视频素材
# ============================================================
class AudioItem(BaseModel):
    path: str
    name: str
    duration: float = 0.0
    duration_str: str = "00:00"
    source: str = Field(default="system", pattern="^(system|custom)$")
    selected: bool = True


class VideoItem(BaseModel):
    name: str
    duration: float = 0.0
    duration_str: str = "00:00"
    selected: bool = True


class TransitionConfig(BaseModel):
    """转场配置（直切 / 淡入淡出 / 滑移 / 缩放）"""

    type: str = Field(default="none", pattern="^(none|fade|slide|zoom)$")
    duration: float = Field(default=0.5, ge=0.2, le=1.5)


class AvatarConfig(BaseModel):
    """主持人人像叠加配置"""

    file_id: str | None = Field(default=None, description="已上传图片文件 ID")
    position: str = Field(default="bottom_right", pattern="^(top_left|top_right|bottom_left|bottom_right)$")
    size_ratio: float = Field(default=0.18, ge=0.05, le=0.5, description="相对短边占比")
    border_color: str = Field(default="#FFFFFF", max_length=16)
    border_width: int = Field(default=4, ge=0, le=20)
    shadow: bool = True
    start: float = Field(default=0.0, ge=0)
    end: float | None = Field(default=None, ge=0)


class QualityConfig(BaseModel):
    """成片质量预设"""

    resolution: str = Field(default="1080x1920", pattern=r"^\d+x\d+$")
    crf: int = Field(default=23, ge=18, le=32)
    preset: str = Field(default="medium", pattern="^(ultrafast|veryfast|fast|medium|slow)$")


class BGMConfig(BaseModel):
    """背景音乐配置（音量比例 + 人声闪避 + 首尾淡入淡出）"""

    file_id: str | None = Field(default=None, description="已上传 BGM 文件 ID")
    volume: int = Field(default=30, ge=0, le=100, description="BGM 基准音量百分比")
    ducking: bool = Field(default=True, description="人声出现时自动压低音乐")
    duck_level: int = Field(default=30, ge=5, le=100, description="闪避后保留的音乐百分比")
    fade_in: float = Field(default=0.6, ge=0, le=5)
    fade_out: float = Field(default=0.8, ge=0, le=5)
    loop: bool = Field(default=True, description="BGM 短于成片时循环")


class IntroOutroItem(BaseModel):
    """片头 / 片尾字卡配置"""

    enabled: bool = False
    title: str = Field(default="", max_length=40)
    subtitle: str = Field(default="", max_length=60)
    duration: float = Field(default=3.0, ge=1.0, le=8.0)
    background_color: str = Field(default="#0F1117", pattern=r"^#[0-9A-Fa-f]{6}$")
    text_color: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    image_file_id: str | None = Field(default=None, description="背景图文件 ID（为空则纯色）")


class IntroOutroConfig(BaseModel):
    """片头片尾配置"""

    intro: IntroOutroItem = Field(default_factory=IntroOutroItem)
    outro: IntroOutroItem = Field(default_factory=IntroOutroItem)


class CoverExportRequest(BaseModel):
    """封面帧导出请求"""

    creation_id: str
    output_path: str | None = Field(default=None, description="成片路径；为空则取该创作最新成片")
    time: float | None = Field(default=None, ge=0, description="截取时间点（秒），默认 1.0s")


class VideoMark(BaseModel):
    id: int = 0
    source: str
    start: float = 0.0
    end: float = 0.0
    duration: float = 0.0
    muted: bool = True
    transition: TransitionConfig | None = Field(default=None, description="进入本段的转场（覆盖全局）")


class Step3RemarkRequest(BaseModel):
    creation_id: str
    video_files: list[str] = Field(default_factory=list)
    target_duration: int | None = Field(default=None, ge=20, le=300)


class Step3RemarkResponse(BaseModel):
    markers_path: str
    marker_count: int
    total_duration: float
    sources_used: list[str] = Field(default_factory=list)
    video_files: list[VideoItem] = Field(default_factory=list)
    markers: list[VideoMark] = Field(default_factory=list)


class Step3SaveStateRequest(BaseModel):
    creation_id: str
    audio_files: list[AudioItem] = Field(default_factory=list)
    video_files: list[VideoItem] = Field(default_factory=list)
    deleted_media: dict[str, list[str]] = Field(default_factory=dict)
    compose_settings: dict[str, Any] | None = Field(default=None, description="转场/头像/质量持久化配置")


class Step3SaveStateResponse(BaseModel):
    creation_id: str
    current_step: int


class Step3ComposeRequest(BaseModel):
    creation_id: str
    audio_files: list[str] = Field(default_factory=list)
    markers: list[VideoMark] = Field(default_factory=list)
    fast_mode: bool = False
    resolution: str = Field(default="1080x1920", pattern=r"^\d+x\d+$")
    subtitle_style: str = Field(default="默认白字黑描边", max_length=32)
    global_transition: TransitionConfig = Field(default_factory=TransitionConfig)
    avatar: AvatarConfig | None = None
    quality: QualityConfig | None = None
    bgm: BGMConfig | None = None
    intro_outro: IntroOutroConfig | None = None


class Step3VideoSourcesRequest(BaseModel):
    """把已上传的视频文件绑定为当前创作的素材目录"""

    creation_id: str
    file_ids: list[str] = Field(min_length=1, description="已上传的视频文件 ID 列表")


class SubtitleStyleSpec(BaseModel):
    """字幕样式在烧录端的真实参数（供前端等比换算预览）"""

    name: str
    force_style: str
    font_size: int
    margin_v: int
    alignment: int
    outline: float
    border_style: int
    primary_colour: str
    outline_colour: str
    back_colour: str


class Step3ComposeResponse(BaseModel):
    task_id: str


# ============================================================
# 文件
# ============================================================
class FileMetaResponse(BaseModel):
    """文件元信息"""
    id: str
    filename: str
    path: str = Field(description="相对用户上传目录的路径")
    size_bytes: int
    mime_type: str | None = None
    created_at: datetime


class FileUploadResponse(BaseModel):
    """上传结果"""
    id: str
    filename: str
    path: str
    size_bytes: int
    mime_type: str


# ============================================================
# 会员与配额
# ============================================================
class MembershipResponse(BaseModel):
    model_config = ORM_CONFIG
    id: str
    user_id: str
    tier: str = Field(description="free / pro / enterprise")
    status: str = Field(description="active / expired / cancelled")
    started_at: datetime
    expires_at: datetime | None = None
    assigned_by: str = ""
    note: str | None = None
    created_at: datetime


class MembershipAssignRequest(BaseModel):
    """管理员分配/续期会员"""
    user_id: str
    tier: str = Field(pattern="^(free|pro|enterprise)$")
    expires_at: datetime | None = Field(default=None, description="NULL = 永久有效")
    note: str | None = Field(default=None, max_length=500)


class QuotaInfoResponse(BaseModel):
    """配额使用快照"""
    tier: str
    projects_limit: int = Field(description="-1 = 无限")
    projects_used: int
    monthly_step_calls_limit: int = Field(description="-1 = 无限")
    monthly_step_calls_used: int
    storage_limit_mb: int = Field(description="-1 = 无限")
    storage_used_mb: float
    current_period: str = Field(description="YYYY-MM")


class AdminUserUpdateRequest(BaseModel):
    """管理员修改用户"""
    is_admin: bool | None = None
    is_active: bool | None = None
    membership_tier: str | None = Field(default=None, pattern="^(free|pro|enterprise)$")


class AdminResetPasswordRequest(BaseModel):
    new_password: str = Field(min_length=6, max_length=64)


# ============================================================
# 完成页
# ============================================================
class OutputResponse(BaseModel):
    id: str
    creation_id: str
    version: int
    output_path: str
    duration: float = 0.0
    duration_str: str = "00:00"
    file_size: int = 0
    resolution: str = ""
    is_latest: bool = False
    created_at: datetime


# ============================================================
# 任务
# ============================================================
class TaskResponse(BaseModel):
    model_config = ORM_CONFIG
    id: str
    user_id: str
    type: str
    status: str
    progress: int
    payload: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime


# ============================================================
# 配置（全局 / 用户级）
# ============================================================
class ConfigResponse(BaseModel):
    key: str
    user_id: str | None = Field(default=None, description="None 表示全局配置")
    value: dict[str, Any]
    description: str | None = None
    updated_at: datetime


class ConfigUpdateRequest(BaseModel):
    key: str = Field(min_length=1, max_length=64)
    value: dict[str, Any]
    description: str | None = None


class ConfigTestRequest(BaseModel):
    provider: str = Field(pattern="^(minimax|deepseek|bing_search)$")
    api_key: str = ""
    base_url: str | None = None
    model: str | None = None


class ConfigTestResult(BaseModel):
    success: bool
    message: str
    latency_ms: int | None = None


# ============================================================
# 错误响应（按共享规则 03）
# ============================================================
class ErrorResponse(BaseModel):
    code: str = Field(description="格式：{DOMAIN}_{HTTP}_{SEQ}")
    message: str
    detail: str | None = None
    traceId: str | None = None  # noqa: N815 契约字段名（跨端协作约定 §2）
    timestamp: str | None = None
    data: Any = None
