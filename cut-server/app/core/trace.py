"""
traceId 中间件
==============
- 请求进入时读 X-Trace-Id，没有则生成 UUID
- 写入 request.state.trace_id
- 通过 X-Trace-Id 响应头回写
- 对 JSON 响应体回填 traceId 字段（跨端协作约定 §9：前后端日志必须能对齐）
"""
from __future__ import annotations

import json
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TraceIdMiddleware(BaseHTTPMiddleware):
    """注入 traceId 并回填响应体"""

    async def dispatch(self, request: Request, call_next):
        # 1. 读取或生成 traceId
        trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex[:16]

        # 2. 写入 request.state（供下游使用）
        request.state.trace_id = trace_id

        # 3. 调用下游
        response: Response = await call_next(request)

        # 4. 响应头回写
        response.headers["X-Trace-Id"] = trace_id

        # 5. JSON 响应体回填 traceId
        await self._fill_trace_id(response, trace_id)
        return response

    @staticmethod
    async def _fill_trace_id(response: Response, trace_id: str) -> None:
        """在 JSON 响应体中回填 traceId 字段（仅当响应体未自带该字段）"""
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # 非 JSON 或流式响应，原样返回
            response.body_iterator = _iter_bytes(body)
            return

        if not isinstance(payload, dict):
            response.body_iterator = _iter_bytes(body)
            return

        if payload.get("traceId") is None:
            payload["traceId"] = trace_id
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            response.headers["content-length"] = str(len(body))

        response.body_iterator = _iter_bytes(body)


async def _iter_bytes(body: bytes):
    """把 bytes 包装成异步迭代器，供 StreamingResponse 消费"""
    yield body
