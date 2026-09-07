"""
Architecture Analyzer - 架构分析器
分析项目目录结构、识别架构模式、核心模块、设计模式
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class ModuleInfo:
    """模块信息"""
    name: str
    path: str
    files: List[Dict[str, any]]
    total_lines: int
    total_size_kb: float

    def to_dict(self) -> Dict[str, any]:
        """转换为字典"""
        return {
            "name": self.name,
            "path": self.path,
            "file_count": len(self.files),
            "total_lines": self.total_lines,
            "total_size_kb": self.total_size_kb,
        }


@dataclass
class ArchitectureInfo:
    """架构信息"""
    pattern: str
    modules: Dict[str, ModuleInfo]
    design_patterns: List[str]
    organization_score: float
    tree: Dict[str, any]
    total_files: int
    total_lines: int
    total_size_kb: float

    def to_dict(self) -> Dict[str, any]:
        """转换为字典"""
        return {
            "pattern": self.pattern,
            "modules": {name: module.to_dict() for name, module in self.modules.items()},
            "design_patterns": self.design_patterns,
            "organization_score": round(self.organization_score, 2),
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "total_size_kb": round(self.total_size_kb, 2),
        }


class ArchitectureAnalyzer:
    """架构分析器"""

    # 默认忽略的目录
    DEFAULT_IGNORE_DIRS = {
        "node_modules",
        ".git",
        ".idea",
        ".vscode",
        "dist",
        "build",
        "__pycache__",
        "venv",
        "venvs",
        "env",
        ".venv",
        "target",
        ".next",
        ".nuxt",
        "vendor",
        "bin",
        "obj",
        "out",
        ".cache",
        "coverage",
    }

    # 默认忽略的文件扩展名
    DEFAULT_IGNORE_EXTS = {
        ".log",
        ".tmp",
        ".bak",
        ".zip",
        ".tar",
        ".gz",
        ".lock",
        ".pyc",
        ".pyo",
        ".class",
        ".jar",
        ".war",
        ".ear",
        ".swp",
        ".DS_Store",
    }

    # 架构模式识别
    ARCHITECTURE_PATTERNS = {
        "MVC": {"/models/", "model", "/views/", "view", "/controllers/", "controller"},
        "Micro-Frontend": {"apps/", "packages/", "/packages/", "/apps/"},
        "Monorepo": {"packages/", "apps/", "/packages/", "/apps/"},
        "12-Factor App": {"app/", "/app/", "config/", "/config/", "public/", "/public/"},
        "Next.js": {"app/", "pages/", "components/", "public/", "/app/", "/pages/"},
        "Nuxt.js": {"pages/", "components/", "layouts/", "middleware/", "/pages/"},
        "React Native": {"src/", "_src/", "android/", "ios/", "/android/", "/ios/"},
        "Rails": {"app/", "/app/", "db/", "/db/", "public/", "/public/", "test/", "/test/"},
        "Flask": {"app/", "static/", "templates/", "/app/", "/static/"},
        "Django": {"/manage.py", "apps/", "migrations/", "/apps/"},
        "Express": {"routes/", "controllers/", "models/", "/routes/"},
        "Vue CLI": {"src/", "public/", "tests/", "/src/", "/public/"},
    }

    # 设计模式代码识别
    DESIGN_PATTERN_REGEX = {
        "Singleton": [
            r"getInstance\s*\(",
            r"instance\s*=\s*null",
            r"private\s+static\s+\w+\s+instance",
        ],
        "Singleton-Thread-Safe": [
            r"synchronized\s+getInstance",
            r"getInstance\s*\([^)]*\)\s*\{[^}]*synchronized",
        ],
        "Factory": [
            r"create[A-Z]\w*Factory",
            r"factory\s*=\s*new\s+\w+Factory",
            r"\.create[A-Z]\w*\(",
        ],
        "Builder": [
            r"Builder\(",
            r"\.build\(",
            r"builder\s*\.\w+\.\w+\(\)",
        ],
        "Observer": [
            r"addObserver\s*\(",
            r"addEventListener\s*\(",
            r".emit\(",
            r".trigger\(",
            r".dispatch\(",
            r"on\s*:\s*\w+",
            r"\.subscribe\s*\(",
            r".on\([\"\']\w+[\"\']\)",
        ],
        "Pub-Sub": [
            r"pubsub\s*\.publish",
            r"pubsub\s*\.subscribe",
            r"EventEmitter",
            r".on\([\"\'][a-zA-Z]+[\"\']\)",
        ],
        "Decorator": [
            r"@\w+",
            r"@\w+\([^)]*\)",
        ],
        "Strategy": [
            r"Strategy\s*=\s*\w+",
            r"setStrategy\s*\(",
        ],
        "Adapter": [
            r"Adapter",
            r"adapt\s*\(",
        ],
        "Proxy": [
            r"Proxy\s*=",
            r"new\s+Proxy\s*\(",
        ],
        "Command": [
            r"Command\s*=",
            r"execute\s*\(",
        ],
    }

    def __init__(self, project_path: Path):
        """
        初始化分析器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self.ignore_dirs = self.DEFAULT_IGNORE_DIRS.copy()
        self.ignore_exts = self.DEFAULT_IGNORE_EXTS.copy()

    def analyze(self) -> ArchitectureInfo:
        """分析项目架构"""
        # 1. 构建目录树
        tree = self._build_tree()

        # 2. 识别架构模式
        pattern = self._detect_pattern(tree)

        # 3. 分析模块
        modules = self._analyze_modules(tree)

        # 4. 识别设计模式
        design_patterns = self._detect_design_patterns()

        # 5. 评分
        organization_score = self._score_organization(tree)

        # 6. 统计
        total_files, total_lines, total_size_kb = self._calculate_totals(tree)

        return ArchitectureInfo(
            pattern=pattern,
            modules=modules,
            design_patterns=design_patterns,
            organization_score=organization_score,
            tree=tree,
            total_files=total_files,
            total_lines=total_lines,
            total_size_kb=total_size_kb,
        )

    def _build_tree(self) -> Dict[str, any]:
        """构建目录树"""
        tree = {}

        # 使用栈来构建树形结构
        for item in self.project_path.rglob("*"):
            # 跳过忽略的目录
            if item.is_dir() and item.name in self.ignore_dirs:
                continue

            # 跳过忽略的扩展名
            if item.is_file() and item.suffix in self.ignore_exts:
                continue

            # 计算相对路径
            try:
                relative_path = str(item.relative_to(self.project_path))
            except ValueError:
                # 超出项目根目录，跳过
                continue

            parts = relative_path.split("/")

            # 构建嵌套字典
            current = tree
            for i, part in enumerate(parts[:-1]):
                current = current.setdefault(part, {})

            last_part = parts[-1]

            if item.is_file():
                # 收集文件信息
                try:
                    lines = len(item.read_text(encoding="utf-8").splitlines())
                except:
                    lines = 0

                # 记录文件
                current[last_part] = {
                    "type": "file",
                    "extension": item.suffix if item.suffix else "unknown",
                    "lines": lines,
                    "size_kb": item.stat().st_size / 1024,
                    "path": relative_path,
                }

        return tree

    def _detect_pattern(self, tree: Dict[str, any]) -> str:
        """识别架构模式"""
        tree_str = str(tree).lower()

        for pattern_name, indicators in self.ARCHITECTURE_PATTERNS.items():
            matches = 0
            for indicator in indicators:
                if indicator.lower() in tree_str:
                    matches += 1
                    if matches >= 2:  # 至少匹配两个指标
                        return pattern_name

        # 特殊检查：检查是否是前端项目
        if "src" in tree:
            if "components" in tree["src"]:
                if "app" in tree["src"] or "pages" in tree["src"]:
                    return "Next.js/Nuxt.js-like"

        return "Custom"

    def _analyze_modules(self, tree: Dict[str, any]) -> Dict[str, ModuleInfo]:
        """分析模块"""
        modules = {}

        # 遍历第一层目录作为模块
        for key, value in tree.items():
            # 只处理目录
            if isinstance(value, dict) and any(isinstance(v, dict)["type"] != "file"
                                              for v in value.values() if isinstance(v, dict)):
                # 提取模块文件
                files = self._extract_files(value, key)

                if files:
                    total_lines = sum(f["lines"] for f in files)
                    total_size_kb = sum(f["size_kb"] for f in files)

                    modules[key] = ModuleInfo(
                        name=key,
                        path=key,
                        files=files,
                        total_lines=total_lines,
                        total_size_kb=total_size_kb,
                    )

        return modules

    def _extract_files(self, node: Dict[str, any], prefix: str) -> List[Dict[str, any]]:
        """提取模块中的所有文件"""
        files = []

        for key, value in node.items():
            if isinstance(value, dict):
                if value.get("type") == "file":
                    # 这是一个文件
                    files.append(value)
                else:
                    # 这是一个目录，递归提取
                    files.extend(self._extract_files(value, f"{prefix}/{key}"))

        return files

    def _detect_design_patterns(self) -> List[str]:
        """识别设计模式"""
        patterns_found = set()

        # 遍历源代码文件
        for ext in [".js", ".jsx", ".ts", ".tsx", ".py", ".java", ".go", ".rb"]:
            for file_path in self.project_path.rglob(f"*{ext}"):
                if any(dir_name in str(file_path) for dir_name in self.ignore_dirs):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                    self._scan_for_patterns(content, patterns_found)
                except:
                    pass

        return sorted(list(patterns_found))

    def _scan_for_patterns(self, content: str, patterns_found: Set[str]):
        """扫描代码中的设计模式"""
        for pattern_name, regex_list in self.DESIGN_PATTERN_REGEX.items():
            for regex in regex_list:
                if re.search(regex, content, re.MULTILINE):
                    # 转换模式名称为更友好的形式
                    friendly_name = pattern_name.replace("-Thread-Safe", " (Thread-Safe)")
                    patterns_found.add(friendly_name)
                    break

    def _score_organization(self, tree: Dict[str, any]) -> float:
        """评分：代码组织结构（0-5分）"""
        score = 5.0

        # 检查1：是否有清晰的目录结构
        if not any(d in tree for d in ["src", "app", "lib", "common", "components", "pages"]):
            score -= 1.0

        # 检查2：检查是否过于扁平
        first_level_files = sum(1 for v in tree.values()
                               if isinstance(v, dict) and v.get("type") == "file")
        if first_level_files > 20:
            score -= 1.5

        # 检查3：检查是否有合理的分离
        has_components = "components" in str(tree).lower()
        has_utils = "utils" in str(tree).lower() or "utilities" in str(tree).lower()
        has_tests = "test" in str(tree).lower() or "spec" in str(tree).lower()

        if not has_components and not (has_utils or "lib" in str(tree).lower()):
            score -= 1.0

        if not has_tests:
            score -= 0.5

        return max(0.0, score)

    def _calculate_totals(self, tree: Dict[str, any]) -> tuple:
        """计算总文件数、总行数、总大小"""
        def count_files(node):
            file_count = 0
            total_lines = 0
            total_size = 0.0

            for value in node.values():
                if isinstance(value, dict):
                    if value.get("type") == "file":
                        file_count += 1
                        total_lines += value.get("lines", 0)
                        total_size += value.get("size_kb", 0)
                    else:
                        # 递归
                        fc, tl, ts = count_files(value)
                        file_count += fc
                        total_lines += tl
                        total_size += ts

            return file_count, total_lines, total_size

        return count_files(tree)
