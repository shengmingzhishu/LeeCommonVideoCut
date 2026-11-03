"""
Local Project Analyzer - 主分析器
协调所有分析模块，执行完整的分析流程
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

# 添加 scripts 目录到 Python 路径
SCRIPT_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from tech_detector import TechStackDetector
except ImportError:
    TechStackDetector = None

try:
    from arch_analyzer import ArchitectureAnalyzer
except ImportError:
    ArchitectureAnalyzer = None

try:
    from dep_analyzer import DependencyAnalyzer
except ImportError:
    DependencyAnalyzer = None

try:
    from quality_scorer import QualityScorer
except ImportError:
    QualityScorer = None

try:
    from best_practices import BestPracticesAdvisor
except ImportError:
    BestPracticesAdvisor = None

from output_manager import OutputManager


class AnalysisResult:
    """分析结果容器"""

    def __init__(
        self,
        project_name: str,
        output_summary: Dict[str, Any],
        artifacts: Dict[str, str],
        metadata: Dict[str, Any],
        tech_stack: Any = None,
        architecture: Any = None,
        dependencies: Any = None,
        quality: Any = None,
        best_practices: Any = None,
    ):
        self.project_name = project_name
        self.output_summary = output_summary
        self.artifacts = artifacts
        self.metadata = metadata
        self.tech_stack = tech_stack
        self.architecture = architecture
        self.dependencies = dependencies
        self.quality = quality
        self.best_practices = best_practices

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "project_name": self.project_name,
            "output_summary": self.output_summary,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
            "tech_stack": self.tech_stack.to_dict() if self.tech_stack else None,
            "architecture": self.architecture.to_dict() if self.architecture else None,
            "dependencies": self.dependencies.to_dict() if self.dependencies else None,
            "quality": self.quality.to_dict() if self.quality else None,
            "best_practices": [bp for bp in self.best_practices] if self.best_practices else None,
        }


class LocalProjectAnalyzer:
    """本地项目分析器"""

    # 默认忽略的目录
    DEFAULT_IGNORE_DIRS = [
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
    ]

    # 标志性文件（按优先级）
    MARKER_FILES = [
        "package.json",
        "pom.xml",
        "build.gradle",
        "requirements.txt",
        "pyproject.toml",
        "Cargo.toml",
        "go.mod",
        "composer.json",
        "Gemfile",
        ".git",
    ]

    def __init__(
        self,
        project_path: Optional[str] = None,
        focus_dir: Optional[str] = None,
        include_tests: bool = False,
        analysis_depth: str = "auto",
        output_dir: Optional[str] = None,
        overwrite: bool = False,
    ):
        """
        初始化分析器

        Args:
            project_path: 项目路径。如果为 None，自动检测当前目录
            focus_dir: 聚焦分析的子目录（如 src/）
            include_tests: 是否包含测试代码
            analysis_depth: 分析深度
            output_dir: 输出目录
            overwrite: 是否覆盖最新的分析（默认保留历史）
        """
        # 检测项目根目录
        if project_path is None:
            self.root_path = self._detect_project_root()
        else:
            self.root_path = Path(project_path).resolve()

        # 聚焦目录
        if focus_dir:
            self.focus_path = self.root_path / focus_dir
            if not self.focus_path.exists():
                raise ValueError(f"聚焦目录不存在: {focus_dir}")
        else:
            self.focus_path = self.root_path

        # 分析配置
        self.include_tests = include_tests
        self.analysis_depth = analysis_depth
        self.overwrite = overwrite

        # 初始化输出管理器
        self.output_mgr = OutputManager(
            project_root=self.root_path,
            output_dir=output_dir,
            overwrite=overwrite,
        )

        # 初始化各分析器
        self.tech_detector = TechStackDetector(self.focus_path) if TechStackDetector else None
        self.arch_analyzer = ArchitectureAnalyzer(self.focus_path) if ArchitectureAnalyzer else None
        self.dep_analyzer = DependencyAnalyzer(self.focus_path) if DependencyAnalyzer else None
        self.quality_scorer = QualityScorer(self.focus_path) if QualityScorer else None
        self.bp_advisor = BestPracticesAdvisor(self.focus_path) if BestPracticesAdvisor else None

        # 温和降级：根据模块可用性决定降级策略
        if TechStackDetector is None:
            print("警告: tech_detector 不可用，将跳过技术栈分析")
        if ArchitectureAnalyzer is None:
            print("警告: arch_analyzer 不可用，将跳过架构分析")
        if DependencyAnalyzer is None:
            print("警告: dep_analyzer 不可用，将跳过依赖分析")
        if QualityScorer is None:
            print("警告: quality_scorer 不可用，将跳过质量评分")
        if BestPracticesAdvisor is None:
            print("警告: best_practices 不可用，将跳过最佳实践建议")

        # 分析元数据
        self.metadata = {
            "project_name": self.root_path.name,
            "analysis_time": None,
            "analysis_duration": None,
            "analysis_depth": analysis_depth,
        }

    def _detect_project_root(self) -> Path:
        """自动检测项目根目录"""
        current = Path.cwd()

        # 向上搜索标志性文件
        for path in [current] + list(current.parents):
            for marker in self.MARKER_FILES:
                if (path / marker).exists():
                    return path

        # 如果没找到，返回当前目录
        print(f"提示: 未检测到标志性配置文件，使用当前目录作为项目根目录: {current}")
        return current

    def analyze(self) -> AnalysisResult:
        """执行完整分析"""
        start_time = datetime.now()

        print(f"📂 检测项目: {self.root_path}")
        print(f"🎯 聚焦目录: {self.focus_path.relative_to(self.root_path)}")

        # 步骤1: 技术栈识别
        if self.tech_detector:
            print("\n🔍 识别技术栈...")
            tech_stack = self.tech_detector.detect()
            print(f"✓ 语言: {tech_stack.language}")
            print(f"✓ 框架: {tech_stack.framework}")
        else:
            tech_stack = None

        # 步骤2: 架构分析
        if self.arch_analyzer:
            print("\n🏗️ 分析架构...")
            architecture = self.arch_analyzer.analyze()
            print(f"✓ 架构模式: {architecture.pattern}")
            print(f"✓ 模块数: {len(architecture.modules)}")
        else:
            architecture = None

        # 步骤3: 依赖分析
        if self.dep_analyzer:
            print("\n📦 分析依赖...")
            dependencies = self.dep_analyzer.analyze()
            print(f"✓ 依赖数: {len(dependencies.dependencies)}")
        else:
            dependencies = None

        # 步骤4: 质量评估
        if self.quality_scorer:
            print("\n📊 评估质量...")
            quality = self.quality_scorer.assess()
            print(f"✓ 综合评分: {quality.overall_score} ({quality.grade})")
        else:
            quality = None

        # 步骤5: 最佳实践建议
        if self.bp_advisor and tech_stack:
            print("\n💡 生成建议...")
            best_practices = self.bp_advisor.suggest(tech_stack, architecture)
            print(f"✓ 建议数: {len(best_practices)}")
        else:
            best_practices = []

        # 计算分析时间
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 更新元数据
        self.metadata["analysis_time"] = end_time.isoformat()
        self.metadata["analysis_duration"] = f"{duration:.1f}s"

        # 步骤6: 生成报告产物
        print("\n📝 生成报告...")
        artifacts = self._generate_artifacts(
            tech_stack=tech_stack,
            architecture=architecture,
            dependencies=dependencies,
            quality=quality,
            best_practices=best_practices,
        )

        print(f"\n✅ 分析完成！耗时: {duration:.1f}s")
        print(f"\n📁 输出目录: {self.output_mgr.current_output_dir}")
        print(f"\n生成文件:")
        for name, path in artifacts.items():
            file_size = Path(path).stat().st_size / 1024
            print(f"  • {name} ({file_size:.1f} KB)")

        return AnalysisResult(
            project_name=self.root_path.name,
            output_summary=self.output_mgr.get_output_summary(),
            artifacts=artifacts,
            metadata=self.metadata,
            tech_stack=tech_stack,
            architecture=architecture,
            dependencies=dependencies,
            quality=quality,
            best_practices=best_practices,
        )

    def _generate_artifacts(
        self,
        tech_stack: Any = None,
        architecture: Any = None,
        dependencies: Any = None,
        quality: Any = None,
        best_practices: List = None,
    ) -> Dict[str, str]:
        """生成所有分析产物"""
        artifacts = {}

        # 1. 生成元数据
        metadata_content = self._generate_metadata(tech_stack, quality)
        self.output_mgr.write_artifact("metadata.json", metadata_content)
        artifacts["metadata"] = str(self.output_mgr.current_output_dir / "metadata.json")

        # 2. 生成主报告
        if tech_stack or architecture or quality:
            report_content = self._generate_report(tech_stack, architecture, dependencies, quality, best_practices)
            self.output_mgr.write_artifact("README.md", report_content)
            artifacts["report"] = str(self.output_mgr.current_output_dir / "README.md")

        # 3. 生成依赖图
        if dependencies:
            self.output_mgr.write_artifact("dependencies.mmd", dependencies.graph_mermaid)
            artifacts["dependencies_mmd"] = str(self.output_mgr.current_output_dir / "dependencies.mmd")

            # 尝试渲染 PNG（如果 mermaid-cli 可用）
            try:
                import subprocess

                result = subprocess.run(
                    ["mmdc", "-i", str(self.output_mgr.current_output_dir / "dependencies.mmd"),
                     "-o", str(self.output_mgr.current_output_dir / "dependencies.png")],
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    artifacts["dependencies_png"] = str(self.output_mgr.current_output_dir / "dependencies.png")
                else:
                    print("提示: mermaid-cli 不可用，未渲染依赖图 PNG")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                print("提示: mermaid-cli 不可用，未渲染依赖图 PNG")

        # 4. 生成快速索引
        if architecture:
            quick_index = self._generate_quick_index(architecture)
            self.output_mgr.write_artifact("quick-index.html", quick_index)
            artifacts["quick_index"] = str(self.output_mgr.current_output_dir / "quick-index.html")

        # 5. 生成最佳实践
        if best_practices:
            bp_content = self._generate_best_practices(best_practices)
            self.output_mgr.write_artifact("best-practices.md", bp_content)
            artifacts["best_practices"] = str(self.output_mgr.current_output_dir / "best-practices.md")

        # 6. 生成质量评分
        if quality:
            quality_content = self._generate_quality_score(quality)
            self.output_mgr.write_artifact("quality-score.md", quality_content)
            artifacts["quality_score"] = str(self.output_mgr.current_output_dir / "quality-score.md")

        # 7. 生成文件清单（简化版，不使用 Excel）
        if architecture:
            inventory_content = self._generate_file_inventory(architecture)
            self.output_mgr.write_artifact("file-inventory.md", inventory_content)
            artifacts["file_inventory"] = str(self.output_mgr.current_output_dir / "file-inventory.md")

        return artifacts

    def _generate_metadata(self, tech_stack: Any = None, quality: Any = None) -> str:
        """生成元数据 JSON"""
        metadata = {
            "project_name": self.root_path.name,
            "project_path": str(self.root_path),
            "analysis_time": self.metadata.get("analysis_time"),
            "analysis_duration": self.metadata.get("analysis_duration"),
            "focus_directory": str(self.focus_path.relative_to(self.root_path)),
        }

        if tech_stack:
            metadata["tech_stack"] = {
                "language": tech_stack.language,
                "framework": tech_stack.framework,
                "package_manager": tech_stack.package_manager,
                "build_tool": tech_stack.build_tool,
                "test_framework": tech_stack.test_framework,
            }

        if quality:
            metadata["quality"] = {
                "overall_score": round(quality.overall_score, 2),
                "grade": quality.grade,
                "scores": {k: round(v, 2) for k, v in quality.scores.items()},
            }

        return json.dumps(metadata, indent=2, ensure_ascii=False)

    def _generate_report(self, tech_stack, architecture, dependencies, quality, best_practices) -> str:
        """生成主报告 - 简化版"""
        lines = [
            f"# {self.root_path.name} - 项目分析报告",
            "",
            f"**生成时间：** {self.metadata.get('analysis_time')}",
            f"**分析时长：** {self.metadata.get('analysis_duration')}",
            "",
            "## 执行摘要",
            "",
            f"**项目名称：** {self.root_path.name}",
            f"**项目路径：** {self.root_path}",
            "",
        ]

        if tech_stack:
            lines.extend([
                "## 技术栈",
                "",
                f"- **语言：** {tech_stack.language}",
                f"- **框架：** {tech_stack.framework}",
                f"- **包管理工具：** {tech_stack.package_manager}",
                f"- **构建工具：** {tech_stack.build_tool}",
                "",
            ])

        if quality:
            lines.extend([
                "## 质量评分",
                "",
                f"**综合评分：** {quality.overall_score:.2f} ({quality.grade})",
                "",
                "| 维度 | 评分 |",
                "|------|------|",
            ])
            for dim, score in quality.scores.items():
                lines.append(f"| {dim} | {score:.2f} |")
            lines.append("")

        if best_practices:
            lines.extend([
                "## 最佳实践建议",
                "",
            ])
            for priority, suggestion in best_practices[:5]:  # 只显示前5条
                priority_icon = "🔴" if priority == "高" else "🟡" if priority == "中" else "🟢"
                lines.append(f"- {priority_icon} **{priority}优先级：** {suggestion}")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*此报告由 project-analysis 自动生成*")

        return "\n".join(lines)

    def _generate_quick_index(self, architecture) -> str:
        """生成快速索引 HTML"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.root_path.name} - 快速索引</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        input {{ padding: 10px; width: 100%; box-sizing: border-box; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>{self.root_path.name} - 快速索引</h1>
    <input type="text" id="searchInput" placeholder="搜索文件..." onkeyup="searchTable()">
    <table id="fileTable">
        <thead>
            <tr>
                <th>文件名</th>
                <th>类型</th>
                <th>行数</th>
                <th>大小 (KB)</th>
            </tr>
        </thead>
        <tbody>
