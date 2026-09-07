---
name: target-system-integration
version: "1.0.0"
lastUpdated: "2026-09-03"
description: "适用于 ai-eval-server 项目接入新被测系统场景：按照标准化流程将新的 LLM 服务、RAG 系统、MCP 工具服务器等接入评测框架，实现配置驱动切换，对上层透明。"
user-invocable: true
---

# 被测系统接入

## 技能目标

当需要在 ai-eval-server 中**接入一个新的被测系统**（如新的 LLM 提供商、RAG 服务、MCP Server 等）时，使用本技能。

本技能提供标准化的接入流程，确保新系统通过配置驱动即可切换，无需修改上层业务逻辑。

## 适用场景

- 接入新的 LLM 提供商（如从 OpenAI 切换到 Anthropic、本地 Ollama 等）
- 接入 RAG 系统作为评测对象
- 接入 MCP 工具服务器进行工具调用评测
- 接入自定义的 HTTP/gRPC 评测后端

## 前置依赖

- 已阅读 `rules/project/01-project-specific.md` §3.2（被测系统接入规则）
- 已了解现有 `managers/target_manager.py` 的实现模式
- 目标系统的 API 文档或接口规范已确认

## 接入步骤

### 第 1 步：分析目标系统接口

在开始编码前，先整理以下信息：

```markdown
## 目标系统分析

### 基本信息
- 系统名称：
- 系统类型：LLM / RAG / MCP / 自定义 HTTP / gRPC
- API 基础 URL：
- 认证方式：API Key / OAuth / None / Other

### 接口清单
| 接口路径 | 方法 | 用途 | 关键参数 | 返回格式 |
|---------|------|------|---------|---------|

### 特殊约束
- 速率限制：
- 超时要求：
- 异常码映射：
- 与现有系统的差异点：
```

### 第 2 步：在 models/ 中定义配置 Schema

```python
# models/schemas/target_system.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class TargetType(str, Enum):
    """被测系统类型。"""
    LLM = "llm"                  # 大语言模型
    RAG = "rag"                  # RAG 系统
    MCP = "mcp"                  # MCP 工具服务器
    CUSTOM_HTTP = "custom_http"  # 自定义 HTTP 服务
    # 新增类型在此扩展...


class AuthConfig(BaseModel):
    """认证配置。"""
    auth_type: Literal["api_key", "oauth", "none"] = "api_key"
    api_key: Optional[str] = Field(None, description="API Key")
    api_key_header: str = "Authorization"
    oauth_token_url: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


class TargetSystemConfig(BaseModel):
    """被测系统配置。"""
    name: str = Field(..., description="系统名称，唯一标识")
    target_type: TargetType = Field(..., description="系统类型")
    base_url: str = Field(..., description="API 基础 URL")
    auth: AuthConfig = Field(default_factory=AuthConfig)
    timeout: int = Field(30, description="请求超时秒数")
    max_retries: int = Field(3, description="最大重试次数")
    extra_params: dict = Field(default_factory=dict, description="扩展参数")

    model_config = {"extra": "allow"}
```

### 第 3 步：在 models/ 中实现客户端封装

```python
# models/clients/base_client.py
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import httpx

from ..schemas.target_system import TargetSystemConfig, AuthConfig


class BaseTargetClient(ABC):
    """被测系统客户端基类。"""

    def __init__(self, config: TargetSystemConfig):
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=self._build_auth_headers(config.auth),
        )

    def _build_auth_headers(self, auth: AuthConfig) -> Dict[str, str]:
        """根据认证配置构建请求头。"""
        headers = {"Content-Type": "application/json"}
        if auth.auth_type == "api_key" and auth.api_key:
            headers[auth.api_key_header] = f"Bearer {auth.api_key}"
        return headers

    @abstractmethod
    async def call(self, payload: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        调用被测系统。

        Args:
            payload: 请求载荷
            **kwargs: 扩展参数

        Returns:
            系统响应字典

        Raises:
            TargetConnectionError: 连接失败
            TargetResponseError: 响应解析失败或业务错误
        """
        ...

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """带重试的 HTTP 请求。"""
        last_exception = None

        for attempt in range(self._config.max_retries):
            try:
                start_time = time.monotonic()
                response = await self._client.request(method, path, json=json_data)
                latency = int((time.monotonic() - start_time) * 1000)

                # 记录调用日志（含事务 ID）
                LOGGER.info(
                    f"[tx:{_get_tx_id()}] Target {self._config.name} "
                    f"{method} {path} → {response.status_code} ({latency}ms)"
                )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                last_exception = e
                if e.response.status_code >= 500 and attempt < self._config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                    continue
                raise TargetResponseError(
                    f"{self._config.name} 返回错误: {e.response.status_code}",
                    status_code=e.response.status_code,
                ) from e

            except httpx.ConnectError as e:
                last_exception = e
                if attempt < self._config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise TargetConnectionError(
                    f"无法连接 {self._config.name}: {e}"
                ) from e

        raise TargetConnectionError(
            f"{self._config.name} 请求失败，已耗尽重试次数: {last_exception}"
        ) from last_exception

    async def close(self):
        """关闭客户端连接。"""
        await self._client.aclose()
```

实现具体客户端：

```python
# models/clients/llm_client.py
class LlmClient(BaseTargetClient):
    """LLM 被测系统客户端。"""

    async def call(self, payload: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        调用 LLM 接口。

        Args:
            payload 必须包含：
            - messages: list[dict] 对话消息
            - model: str 模型名称
            - temperature: float (可选)
            - max_tokens: int (可选)
        """
        # 参数校验
        if "messages" not in payload:
            raise ValueError("LLM 请求缺少 messages 字段")

        request_payload = {
            "model": payload.get("model", "default"),
            "messages": payload["messages"],
            "temperature": payload.get("temperature", 0.7),
            "max_tokens": payload.get("max_tokens", 2048),
        }

        return await self._request_with_retry("POST", "/v1/chat/completions", json_data=request_payload)
```

