"""
分页参数依赖
============
契约字段为 `pageSize`（docs/00-跨端协作约定.md §10）：
- 主参数：`?page=1&pageSize=20`
- 兼容参数：`?page=1&page_size=20`（旧前端/脚本，不进 OpenAPI 文档）

控制器统一用 `Annotated[PageParams, Depends(page_params)]` 注入，
避免每个列表接口重复声明三份 Query 参数。
"""
from __future__ import annotations

from fastapi import Query

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class PageParams:
    """已归一化的分页参数"""

    __slots__ = ("page", "page_size")

    def __init__(self, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE):
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    def __repr__(self) -> str:  # pragma: no cover - 调试辅助
        return f"PageParams(page={self.page}, page_size={self.page_size})"


def page_params(
    page: int = Query(default=1, ge=1, description="页码，从 1 开始"),
    pageSize: int = Query(  # noqa: N803 契约字段名
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description="每页条数（契约字段）",
    ),
    page_size: int | None = Query(  # noqa: N803 兼容旧参数
        default=None,
        ge=1,
        le=MAX_PAGE_SIZE,
        include_in_schema=False,
        description="兼容旧参数，等价于 pageSize",
    ),
) -> PageParams:
    """解析分页参数，优先使用契约字段 pageSize。"""
    size = page_size if page_size is not None else pageSize
    return PageParams(page=page, page_size=size)