"""

        # 简化：基于架构模块生成文件列表
        if hasattr(architecture, 'tree'):
            for module_name, module_info in architecture.modules.items():
                if isinstance(module_info, dict) and 'files' in module_info:
                    for file in module_info['files'][:20]:  # 限制显示数量
                        html += f"""
            <tr>
                <td>{file.get('path', module_name)}</td>
                <td>{file.get('extension', 'unknown')}</td>
                <td>{file.get('lines', 0)}</td>
                <td>{file.get('size_kb', 0):.2f}</td>
            </tr>
"""

        html += """
        </tbody>
    </table>

    <script>
        function searchTable() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toUpperCase();
            const table = document.getElementById('fileTable');
            const tr = table.getElementsByTagName('tr');

            for (let i = 1; i < tr.length; i++) {
                let td = tr[i].getElementsByTagName('td')[0];
                if (td) {
                    const txtValue = td.textContent || td.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = '';
                    } else {
                        tr[i].style.display = 'none';
                    }
                }
            }
        }
    </script>
</body>
</html>
"""
        return html

    def _generate_best_practices(self, best_practices: List) -> str:
        """生成最佳实践建议"""
        lines = [
            "# 最佳实践建议",
            "",
            f"**生成时间：** {self.metadata.get('analysis_time')}",
            "",
        ]

        # 按优先级分组
        high_priority = [bp for bp in best_practices if bp[0] == "高"]
        medium_priority = [bp for bp in best_practices if bp[0] == "中"]
        low_priority = [bp for bp in best_practices if bp[0] == "低"]

        if high_priority:
            lines.append("## 🔴 高优先级")
            lines.append("")
            for _, suggestion in high_priority:
                lines.append(f"- {suggestion}")
            lines.append("")

        if medium_priority:
            lines.append("## 🟡 中优先级")
            lines.append("")
            for _, suggestion in medium_priority:
                lines.append(f"- {suggestion}")
            lines.append("")

        if low_priority:
            lines.append("## 🟢 低优先级")
            lines.append("")
            for _, suggestion in low_priority:
                lines.append(f"- {suggestion}")
            lines.append("")

        return "\n".join(lines)

    def _generate_quality_score(self, quality) -> str:
        """生成质量评分卡"""
        lines = [
            "# 质量评分卡",
            "",
            f"**项目：** {self.root_path.name}",
            f"**生成时间：** {self.metadata.get('analysis_time')}",
            "",
            "## 综合评分",
            "",
            f"**评分：** {quality.overall_score:.2f} / 5.0",
            f"**等级：** **{quality.grade}**",
            "",
            "## 各维度评分",
            "",
            "| 维度 | 评分 | 说明 |",
            "|------|------|------|",
        ]

        descriptions = {
            "organization": "代码组织结构",
            "documentation": "文档完整性",
            "testing": "测试覆盖率",
            "code_style": "代码规范",
            "security": "安全性",
            "maintainability": "可维护性",
        }

        for dim, score in quality.scores.items():
            lines.append(f"| {descriptions.get(dim, dim)} | {score:.2f} | |")

        lines.append("")
        if quality.suggestions:
            lines.append("## 改进建议")
            lines.append("")
            for priority, suggestion in quality.suggestions:
                priority_icon = "🔴" if priority == "高" else "🟡" if priority == "中" else "🟢"
                lines.append(f"- {priority_icon} **{priority}优先级：** {suggestion}")
            lines.append("")

        return "\n".join(lines)

    def _generate_file_inventory(self, architecture) -> str:
        """生成文件清单"""
        lines = [
            "# 文件清单",
            "",
            f"**项目：** {self.root_path.name}",
            f"**生成时间：** {self.metadata.get('analysis_time')}",
            "",
            "## 模块统计",
            "",
            "| 模块名称 | 文件数 | 代码行数 |",
            "|---------|-------|---------|",
        ]

        if hasattr(architecture, 'modules'):
            for module_name, module_info in architecture.modules.items():
                if isinstance(module_info, dict):
                    file_count = len(module_info.get('files', []))
                    total_lines = sum(f.get('lines', 0) for f in module_info.get('files', []))
                    lines.append(f"| {module_name} | {file_count} | {total_lines} |")

        lines.append("")
        lines.append("## 核心文件")
        lines.append("")

        # 显示部分重要文件
        if hasattr(architecture, 'tree'):
            for module_name, module_info in architecture.modules.items():
                if isinstance(module_info, dict) and module_name in architecture.tree:
                    lines.append(f"### {module_name}")
                    lines.append("")
                    for file in module_info.get('files', [])[:10]:
                        lines.append(f"- `{file.get('path', '')}` ({file.get('lines', 0)} 行)")
                    if len(module_info.get('files', [])) > 10:
                        lines.append(f"*...还有 {len(module_info.get('files', [])) - 10} 个文件*")
                    lines.append("")

        return "\n".join(lines)


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="本地项目分析器")
    parser.add_argument("--project", "-p", help="项目路径（默认为当前目录）")
    parser.add_argument("--focus", "-f", help="聚焦分析的子目录（如 src/）")
    parser.add_argument("--include-tests", action="store_true", help="包含测试代码")
    parser.add_argument("--depth", "-d", choices=["auto", "quick", "standard", "deep"], default="auto",
                        help="分析深度（默认 auto）")
    parser.add_argument("--output", "-o", help="输出目录（默认 .project-analysis）")
    parser.add_argument("--overwrite", action="store_true", help="覆盖最新的分析（默认保留历史）")

    args = parser.parse_args()

    analyzer = LocalProjectAnalyzer(
        project_path=args.project,
        focus_dir=args.focus,
        include_tests=args.include_tests,
        analysis_depth=args.depth,
        output_dir=args.output,
        overwrite=args.overwrite,
    )

    result = analyzer.analyze()
    print(f"\n✓ 分析完成！产物保存在: {result.output_summary['current_dir']}")


if __name__ == "__main__":
    main()
