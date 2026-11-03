"""
网络搜索管理器
==============
搜索引擎：Bing（有 API Key 时）→ DuckDuckGo（免 key 兜底）。
搜索结果仅用于给 AI 提供参考素材，抓取正文有长度上限与超时保护。
"""
from __future__ import annotations

import re
import urllib.parse

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

SEARCH_TIMEOUT = 15.0
FETCH_TIMEOUT = 15.0
MAX_CONTENT_CHARS = 2000


class SearchManager:
    """搜索引擎封装（Bing / DuckDuckGo）"""

    def __init__(self) -> None:
        self.engine = settings.search_engine

    def search(self, query: str, count: int = 3) -> list[dict[str, str]]:
        """搜索并抓取正文

        Args:
            query: 搜索关键词
            count: 返回条数

        Returns:
            [{"title": ..., "url": ..., "content": ...}]
        """
        if not query.strip():
            return []

        if self.engine == "bing" and settings.bing_search_key:
            results = self._search_bing(query, count)
            if results:
                return results
            logger.warning("Bing 搜索无结果，降级到 DuckDuckGo")

        return self._search_duckduckgo(query, count)

    def _search_bing(self, query: str, count: int) -> list[dict[str, str]]:
        """Bing Web Search API"""
        url = "https://api.bing.microsoft.com/v7.0/search"
        params = {"q": query, "mkt": "zh-CN", "count": count}
        headers = {"Ocp-Apim-Subscription-Key": settings.bing_search_key}

        try:
            with httpx.Client(timeout=SEARCH_TIMEOUT, headers=headers) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.warning(f"Bing 搜索失败: {type(e).__name__}", extra={"error": str(e)[:200]})
            return []

        results = []
        for item in data.get("webPages", {}).get("value", [])[:count]:
            url = item.get("url", "")
            results.append(
                {
                    "title": item.get("name", ""),
                    "url": url,
                    "content": self.fetch_content(url) if url else "",
                }
            )
        return results

    def _search_duckduckgo(self, query: str, count: int) -> list[dict[str, str]]:
        """DuckDuckGo HTML 端点（免 key）"""
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}

        try:
            with httpx.Client(timeout=SEARCH_TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
                resp = client.post(url, data=params)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            logger.warning(f"DuckDuckGo 搜索失败: {type(e).__name__}", extra={"error": str(e)[:200]})
            return []

        results: list[dict[str, str]] = []
        for item in soup.select(".result")[:count]:
            link = item.select_one(".result__a")
            if not link:
                continue
            href = link.get("href", "")
            # DuckDuckGo 用 uddg 参数包装真实 URL
            if "uddg=" in href:
                parsed = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed.query)
                real_url = qs.get("uddg", [""])[0]
            else:
                real_url = href

            title = link.get_text(strip=True)
            results.append(
                {
                    "title": title,
                    "url": real_url,
                    "content": self.fetch_content(real_url) if real_url else "",
                }
            )
        return results

    def fetch_content(self, url: str) -> str:
        """抓取文章正文（剔除脚本/导航等噪声，限长）"""
        if not url.startswith(("http://", "https://")):
            return ""

        try:
            with httpx.Client(timeout=FETCH_TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
                resp = client.get(url)
                resp.raise_for_status()
                resp.encoding = resp.encoding or "utf-8"
                soup = BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            logger.debug(f"正文抓取失败: {type(e).__name__}", extra={"url": url[:100]})
            return ""

        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        text = "\n".join(p for p in paragraphs if len(p) > 10)
        if not text:
            text = soup.get_text(" ", strip=True)

        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[:MAX_CONTENT_CHARS]