### 第 4 步：在 managers/ 中注册路由

扩展现有 `target_manager.py`：

```python
# managers/target_manager.py
from typing import Dict, Optional
from ..models.clients.base_client import BaseTargetClient
from ..models.clients.llm_client import LlmClient
from ..models.schemas.target_system import TargetSystemConfig, TargetType


class TargetManager:
    """
    被测系统管理器。

    职责：
    - 根据配置创建和管理被测系统客户端
    - 按名称路由请求到对应系统
    - 对上层透明屏蔽底层差异
    """

    def __init__(self):
        self._clients: Dict[str, BaseTargetClient] = {}
        self._configs: Dict[str, TargetSystemConfig] = {}
        self._client_factory = {
            TargetType.LLM: LlmClient,
            # TargetType.RAG: RagClient,       # 未来扩展
            # TargetType.MCP: McpClient,        # 未来扩展
            # TargetType.CUSTOM_HTTP: HttpClient, # 未来扩展
        }

    async def register(self, config: TargetSystemConfig) -> None:
        """
        注册被测系统。

        Args:
            config: 系统配置

        Raises:
            ValueError: 系统类型不支持或名称重复
        """
        if config.name in self._clients:
            raise ValueError(f"被测系统 '{config.name}' 已存在")

        client_class = self._client_factory.get(config.target_type)
        if not client_class:
            raise ValueError(f"不支持的系统类型: {config.target_type}")

        client = client_class(config)
        self._clients[config.name] = client
        self._configs[config.name] = config

        LOGGER.info(f"[tx:{_get_tx_id()}] Registered target system: {config.name} ({config.target_type.value})")

    async def get_client(self, name: str) -> BaseTargetClient:
        """
        获取指定名称的客户端。

        Raises:
            KeyError: 系统未注册
        """
        if name not in self._clients:
            raise KeyError(f"被测系统 '{name}' 未注册，可用系统: {list(self._clients.keys())}")
        return self._clients[name]

    async def call(self, target_name: str, payload: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        路由请求到指定被测系统。

        Args:
            target_name: 系统名称（对应配置中的 name）
            payload: 请求载荷

        Returns:
            系统响应
        """
        client = await self.get_client(target_name)
        return await client.call(payload, **kwargs)

    async def close_all(self):
        """关闭所有客户端连接。"""
        for name, client in self._clients.items():
            try:
                await client.close()
                LOGGER.debug(f"[tx:{_get_tx_id()}] Closed client: {name}")
            except Exception as e:
                LOGGER.warning(f"[tx:{_get_tx_id()}] Error closing {name}: {e}")

    @property
    def registered_names(self) -> list[str]:
        """已注册的系统名称列表。"""
        return list(self._clients.keys())
```

### 第 5 步：数据库持久化（可选）

如果需要持久化配置到数据库：

```python
# models/entities/target_system.py
from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class TargetSystemEntity(Base):
    __tablename__ = "target_system"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False, comment="系统名称")
    target_type = Column(String(32), nullable=False, comment="系统类型")
    base_url = Column(String(512), nullable=False, comment="API 地址")
    auth_config = Column(JSON, comment="认证配置")
    extra_params = Column(JSON, comment="扩展参数")
    is_active = Column(Integer, default=1, comment="是否启用: 0-禁用 1-启用")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(64), comment="创建人")
```

### 第 6 步：验证

```bash
# 1. 单元测试
pytest tests/models/test_clients/ -v
pytest tests/managers/test_target_manager.py -v

# 2. 手动验证：通过 API 注册并调用
# 注册系统
curl -X POST http://localhost:8000/api/target-systems \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_llm_provider",
    "target_type": "llm",
    "base_url": "https://api.example.com",
    "auth": {"auth_type": "api_key", "api_key": "sk-test"}
  }'

# 调用测试
curl -X POST http://localhost:8000/api/eval/run \
  -H "Authorization: Bearer <token>" \
  -d '{"target_name": "my_llm_provider", ...}'
```

## 检查清单

- [ ] 目标系统接口分析文档已完成
- [ ] 配置 Schema 定义完整，包含校验规则
- [ ] 客户端继承 `BaseTargetClient`，实现了 `call()` 方法
- [ ] 客户端支持超时、重试、错误码映射
- [ ] 日志包含事务 ID、系统名称、耗时、状态码
- [ ] `TargetManager` 已注册新类型的工厂方法
- [ ] 如需持久化，ORM Entity 已定义
- [ ] 单元测试覆盖正常/异常/重试场景
- [ ] 未修改 Service 层或 Controller 层现有逻辑

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 注册时提示"不支持的系统类型" | `_client_factory` 未注册新类型 | 在 `TargetManager.__init__` 中添加映射 |
| 请求超时无重试 | 直接用了 `httpx` 而非 `_request_with_retry` | 使用基类提供的重试方法 |
| 日志缺少事务 ID | 手动创建了 `httpx.Client` 而非使用基类 | 继承 `BaseTargetClient` 并使用其封装 |
| 配置无法保存到数据库 | 缺少对应的 Repository 层 | 参考 `models/entities/` 下已有实体实现 |

## 非目标

- 不修改现有被测系统的客户端实现
- 不改动评测流程编排逻辑（eval_manager.py）
- 不涉及前端配置页面的 UI 开发
