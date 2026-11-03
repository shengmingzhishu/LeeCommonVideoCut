"""
配置服务（全局配置 + 用户级配置 + 测试连接）
============================================
- 全局配置：user_id = GLOBAL_SCOPE（空字符串）
- 用户级配置：user_id = <用户 id>，优先级高于全局
"""
from __future__ import annotations

import time

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.config import Config, GLOBAL_SCOPE
from app.schemas import ConfigResponse

DEFAULT_BASE_URLS = {
    "minimax": "https://api.minimaxi.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
}
DEFAULT_MODELS = {
    "minimax": "MiniMax-M3",
    "deepseek": "deepseek-chat",
}


class ConfigService:
    """配置读写与连接测试"""

    def __init__(self, db: Session):
        self.db = db

    # ---------- 查询 ----------

    def list_effective(self, user_id: str) -> list[ConfigResponse]:
        """返回用户可见配置：全局打底，用户级覆盖"""
        rows = (
            self.db.execute(
                select(Config).where(Config.user_id.in_([GLOBAL_SCOPE, user_id]))
            )
            .scalars()
            .all()
        )
        merged: dict[str, Config] = {r.key: r for r in rows if r.user_id == GLOBAL_SCOPE}
        merged.update({r.key: r for r in rows if r.user_id == user_id})
        return [self._to_response(merged[k]) for k in sorted(merged)]

    def get_effective(self, key: str, user_id: str) -> ConfigResponse:
        """获取单个配置（用户级优先，其次全局）"""
        row = self._find(key, user_id) or self._find(key, GLOBAL_SCOPE)
        if not row:
            raise NotFoundError(f"配置不存在: {key}", code="CONF_404_001")
        return self._to_response(row)

    def list_global(self) -> list[ConfigResponse]:
        """管理员：全局配置列表"""
        rows = (
            self.db.execute(select(Config).where(Config.user_id == GLOBAL_SCOPE))
            .scalars()
            .all()
        )
        return [self._to_response(r) for r in sorted(rows, key=lambda x: x.key)]

    # ---------- 写入 ----------

    def set_config(
        self, key: str, value: dict, description: str | None, *, user_id: str
    ) -> ConfigResponse:
        """设置配置（user_id 传 GLOBAL_SCOPE 表示全局）"""
        row = self._find(key, user_id)
        if row:
            row.value = value
            row.description = description
        else:
            row = Config(key=key, user_id=user_id, value=value, description=description)
            self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_response(row)

    def delete_user_config(self, key: str, user_id: str) -> None:
        """删除用户级配置（恢复为全局生效）"""
        row = self._find(key, user_id)
        if not row:
            raise NotFoundError(f"用户配置不存在: {key}", code="CONF_404_002")
        self.db.delete(row)
        self.db.commit()

    # ---------- 测试连接 ----------

    @staticmethod
    def test_connection(
        provider: str, api_key: str, base_url: str | None, model: str | None
    ) -> tuple[bool, str, int | None]:
        """测试外部服务连接

        Returns:
            (success, message, latency_ms)
        """
        start = time.perf_counter()
        try:
            if provider == "bing_search":
                resp = httpx.get(
                    "https://api.bing.microsoft.com/v7.0/search",
                    params={"q": "test", "count": 1},
                    headers={"Ocp-Apim-Subscription-Key": api_key},
                    timeout=15.0,
                )
            else:
                base = (base_url or DEFAULT_BASE_URLS.get(provider) or "").rstrip("/")
                payload = {
                    "model": model or DEFAULT_MODELS.get(provider, ""),
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 4,
                }
                resp = httpx.post(
                    f"{base}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                    timeout=15.0,
                )
            latency = int((time.perf_counter() - start) * 1000)
            if resp.status_code == 200:
                return True, "连接成功", latency
            return False, f"HTTP {resp.status_code}: {resp.text[:160]}", latency
        except Exception as e:  # noqa: BLE001 - 对外部服务的任何失败都转成测试结果
            latency = int((time.perf_counter() - start) * 1000)
            return False, f"连接失败: {type(e).__name__}: {str(e)[:160]}", latency

    # ---------- 内部 ----------

    def _find(self, key: str, user_id: str) -> Config | None:
        return self.db.get(Config, (key, user_id))

    @staticmethod
    def _to_response(row: Config) -> ConfigResponse:
        return ConfigResponse(
            key=row.key,
            user_id=None if row.user_id == GLOBAL_SCOPE else row.user_id,
            value=row.value,
            description=row.description,
            updated_at=row.updated_at,
        )
