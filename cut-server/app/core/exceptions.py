"""
业务异常体系
============
所有业务异常必须继承自 AppError；main.py 的全局异常处理器统一转为统一响应格式。

HTTP 状态码语义（与 docs/openapi.yaml、共享规则 03 一致）：
- 401 未登录 / Token 失效
- 403 权限不足
- 404 资源不存在
- 402 会员配额不足
- 400 参数或路径非法
- 422 业务校验失败
- 502 外部服务（AI / 搜索）调用失败
"""
from __future__ import annotations


class AppError(Exception):
    """所有业务异常的基类"""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        http_status: int = 400,
        detail: str | None = None,
    ):
        self.code = code
        self.message = message
        self.http_status = http_status
        self.detail = detail
        super().__init__(message)


class AuthError(AppError):
    """鉴权错误"""

    def __init__(self, message: str = "未登录", code: str = "AUTH_401_001", detail: str | None = None):
        super().__init__(code, message, http_status=401, detail=detail)


class ForbiddenError(AppError):
    """权限错误"""

    def __init__(self, message: str = "权限不足", code: str = "AUTH_403_001", detail: str | None = None):
        super().__init__(code, message, http_status=403, detail=detail)


class NotFoundError(AppError):
    """资源不存在"""

    def __init__(self, message: str = "资源不存在", code: str = "COMMON_404_001", detail: str | None = None):
        super().__init__(code, message, http_status=404, detail=detail)


class QuotaExceededError(AppError):
    """会员配额不足"""

    def __init__(self, message: str = "会员配额不足", code: str = "MEMBER_402_001", detail: str | None = None):
        super().__init__(code, message, http_status=402, detail=detail)


class ValidationError(AppError):
    """业务校验失败"""

    def __init__(self, message: str = "请求参数无效", code: str = "COMMON_422_001", detail: str | None = None):
        super().__init__(code, message, http_status=422, detail=detail)


class AdminOnlyError(AppError):
    """仅管理员可访问"""

    def __init__(self, message: str = "仅管理员可访问", code: str = "ADMIN_403_001", detail: str | None = None):
        super().__init__(code, message, http_status=403, detail=detail)


class PathTraversalError(AppError):
    """路径越界"""

    def __init__(self, message: str = "文件路径越界", code: str = "FILE_400_001", detail: str | None = None):
        super().__init__(code, message, http_status=400, detail=detail)


class ExternalServiceError(AppError):
    """外部服务调用失败（AI / 搜索 / TTS）"""

    def __init__(self, message: str = "外部服务调用失败", code: str = "COMMON_502_001", detail: str | None = None):
        super().__init__(code, message, http_status=502, detail=detail)
