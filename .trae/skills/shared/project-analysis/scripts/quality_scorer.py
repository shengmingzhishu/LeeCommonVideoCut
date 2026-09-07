"""
Quality Scorer - 质量评分器
评估代码质量，包括文档完整性、测试覆盖率、代码规范、安全性等
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class QualityReport:
    """质量报告"""
    scores: Dict[str, float]
    overall_score: float
    grade: str
    suggestions: List[Tuple[str, str]]

    def to_dict(self) -> Dict[str, any]:
        """转换为字典"""
        return {
            "scores": {k: round(v, 2) for k, v in self.scores.items()},
            "overall_score": round(self.overall_score, 2),
            "grade": self.grade,
            "suggestions": list(self.suggestions),
        }


class QualityScorer:
    """代码质量评分器"""

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
    }

    def __init__(self, project_path: Path):
        """
        初始化评分器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)

    def assess(self) -> QualityReport:
        """评估代码质量"""
        # 各维度评分
        scores = {}

        # 1. 代码组织评分
        scores["organization"] = self._score_organization()

        # 2. 文档完整性评分
        scores["documentation"] = self._score_documentation()

        # 3. 测试覆盖率评分
        scores["testing"] = self._score_testing()

        # 4. 代码规范评分
        scores["code_style"] = self._score_code_style()

        # 5. 安全性评分
        scores["security"] = self._score_security()

        # 6. 可维护性评分
        scores["maintainability"] = self._score_maintainability()

        # 综合评分
        overall = sum(scores.values()) / len(scores)

        # 等级评定
        grade = self._grade_from_score(overall)

        # 生成改进建议
        suggestions = self._generate_suggestions(scores)

        return QualityReport(
            scores=scores,
            overall_score=overall,
            grade=grade,
            suggestions=suggestions,
        )

    def _score_organization(self) -> float:
        """评分：代码组织结构（0-5分）"""
        score = 5.0

        # 检查1：是否有清晰的目录结构
        src_dirs = ["src", "app", "lib", "common", "components", "pages"]
        if not any((self.project_path / d).exists() or self._has_dir_in_tree(d) for d in src_dirs):
            score -= 1.0

        # 检查2：是否分离关注点
        if (self.project_path / "src").exists():
            # 检查是否过于扁平
            all_files = list((self.project_path / "src").rglob("*.*"))
            if len(all_files) > 50:
                # 统计顶层目录数量
                top_dirs = set(f.parent.name for f in all_files)
                if len(top_dirs) < 3:
                    score -= 0.5

        # 检查3：是否有配置文件
        config_files = [".eslintrc.js", "tsconfig.json", "pyproject.toml", "pom.xml"]
        if not any((self.project_path / cf).exists() for cf in config_files):
            score -= 0.5

        return max(0.0, score)

    def _score_documentation(self) -> float:
        """评分：文档完整性（0-5分）"""
        score = 0.0

        # 检查 README
        readme_files = ["README.md", "README.rst", "README.txt"]
        for readme in readme_files:
            if (self.project_path / readme).exists():
                score += 2.0
                # 检查 README 完整性
                try:
                    readme_content = (self.project_path / readme).read_text().lower()
                    has_install = any(kw in readme_content for kw in ["安装", "install", "getting started", "quick start"])
                    has_usage = any(kw in readme_content for kw in ["使用", "usage", "how to use"])

                    if has_install:
                        score += 1.0
                    if has_usage:
                        score += 1.0
                except Exception:
                    pass
                break

        # 检查文档目录
        if (self.project_path / "docs").exists() or (self.project_path / "documentation").exists():
            score += 1.0

        # 检查 API 文档
        api_docs = ["API.md", "api.md", "docs/api.md"]
        if any((self.project_path / doc).exists() for doc in api_docs):
            score += 0.5

        # 检查代码注释（简化）
        total_files = 0
        commented_files = 0

        for ext in [".js", ".jsx", ".ts", ".tsx", ".py", ".java"]:
            for file_path in self.project_path.rglob(f"*{ext}"):
                if any(d in str(file_path) for d in self.DEFAULT_IGNORE_DIRS):
                    continue

                total_files += 1
                try:
                    content = file_path.read_text(encoding="utf-8")
                    # 简单的注释检测
                    has_comment = any(pattern in content
                                     for pattern in ["#", "//", "/**", "<!--"])
                    if has_comment:
                        commented_files += 1
                except Exception:
                    pass

        if total_files > 0:
            comment_ratio = commented_files / total_files
            score += min(1.0, comment_ratio * 2)  # 最高1分，需要50%的文件有注释

        return min(5.0, score)

    def _score_testing(self) -> float:
        """评分：测试覆盖率（0-5分）"""
        score = 0.0

        # 查找测试文件
        test_patterns = [
            "*test*.py",
            "*_test.py",
            "*.test.ts",
            "*.test.js",
            "*_test.go",
            "*Test.java",
        ]

        test_files = []
        for pattern in test_patterns:
            test_files.extend(self.project_path.rglob(pattern))

        if test_files:
            score += 2.0

            # 计算测试文件比例
            source_files = []
            for ext in [".js", ".jsx", ".ts", ".tsx", ".py", ".go", ".java"]:
                source_files.extend(self.project_path.rglob(f"*{ext}"))

            if source_files:
                test_ratio = len(test_files) / len(source_files)
                score += min(3.0, test_ratio * 15)  # 比例>20%得满分

        # 检查测试框架配置文件
        test_configs = [
            "jest.config.js",
            "vitest.config.ts",
            "pytest.ini",
            "junit.xml",
        ]
        if any((self.project_path / cf).exists() for cf in test_configs):
            score += 1.0

        return min(5.0, score)

    def _score_code_style(self) -> float:
        """评分：代码规范（0-5分）"""
        score = 5.0

        # 检查1：代码格式化工具
        formatters = [
            ".prettierrc",
            "prettier.config.js",
            ".eslintrc.js",
            ".eslintrc.json",
            "eslint.config.js",
            "pyproject.toml",  # 可能包含 black/isort 配置
            "setup.cfg",  # 可能包含 flake8/mypy 配置
        ]

        if not any((self.project_path / f).exists() for f in formatters):
            score -= 1.5

        # 检查2：命名规范一致性
        # JavaScript/TypeScript
        js_files = list(self.project_path.rglob("*.js")) + list(self.project_path.rglob("*.jsx")) + \
                   list(self.project_path.rglob("*.ts")) + list(self.project_path.rglob("*.tsx"))

        if js_files:
            # 简化：只检查是否混用蛇形命名和驼峰命名
            snake_case_files = []
            camel_case_files = []

            for file_path in js_files[:50]:  # 限制检查数量
                if any(d in str(file_path) for d in self.DEFAULT_IGNORE_DIRS):
                    continue
                try:
                    if "_" in file_path.name:
                        snake_case_files.append(file_path.name)
                    else:
                        camel_case_files.append(file_path.name)
                except Exception:
                    pass

            # 如果同时存在两种命名风格，说明不统一
            if snake_case_files and camel_case_files:
                score -= 1.0

        # 检查3：文件长度合理性
        max_file_lines = 0
        long_files = 0

        for ext in [".js", ".jsx", ".ts", ".tsx", ".py", ".java"]:
            for file_path in self.project_path.rglob(f"*{ext}"):
                if any(d in str(file_path) for d in self.DEFAULT_IGNORE_DIRS):
                    continue

                try:
                    lines = len(file_path.read_text(encoding="utf-8").splitlines())
                    max_file_lines = max(max_file_lines, lines)
                    if lines > 1000:
                        long_files += 1
                except Exception:
                    pass

        if max_file_lines > 2000:
            score -= 1.0
        elif long_files > 5:
            score -= 0.5

        return max(0.0, score)

    def _score_security(self) -> float:
        """评分：安全性（0-5分）"""
        score = 5.0

        # 检查1：硬编码密钥
        sensitive_patterns = [
            r'api[_-]?key\s*=\s*[\'"][^\'"]+[\'"]',
            r'api[_-]?secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'token\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret[_-]?key\s*=\s*[\'"][^\'"]+[\'"]',
            r'aws[_-]?access[_-]?key\s*=\s*[\'"][^\'"]+[\'"]',
            r'aws[_-]?secret[_-]?key\s*=\s*[\'"][^\'"]+[\'"]',
        ]

        security_issues = 0

        for ext in [".js", ".jsx", ".ts", ".tsx", ".py", ".java", ".go"]:
            for file_path in self.project_path.rglob(f"*{ext}"):
                if any(d in str(file_path) for d in self.DEFAULT_IGNORE_DIRS):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                    for pattern in sensitive_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            security_issues += 1
                            break
                except Exception:
                    pass

        # 扣分规则
        if security_issues > 0:
            score -= min(2.0, security_issues * 0.5)

        # 检查2：SQL 注入风险
        sql_patterns = [
            r"SELECT.*FROM.*WHERE.*['\"]\s*\+",
            r"INSERT.*INTO.*VALUES.*['\"]\s*\+",
            r"UPDATE.*SET.*['\"]\s*\+",
            r"DELETE.*FROM.*WHERE.*[\'\"]\s*\+",
        ]

        # 检查 SQL 注入风险
        sql_issues = 0

        for ext in [".js", ".jsx", ".ts", ".tsx", ".py", ".java", ".go"]:
            for file_path in self.project_path.rglob(f"*{ext}"):
                if any(d in str(file_path) for d in self.DEFAULT_IGNORE_DIRS):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                    for pattern in sql_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            sql_issues += 1
                            break
                except Exception:
                    pass

        if sql_issues > 0:
            score -= min(1.5, sql_issues * 0.5)

        # 检查3：.env 文件是否提交到了版本库（简化检查）
        # 实际场景中应该检查 .git 历史，这里简化为检查 .env 文件大小和内容
        if (self.project_path / ".env").exists():
            try:
                env_content = (self.project_path / ".env").read_text()
                # 如果 .env 包含真实的密钥
                if "=" in env_content and len([line for line in env_content.split("\n")
                                              if line.strip() and not line.startswith("#")]) > 0:
                    score -= 1.0
            except Exception:
                pass

        return max(0.0, score)

    def _score_maintainability(self) -> float:
        """评分：可维护性（0-5分）"""
        score = 5.0

        # 检查1：函数长度
        max_lines = 0
        complex_files = 0

        # JavaScript/TypeScript 函数检测
        js_files = list(self.project_path.rglob("*.js")) + list(self.project_path.rglob("*.jsx"))

        for file_path in js_files[:100]:  # 限制检查数量
            if any(d in str(file_path) for d in self.DEFAULT_IGNORE_DIRS):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()

                # 简化的检测：查找大括号块
                for i, line in enumerate(lines):
                    if "{" in line:
                        # 查找对应的 }
                        brace_count = 1
                        j = i + 1
                        while j < len(lines) and brace_count > 0:
                            brace_count += lines[j].count("{") - lines[j].count("}")
                            j += 1

                        block_length = j - i
                        if block_length > 50:
                            max_lines = max(max_lines, block_length)
                            if block_length > 100:
                                complex_files += 1
            except Exception:
                pass

        # Python 函数检测
        py_files = list(self.project_path.rglob("*.py"))

        for file_path in py_files[:100]:
            if any(d in str(file_path) for d in self.DEFAULT_IGNORE_DIRS):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()

                # 检测函数定义
                for i, line in enumerate(lines):
                    if line.strip().startswith("def ") and ":" in line:
                        # 检测缩进级别
                        indent = len(line) - len(line.lstrip())

                        # 查找函数结束
                        j = i + 1
                        while j < len(lines):
                            if lines[j].strip() and (len(lines[j]) - len(lines[j].lstrip())) <= indent:
                                break
                            if j - i > 0 and ":" in lines[j] and (len(lines[j]) - len(lines[j].lstrip())) <= indent:
                                break
                            j += 1

                        function_length = j - i
                        if function_length > 50:
                            max_lines = max(max_lines, function_length)
                            if function_length > 100:
                                complex_files += 1
            except Exception:
                pass

        # 扣分
        if max_lines > 150:
            score -= 1.5
        elif max_lines > 100:
            score -= 1.0

        if complex_files > 10:
            score -= 1.0
        elif complex_files > 5:
            score -= 0.5

        # 检查2：循环复杂度（简化：检测嵌套层级）
        max_depth = 0

        for file_path in list(self.project_path.rglob("*.js"))[:50] + list(self.project_path.rglob("*.py"))[:50]:
            if any(d in str(file_path) for d in self.DEFAULT_IGNORE_DIRS):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                for line in content.splitlines():
                    # 统计缩进级别
                    indent = len(line) - len(line.lstrip())
                    depth = indent // 4  # 假设4个空格为一个缩进
                    max_depth = max(max_depth, depth)
            except Exception:
                pass

        if max_depth > 8:
            score -= 1.0
        elif max_depth > 5:
            score -= 0.5

        return max(0.0, score)

    def _grade_from_score(self, score: float) -> str:
        """将分数转换为等级"""
        if score >= 4.5:
            return "A"
        elif score >= 4.0:
            return "A-"
        elif score >= 3.5:
            return "B"
        elif score >= 3.0:
            return "B-"
        elif score >= 2.5:
            return "C"
        else:
            return "D"

    def _generate_suggestions(self, scores: Dict[str, float]) -> List[Tuple[str, str]]:
        """根据评分生成改进建议"""
        suggestions = []

        if scores.get("organization", 0) < 3.0:
            suggestions.append((
                "高",
                "改进代码组织：建议使用清晰的目录结构（如 MVC、分层架构）分离关注点"
            ))

        if scores.get("documentation", 0) < 2.5:
            suggestions.append((
                "高",
                "完善文档：为项目添加 README.md，包含安装、使用说明；为公共API添加文档注释"
            ))

        if scores.get("testing", 0) < 2.5:
            suggestions.append((
                "高",
                "增加测试：建立测试框架，提升测试覆盖率至 80% 以上；为关键功能编写单元测试"
            ))

        if scores.get("code_style", 0) < 3.0:
            suggestions.append((
                "中",
                "统一代码风格：配置代码格式化工具（如 Prettier、Black），规范中文注释与命名"
            ))

        if scores.get("security", 0) < 3.5:
            suggestions.append((
                "高",
                "修复安全问题：移除硬编码密钥，使用环境变量；修复 SQL 注入漏洞；使用参数化查询"
            ))

        if scores.get("maintainability", 0) < 3.0:
            suggestions.append((
                "中",
                "提高可维护性：拆分过长函数，控制循环复杂度；提取公共逻辑，减少代码重复"
            ))

        return suggestions

    def _has_dir_in_tree(self, dir_name: str) -> bool:
        """检查项目中是否存在特定目录"""
        return dir_name in str(self.project_path).lower()
