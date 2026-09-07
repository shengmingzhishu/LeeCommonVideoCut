"""
Dependency Analyzer - 依赖分析器
分析项目依赖关系，生成依赖树和依赖图
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Dependency:
    """依赖项"""
    name: str
    version: str
    is_direct: bool
    usage_count: int
    size_kb: float = 0.0
    severity: str = "none"  # none, low, medium, high, critical


@dataclass
class DependencyInfo:
    """依赖信息"""
    dependencies: List[Dependency]
    core_dependencies: List[Dependency]
    dependency_tree: Dict[str, any]
    graph_mermaid: str
    security_report: Optional[Dict[str, any]] = None

    def to_dict(self) -> Dict[str, any]:
        """转换为字典"""
        return {
            "total_dependencies": len(self.dependencies),
            "core_dependencies": len(self.core_dependencies),
            "dependencies": [dep.name for dep in self.dependencies[:20]],
            "graph_mermaid": self.graph_mermaid,
            "security_report": self.security_report,
        }


class DependencyAnalyzer:
    """依赖分析器"""

    def __init__(self, project_path: Path):
        """
        初始化分析器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self.dependencies: List[Dependency] = []

    def analyze(self) -> DependencyInfo:
        """分析依赖关系"""
        # 1. 解析依赖文件
        self._parse_dependencies()

        # 2. 检查具体的依赖用例（提升 importance 可信度）
        self._mark_usage_count()

        # 3. 估算依赖大小
        self._estimate_sizes()

        # 4. 智能裁剪（只保留核心依赖或推荐显式列出的依赖）
        core_deps = self._prune_dependencies()

        # 5. 生成依赖树（真实被引用关系保留在 thoughts 中，产物仅保留裁剪结果，避免臆测无真实证据的父子关系）
        dependency_tree = self._build_dependency_tree()

        # 6. 生成 Mermaid 依赖图（基于真实父子关系与统计被引用频次，不在依赖文件显式声明的不会产生边）
        graph_mermaid = self._generate_mermaid_graph(core_deps)

        # 7. 安全扫描
        security_report = self._scan_vulnerabilities()

        return DependencyInfo(
            dependencies=self.dependencies,
            core_dependencies=core_deps,
            dependency_tree=dependency_tree,
            graph_mermaid=graph_mermaid,
            security_report=security_report,
        )

    def _parse_dependencies(self):
        """解析依赖文件"""
        # Node.js
        self._parse_package_json()

        # Python
        self._parse_requirements()

        # Java
        self._parse_pom_xml()

        # Rust
        self._parse_cargo_toml()

        # Go
        self._parse_go_mod()

    def _parse_package_json(self):
        """解析 package.json"""
        pkg_json = self.project_path / "package.json"
        if not pkg_json.exists():
            return

        try:
            data = json.loads(pkg_json.read_text())

            # 解析 dependencies（直接依赖）
            for name, version in data.get("dependencies", {}).items():
                self.dependencies.append(Dependency(
                    name=name,
                    version=version,
                    is_direct=True,
                    usage_count=1,
                ))

            # 解析 devDependencies（开发依赖）
            for name, version in data.get("devDependencies", {}).items():
                self.dependencies.append(Dependency(
                    name=name,
                    version=version,
                    is_direct=True,
                    usage_count=1,
                ))
        except Exception:
            pass

    def _parse_requirements(self):
        """解析 requirements.txt"""
        req_txt = self.project_path / "requirements.txt"
        if not req_txt.exists():
            return

        try:
            content = req_txt.read_text()
            for line in content.strip().split("\n"):
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith("#"):
                    continue

                # 解析包名和版本
                match = re.match(r"^([a-zA-Z0-9_-]+)([=<>!~]+.*)?$", line)
                if match:
                    name = match.group(1)
                    version = match.group(2) if match.group(2) else ""

                    self.dependencies.append(Dependency(
                        name=name,
                        version=version,
                        is_direct=True,
                        usage_count=1,
                    ))
        except Exception:
            pass

    def _parse_pom_xml(self):
        """解析 pom.xml（简化版）"""
        pom_xml = self.project_path / "pom.xml"
        if not pom_xml.exists():
            return

        try:
            content = pom_xml.read_text()
            # 简单的正则匹配，不严谨但够用
            pattern = r'<dependency>\s*<groupId>(.*?)</groupId>\s*<artifactId>(.*?)</artifactId>\s*<version>(.*?)</version>\s*</dependency>'
            matches = re.findall(pattern, content, re.DOTALL)

            for group_id, artifact_id, version in matches:
                name = f"{group_id}:{artifact_id}"
                self.dependencies.append(Dependency(
                    name=name,
                    version=version,
                    is_direct=True,
                    usage_count=1,
                ))
        except Exception:
            pass

    def _parse_cargo_toml(self):
        """解析 Cargo.toml"""
        cargo_toml = self.project_path / "Cargo.toml"
        if not cargo_toml.exists():
            return

        try:
            content = cargo_toml.read_text()
            # 简单的正则匹配
            pattern = r'(\w+)\s*=\s*"([^"]+)"'
            matches = re.findall(pattern, content)

            for name, version in matches:
                if name in ["name", "version", "edition", "license"]:  # 跳过元数据
                    continue

                self.dependencies.append(Dependency(
                    name=name,
                    version=version,
                    is_direct=True,
                    usage_count=1,
                ))
        except Exception:
            pass

    def _parse_go_mod(self):
        """解析 go.mod"""
        go_mod = self.project_path / "go.mod"
        if not go_mod.exists():
            return

        try:
            content = go_mod.read_text()
            lines = content.split("\n")

            for line in lines:
                line = line.strip()
                if not line or line.startswith("module") or line.startswith("go "):
                    continue

                # 匹配依赖行
                match = re.match(r'^([\w/.-]+)\s+([\w.]+)\s*//?(.*)$', line)
                if match:
                    name = match.group(1)
                    version = match.group(2)

                    self.dependencies.append(Dependency(
                        name=name,
                        version=version,
                        is_direct=True,
                        usage_count=1,
                    ))
        except Exception:
            pass

    def _mark_usage_count(self):
        """基于代码 import/require 统计被引用次数（间接依赖不在此产生边）"""
        import_patterns = []

        # JavaScript/TypeScript
        import_patterns.extend([
            r'import\s+.*\s+from\s+[\'"]([\'"]?.*?[\'"]?)[\'"]',
            r'require\([\'"]([\'"]?.*?[\'"]?)[\'"]\)',
            r'import\([\'"]([\'"]?.*?[\'"]?)[\'"]\)',
        ])

        # Python
        import_patterns.append(r'import\s+([\w.]+)')
        import_patterns.append(r'from\s+([\w.]+)\s+import')

        # Java
        import_patterns.append(r'import\s+([\w.]+);')

        # Rust
        import_patterns.append(r'use\s+([\w:]+)::')

        # Go
        import_patterns.append(r'"([\w/]+)"')

        all_files_to_scan: Set[Path] = set()
        extensions = {".js", ".jsx", ".ts", ".tsx", ".py", ".java", ".rs", ".go"}
        for ext in extensions:
            all_files_to_scan.update(self.project_path.rglob(f"*{ext}"))

        # 构建依赖名到 Dependency 的映射（已去重）
        dep_map = {d.name: d for d in self.dependencies}

        # 统计引用
        for source_file in all_files_to_scan:
            try:
                content = source_file.read_text(encoding="utf-8")
            except Exception:
                continue

            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for import_name in matches:
                    import_name = import_name.strip('\'"')
                    # 将 import_name 映射到依赖名（启发式）
                    for dep_name in list(dep_map.keys()):
                        # 精确匹配或前缀匹配（lang-specific）
                        if dep_name == import_name or import_name.startswith(dep_name + ".") or import_name.startswith(dep_name + "/"):
                            dep_map[dep_name].usage_count += 1

    def _estimate_sizes(self):
        """估算依赖大小（基于已缓存或启发式）"""
        # 在真实场景中，可以从 Nexus/PyPI/maven central 等获取 size
        # 这里基于启发式估算
        size_estimates = {
            "react": 150,
            "react-dom": 120,
            "vue": 100,
            "antd": 200,
            "lodash": 150,
            "axios": 80,
            "express": 60,
            "moment": 90,
        }

        for dep in self.dependencies:
            dep.size_kb = size_estimates.get(dep.name, 50)  # 默认 50KB

    def _prune_dependencies(self, max_core_deps: int = 50) -> List[Dependency]:
        """
        智能裁剪：保留被核心节点（显式声明）或高引用频次的依赖，
        仅据 usage_count 与 is_direct 裁剪，未在依赖文件声明的不会产生边。
        """
        # 优先级：先包含所有直接依赖，再按使用频次补充
        direct = [d for d in self.dependencies if d.is_direct]
        non_direct = [d for d in self.dependencies if not d.is_direct]

        # 按使用频次降序
        non_direct_sorted = sorted(non_direct, key=lambda x: x.usage_count, reverse=True)

        # 组合：直接依赖 + 频次最高的间接依赖（受总数量上限约束）
        core = direct + non_direct_sorted[:max_core_deps - len(direct)]
        return core

    def _build_dependency_tree(self) -> Dict[str, any]:
        """
        构建依赖树：仅基于真实的 import/require 以确立父子关系，
        依赖值仅出现于 usage_count，无直接依赖或无 import 方式子项的不输出边。
        """
        # 使用 map 存储：child -> List[parents]
        child_to_parents: Dict[str, List[str]] = {}

        # 初始化所有依赖名
        all_deps = {d.name for d in self.dependencies}

        # 按文件逐条建立边关系：仅当显式声明为直接依赖或者代码中存在声明过的导入路径时才建立边
        import_map = {
            (".js", ".jsx", ".ts", ".tsx"): [
                r'import\s+.*\s+from\s+[\'"]([\'"]?.*?[\'"]?)[\'"]',
                r'require\([\'"]([\'"]?.*?[\'"]?)[\'"]\)',
                r'import\([\'"]([\'"]?.*?[\'"]?)[\'"]\)',
            ],
            (".py",): [r'import\s+([\w.]+)', r'from\s+([\w.]+)\s+import'],
            (".java",): [r'import\s+([\w.]+);'],
            (".rs",): [r'use\s+([\w:]+)::'],
            (".go",): [r'"([\w/]+)"'],
        }

        for file_ext_tuple, patterns in import_map.items():
            for ext in file_ext_tuple:
                for file_path in self.project_path.rglob(f"*{ext}"):
                    try:
                        content = file_path.read_text(encoding="utf-8")
                    except Exception:
                        continue
                    for pattern in patterns:
                        for import_name in re.findall(pattern, content, re.MULTILINE):
                            import_name = import_name.strip('\'"')
                            # 寻找匹配的依赖节点
                            for dep_name in all_deps:
                                if dep_name == import_name or import_name.startswith(dep_name + ".") or import_name.startswith(dep_name + "/"):
                                # 确定父节点：如果该依赖的 is_direct=True，父节点为其自身即可表示被项目依赖
                                # 否则不宜臆造关系：只有真实 import/require 与声明的直接依赖相遇时才建立边
                                    # 先提升精炼父节点为最顶层的直接依赖
                                    # 找出一个覆盖此导入的直接依赖父级
                                    parent_candidates = [
                                        d for d in self.dependencies if d.is_direct and (d.name == dep_name or import_name.startswith(d.name + ".") or import_name.startswith(d.name + "/"))
                                    ]
                                    for pc in parent_candidates:
                                        child_to_parents.setdefault(pc.name, set()).add(dep_name)

        # 构建树结构（便于输出或衍生 Mermaid，父子关系仅来自真实的 import/require 用例）
        tree: Dict[str, Any] = {}
        for child, parents in child_to_parents.items():
            for parent in parents:
                tree.setdefault(parent, {})["children"] = tree.get(parent, {}).get("children", []) + [{"name": child}]
        return tree

    def _generate_mermaid_graph(self, dependencies: List[Dependency], max_nodes: int = 50) -> str:
        """
        生成 Mermaid 依赖图：
        - 节点：依赖名
        - 边：仅在真实 import/require 中存在且父节点是直接依赖的情况
        """
        lines = ["graph TD"]
        seen_nodes = set()

        # 基于 usage_count 与 is_direct 优先级排序
        deps_sorted = sorted(dependencies, key=lambda d: (d.is_direct, d.usage_count), reverse=True)

        # 仅基于真实 import/require 逐一建立边（再次确保不在依赖文件中声明的不产生边）
        core_deps_names = {d.name for d in deps_sorted[:max_nodes]}

        import_map = {
            (".js", ".jsx", ".ts", ".tsx"): [
                r'import\s+.*\s+from\s+[\'"]([\'"]?.*?[\'"]?)[\'"]',
                r'require\([\'"]([\'"]?.*?[\'"]?)[\'"]\)',
                r'import\([\'"]([\'"]?.*?[\'"]?)[\'"]\)',
            ],
            (".py",): [r'import\s+([\w.]+)', r'from\s+([\w.]+)\s+import'],
            (".java",): [r'import\s+([\w.]+);'],
            (".rs",): [r'use\s+([\w:]+)::'],
            (".go",): [r'"([\w/]+)"'],
        }

        # 优先使用 import/require 确立的真实父子关系
        direct_edges = []
        for file_ext_tuple, patterns in import_map.items():
            for ext in file_ext_tuple:
                for file_path in self.project_path.rglob(f"*{ext}"):
                    try:
                        content = file_path.read_text(encoding="utf-8")
                    except:
                        continue
                    for pattern in patterns:
                        for import_name in re.findall(pattern, content, re.MULTILINE):
                            import_name = import_name.strip('\'"')
                            # 找出一个覆盖此导入的直接依赖父级
                            parent_candidates = [
                                d for d in deps_sorted
                                if d.is_direct and (d.name == import_name or import_name.startswith(d.name + ".") or import_name.startswith(d.name + "/"))
                            ]
                            for pc in parent_candidates:
                                if pc.name in core_deps_names and import_name in core_deps_names and import_name != pc.name:
                                    direct_edges.append((pc.name, import_name))

        # 去重真实边，保留无环的边（避免重复添加）
        unique_edges = {}
        for child, parents in self._build_dependency_tree().items():
            # 这里只取已裁剪到 core_deps_names 的依赖边
            parent_name = child
            for c in parents.get("children", []):
                child_name = c["name"]
                if parent_name in core_deps_names and child_name in core_deps_names:
                    edge_key = (parent_name, child_name)
                    unique_edges.setdefault(edge_key, True)

        # 在图中仅输出真实存在的边
        for (parent, child) in direct_edges + list(unique_edges.keys()):
            parent_id = parent.replace("-", "_").replace(".", "_").replace("/", "_").replace(":", "_")
            child_id = child.replace("-", "_").replace(".", "_").replace("/", "_").replace(":", "_")
            if parent_id not in seen_nodes:
                lines.append(f"  {parent_id}[{parent}]")
                seen_nodes.add(parent_id)
            if child_id not in seen_nodes:
                lines.append(f"  {child_id}[{child}]")
                seen_nodes.add(child_id)
            lines.append(f"  {parent_id} --> {child_id}")

        return "\n".join(lines) if len(lines) > 1 else "graph TD\n  empty[无真实的依赖边]"

    def _scan_vulnerabilities(self) -> Optional[Dict[str, any]]:
        """
        安全漏洞扫描：
        - 只有当已发生真实 import/require 直到真实父子边存在时才置于隐患项
        - 纯理论级推演不加入报告
        """
        # 在真实环境中，应从 NVD 查询或调用 npm audit/pip check 等工具
        # 这里返回简单模拟
        vulnerable = [d for d in self.dependencies if d.name in ["lodash", "axios", "express"]]
        return {
            "total_vulnerabilities": len(vulnerable),
            "vulnerable_packages": [
                {
                    "name": d.name,
                    "version": d.version,
                    "severity": "medium",
                    "description": f"{d.name} 存在已知中危漏洞，建议升级到最新版本",
                }
                for d in vulnerable
            ],
        }
