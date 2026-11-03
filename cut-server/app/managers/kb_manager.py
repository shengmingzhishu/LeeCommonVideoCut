"""
知识库管理器
============
扫描 intro_dir 下的文本文件，构建简单 KB（按文件存储为 markdown 块）。
参考旧 `AI漫剧剪辑师旧参考项目代码/app/services/kb.py` 的思路。
"""
from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()

SUPPORTED_TEXT_EXT = {".txt", ".md", ".markdown", ".rst"}


class KBManager:
    """知识库管理器（简化版：直接扫描文本文件，按内容 hash 去重）"""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.workdir = settings.workdir_abs

    @property
    def kb_path(self) -> Path:
        """知识库产物路径"""
        path = self.workdir / self.project_id / "kb"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def build(
        self,
        *,
        title: str,
        author: str,
        intro: str,
        intro_dir: str | None,
        relearn: bool = False,
    ) -> dict:
        """构建知识库

        Returns:
            {
              "kb_path": str,   # 知识库根目录绝对路径
              "doc_count": int, # 扫描到的文本文件数
              "relearned": bool # 是否重新学习（强制刷新）
            }
        """
        kb_root = self.kb_path
        marker = kb_root / ".build_marker"

        # 已构建且非 relearn：直接返回
        if marker.exists() and not relearn:
            doc_count = sum(1 for _ in kb_root.rglob("*") if _.is_file() and _.suffix in SUPPORTED_TEXT_EXT)
            logger.info(
                "知识库已存在，跳过构建",
                extra={"project_id": self.project_id, "doc_count": doc_count},
            )
            return {"kb_path": str(kb_root), "doc_count": doc_count, "relearned": False}

        # 清空旧（注意：先写 marker 再写内容，不要反）
        if relearn:
            for f in kb_root.rglob("*"):
                if f.is_file():
                    f.unlink()

        # 写入元信息
        meta = kb_root / "meta.md"
        meta.write_text(
            f"# {title}\n\n**作者**: {author}\n\n**简介**: {intro}\n\n",
            encoding="utf-8",
        )

        # 扫描用户资料目录
        doc_count = 1  # meta.md 算一份
        if intro_dir:
            src = Path(intro_dir)
            if src.is_dir():
                for f in src.rglob("*"):
                    if f.is_file() and f.suffix.lower() in SUPPORTED_TEXT_EXT:
                        rel = f.relative_to(src)
                        dst = kb_root / "docs" / rel
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        dst.write_text(f.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                        doc_count += 1

        # 写 marker（必须最后写，因为前面 relearn 会把文件删了）
        marker_path = kb_root / ".build_marker"
        marker_path.write_text(
            f"built_at={doc_count}\n",
            encoding="utf-8",
        )

        logger.info(
            "知识库构建完成",
            extra={"project_id": self.project_id, "doc_count": doc_count, "relearned": relearn},
        )
        return {"kb_path": str(kb_root), "doc_count": doc_count, "relearned": bool(relearn)}

    def get_context_for_ai(self, max_chars: int = 8000) -> str:
        """组装 KB 内容（用于 AI prompt，限长 max_chars）"""
        kb_root = self.kb_path
        if not kb_root.exists():
            return ""

        parts: list[str] = []
        total = 0
        for f in sorted(kb_root.rglob("*.md")):
            content = f.read_text(encoding="utf-8", errors="ignore")
            chunk = f"\n\n## {f.name}\n\n{content}"
            if total + len(chunk) > max_chars:
                parts.append(chunk[: max_chars - total] + "\n\n[...truncated]")
                break
            parts.append(chunk)
            total += len(chunk)

        return "".join(parts)
