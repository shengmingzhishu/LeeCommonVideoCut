"""
配置路由
========
- GET    /api/configs          我的配置列表（全局 + 用户级合并）
- POST   /api/configs/test     测试连接
- GET    /api/configs/{key}    获取单个配置（用户级优先）
- PUT    /api/configs/{key}    设置我的配置
- DELETE /api/configs/{key}    删除我的配置（恢复全局）
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas import (
    ApiResponse,
    ConfigResponse,
    ConfigTestRequest,
    ConfigTestResult,
    ConfigUpdateRequest,
)
from app.services.config_service import ConfigService

router = APIRouter(prefix="/configs", tags=["Configs"])


@router.get("", response_model=ApiResponse[list[ConfigResponse]])
def list_configs(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """我的配置列表（全局配置打底，用户级覆盖）"""
    return ApiResponse(data=ConfigService(db).list_effective(user.id))


@router.post("/test", response_model=ApiResponse[ConfigTestResult])
def test_connection(
    req: ConfigTestRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """测试外部服务连接（验证 API Key）"""
    ok, msg, latency = ConfigService.test_connection(
        req.provider, req.api_key, req.base_url, req.model
    )
    return ApiResponse(data=ConfigTestResult(success=ok, message=msg, latency_ms=latency))


@router.get("/{key}", response_model=ApiResponse[ConfigResponse])
def get_config(
    key: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """获取单个配置（用户级优先，其次全局）"""
    return ApiResponse(data=ConfigService(db).get_effective(key, user.id))


@router.put("/{key}", response_model=ApiResponse[ConfigResponse])
def set_config(
    key: str,
    req: ConfigUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """设置我的配置"""
    svc = ConfigService(db)
    return ApiResponse(
        data=svc.set_config(key, req.value, req.description, user_id=user.id), msg="已保存"
    )


@router.delete("/{key}", response_model=ApiResponse[None])
def delete_config(
    key: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """删除我的配置（恢复全局配置）"""
    ConfigService(db).delete_user_config(key, user.id)
    return ApiResponse(msg="已删除")
