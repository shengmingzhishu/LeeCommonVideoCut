"""
Tech Stack Detector - 技术栈识别器
识别项目的语言、框架、构建工具、测试框架等
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class TechStackInfo:
    """技术栈信息"""
    language: str
    package_manager: str
    framework: str
    build_tool: str
    test_framework: List[str]
    has_documentation: bool
    main_entry: Optional[str] = None
    config_files: List[str] = None

    def to_dict(self) -> Dict[str, any]:
        """转换为字典"""
        return {
            "language": self.language,
            "package_manager": self.package_manager,
            "framework": self.framework,
            "build_tool": self.build_tool,
            "test_framework": self.test_framework,
            "has_documentation": self.has_documentation,
            "main_entry": self.main_entry,
            "config_files": self.config_files,
        }


class TechStackDetector:
    """技术栈检测器"""

    # 文件扩展名到编程语言的映射
    EXTENSION_MAP = {
        "py": "Python",
        "js": "JavaScript",
        "jsx": "JavaScript/React",
        "ts": "TypeScript",
        "tsx": "TypeScript/React",
        "java": "Java",
        "kt": "Kotlin",
        "rs": "Rust",
        "go": "Go",
        "rb": "Ruby",
        "php": "PHP",
        "cs": "C#",
        "cpp": "C++",
        "c": "C",
        "swift": "Swift",
        "dart": "Dart",
        "vue": "Vue.js",
        "svelte": "Svelte",
    }

    # 配置文件特征
    CONFIG_PATTERNS = {
        "package.json": ("JavaScript/TypeScript", "Node.js"),
        "tsconfig.json": ("TypeScript", None),
        "pom.xml": ("Java", "Maven"),
        "build.gradle": ("Java", "Gradle"),
        "requirements.txt": ("Python", "pip"),
        "pyproject.toml": ("Python", "poetry"),
        "setup.py": ("Python", " setuptools"),
        "Cargo.toml": ("Rust", "cargo"),
        "go.mod": ("Go", "go modules"),
        "composer.json": ("PHP", "composer"),
        "Gemfile": ("Ruby", "bundler"),
    }

    # 框架特征
    FRAMEWORK_PATTERNS = {
        # JavaScript/TypeScript 框架
        "react": ["react", "react-dom", "@types/react"],
        "vue": ["vue", "@vue/*"],
        "angular": ["@angular/", "angular"],
        "svelte": ["svelte"],
        "next": ["next", "next-auth"],
        "nuxt": ["nuxt"],
        "express": ["express", "express-"],
        "nest": ["@nestjs/", "nest"],
        # Python 框架
        "django": ["django"],
        "flask": ["flask"],
        "fastapi": ["fastapi"],
        # Java 框架
        "spring": ["spring-boot", "springframework"],
    }

    # 构建工具特征
    BUILD_TOOL_PATTERNS = {
        "vite": ["vite"],
        "webpack": ["webpack", "webpack-cli"],
        "rollup": ["rollup"],
        "esbuild": ["esbuild"],
        "parcel": ["parcel"],
    }

    # 测试框架特征
    TEST_FRAMEWORK_PATTERNS = {
        "jest": ["jest", "@types/jest"],
        "vitest": ["vitest"],
        "mocha": ["mocha"],
        "pytest": ["pytest"],
        "junit": ["junit", "jupiter"],
        "vitest": ["vitest"],
    }

    def __init__(self, project_path: Path):
        """
        初始化检测器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self.config_files = self._scan_config_files()
        self.language_distribution = self._analyze_file_extensions()

    def detect(self) -> TechStackInfo:
        """检测技术栈"""
        # 1. 识别主要语言
        language = self._detect_language()

        # 2. 识别包管理工具
        package_manager = self._detect_package_manager(language)

        # 3. 识别框架
        framework = self._detect_framework(language)

        # 4. 识别构建工具
        build_tool = self._detect_build_tool(language)

        # 5. 识别测试框架
        test_framework = self._detect_test_framework(language)

        # 6. 检查文档
        has_documentation = self._check_documentation()

        # 7. 识别主入口
        main_entry = self._detect_main_entry()

        return TechStackInfo(
            language=language,
            package_manager=package_manager,
            framework=framework,
            build_tool=build_tool,
            test_framework=test_framework,
            has_documentation=has_documentation,
            main_entry=main_entry,
            config_files=self.config_files,
        )

    def _scan_config_files(self) -> List[str]:
        """扫描配置文件"""
        config_files = []

        common_configs = [
            "package.json",
            "tsconfig.json",
            "vue.config.js",
            "vite.config.js",
            "webpack.config.js",
            "pom.xml",
            "build.gradle",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "Cargo.toml",
            "go.mod",
            "composer.json",
            "Gemfile",
            ".eslintrc.js",
            ".prettierrc",
            "jest.config.js",
            "vitest.config.js",
        ]

        for config in common_configs:
            if (self.project_path / config).exists():
                config_files.append(config)

        return config_files

    def _analyze_file_extensions(self) -> Dict[str, int]:
        """分析文件扩展名分布"""
        extensions = {}

        for ext, lang in self.EXTENSION_MAP.items():
            count = len(list(self.project_path.rglob(f"*.{ext}")))
            if count > 0:
                extensions[lang] = count

        return extensions

    def _detect_language(self) -> str:
        """检测主要编程语言"""
        if not self.language_distribution:
            return "unknown"

        # 返回文件数最多的语言
        language = max(self.language_distribution, key=self.language_distribution.get)
        return language

    def _detect_package_manager(self, language: str) -> str:
        """检测包管理工具"""
        package_managers = []

        # Node.js
        if (self.project_path / "package-lock.json").exists():
            package_managers.append("npm")
        if (self.project_path / "yarn.lock").exists():
            package_managers.append("yarn")
        if (self.project_path / "pnpm-lock.yaml").exists():
            package_managers.append("pnpm")

        if package_managers:
            return " / ".join(package_managers)

        # Python
        if (self.project_path / "requirements.txt").exists():
            return "pip"
        if (self.project_path / "poetry.lock").exists():
            return "poetry"
        if (self.project_path / "Pipfile").exists():
            return "pipenv"

        # Java
        if (self.project_path / "pom.xml").exists():
            return "Maven"
        if (self.project_path / "build.gradle").exists():
            return "Gradle"

        # Rust
        if (self.project_path / "Cargo.toml").exists():
            return "cargo"

        # Go
        if (self.project_path / "go.mod").exists():
            return "go modules"

        # PHP
        if (self.project_path / "composer.json").exists():
            return "composer"

        # Ruby
        if (self.project_path / "Gemfile").exists():
            return "bundler"

        return "unknown"

    def _detect_framework(self, language: str) -> str:
        """检测框架"""
        frameworks = []

        if language in ["JavaScript", "TypeScript", "JavaScript/React", "TypeScript/React"]:
            pkg_json = self.project_path / "package.json"
            if pkg_json.exists():
                try:
                    data = json.loads(pkg_json.read_text())
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    for framework, patterns in self.FRAMEWORK_PATTERNS.items():
                        for pattern in patterns:
                            if any(pattern in dep for dep in deps.keys()):
                                frameworks.append(framework.capitalize())
                                break
                except Exception:
                    pass

        elif language == "Python":
            req_txt = self.project_path / "requirements.txt"
            if req_txt.exists():
                content = req_txt.read_text().lower()
                if "django" in content:
                    frameworks.append("Django")
                if "flask" in content:
                    frameworks.append("Flask")
                if "fastapi" in content:
                    frameworks.append("FastAPI")

        return frameworks[0] if frameworks else "unknown"

    def _detect_build_tool(self, language: str) -> str:
        """检测构建工具"""
        build_tools = []

        # JavaScript/TypeScript
        if language in ["JavaScript", "TypeScript", "JavaScript/React", "TypeScript/React"]:
            pkg_json = self.project_path / "package.json"
            if pkg_json.exists():
                try:
                    data = json.loads(pkg_json.read_text())
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    for tool, patterns in self.BUILD_TOOL_PATTERNS.items():
                        for pattern in patterns:
                            if any(pattern in dep for dep in deps.keys()):
                                build_tools.append(tool)
                                break
                except Exception:
                    pass

        return build_tools[0] if build_tools else "unknown"

    def _detect_test_framework(self, language: str) -> List[str]:
        """检测测试框架"""
        test_frameworks = []

        # JavaScript/TypeScript
        if language in ["JavaScript", "TypeScript", "JavaScript/React", "TypeScript/React"]:
            pkg_json = self.project_path / "package.json"
            if pkg_json.exists():
                try:
                    data = json.loads(pkg_json.read_text())
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    for framework, patterns in self.TEST_FRAMEWORK_PATTERNS.items():
                        for pattern in patterns:
                            if any(pattern in dep for dep in deps.keys()):
                                test_frameworks.append(framework.capitalize())
                                break
                except Exception:
                    pass

        # Python
        elif language == "Python":
            req_txt = self.project_path / "requirements.txt"
            if req_txt.exists():
                content = req_txt.read_text().lower()
                if "pytest" in content:
                    test_frameworks.append("PyTest")
                if "junit" in content or "unittest" in content:
                    test_frameworks.append("JUnit/Unittest")

        # Java
        elif language == "Java":
            pom_xml = self.project_path / "pom.xml"
            if pom_xml.exists():
                content = pom_xml.read_text().lower()
                if "junit" in content:
                    test_frameworks.append("JUnit")

        return test_frameworks

    def _check_documentation(self) -> bool:
        """检查是否有文档"""
        doc_files = ["README.md", "README.rst", "README.txt", "docs/"]
        return any((self.project_path / doc).exists() for doc in doc_files)

    def _detect_main_entry(self) -> Optional[str]:
        """检测主入口文件"""
        # Node.js
        if (self.project_path / "package.json").exists():
            try:
                data = json.loads((self.project_path / "package.json").read_text())
                return data.get("main")
            except Exception:
                pass

        # Python
        if (self.project_path / "main.py").exists():
            return "main.py"
        if (self.project_path / "app.py").exists():
            return "app.py"

        return None


# 工具函数
def detect_from_deps(deps: Dict[str, str], patterns: Dict[str, List[str]]) -> List[str]:
    """
    从依赖列表中检测匹配的模式

    Args:
        deps: 依赖字典 {name: version}
        patterns: 模式字典 {name: [pattern_list]}

    Returns:
        匹配到的名称列表
    """
    matches = []

    for name, pattern_list in patterns.items():
        for pattern in pattern_list:
            if any(pattern in dep for dep in deps.keys()):
                matches.append(name)
                break

    return matches
