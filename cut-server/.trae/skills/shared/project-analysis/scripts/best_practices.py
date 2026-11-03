"""
Best Practices Advisor - 最佳实践建议生成器
基于项目特征和技术栈生成针对性的建议
"""

from pathlib import Path
from typing import List, Tuple, Any, Optional


class BestPracticesAdvisor:
    """最佳实践建议器"""

    # React 项目最佳实践
    REACT_BEST_PRACTICES = {
        "高": [
            "为列表渲染使用唯一且稳定的 key prop",
            "避免在渲染路径中创建新函数，使用 useCallback 优化",
            "使用 React.memo 优化组件性能",
            "正确使用 useEffect 依赖数组，包括所有外部变量",
            "避免直接修改 state，使用 setState 的函数形式",
        ],
        "中": [
            "使用 TypeScript 获得类型安全",
            "拆分大型组件，遵循单一职责原则",
            "使用 Context API 或状态管理库管理共享状态",
            "配置 ESLint + Prettier 统一代码风格",
            "使用 Storybook 开发和测试组件",
        ],
        "低": [
            "使用语义化 HTML 标签",
            "添加适当的 ARIA 属性提升可访问性",
            "使用环境变量管理配置",
            "添加图片懒加载优化性能",
            "使用 CSS-in-JS 或 CSS Modules 组织样式",
        ],
    }

    # Vue 项目最佳实践
    VUE_BEST_PRACTICES = {
        "高": [
            "为 v-for 循环提供唯一的 key 属性",
            "避免在模板中使用复杂表达式，使用 computed 或 methods",
            "正确使用 v-if 和 v-show 根据场景选择",
            "在组件销毁时清除定时器和事件监听",
            "避免在 data 中使用箭头函数",
        ],
        "中": [
            "使用 TypeScript 提高开发体验和代码质量",
            "使用 Vuex 或 Pinia 管理全局状态",
            "合理使用组件的 props、emits、slots",
            "使用 Vetur 或 Volar 插件获得更好的 IDE 支持",
            "配置 ESLint + Prettier 统一代码风格",
        ],
        "低": [
            "使用 v-once 优化静态内容",
            "合理使用 keep-cache 缓存组件",
            "使用 Vue DevTools 调试应用",
            "使用 scoped 样式避免样式冲突",
            "为路由使用懒加载优化首屏加载",
        ],
    }

    # JavaScript/TypeScript 项目最佳实践
    JAVASCRIPT_BEST_PRACTICES = {
        "高": [
            "使用 ESLint 进行代码质量检查",
            "使用 Prettier 进行代码格式化",
            "使用 .env 文件管理环境变量，不要提交到版本库",
            "为 async/await 函数添加适当的错误处理",
            "避免在 HTML 中使用内联脚本（可防范 XSS）",
        ],
        "中": [
            "使用 TypeScript 获得类型安全",
            "使用 npm scripts 定义开发流程",
            "使用 Husky 添加 Git hooks（pre-commit 检查等）",
            "使用 Jest 或 Mocha 进行单元测试",
            "配置 .npmrc 和 .nvmrc 管理包和 Node 版本",
        ],
        "低": [
            "使用语义化版本号（Semantic Versioning）",
            "添加 package-lock.json 或 yarn.lock 确保依赖一致性",
            "使用 npm outdated 检查并更新过时的依赖",
            "在 package.json 中添加 homepage、repository、bugs 等元数据",
            "使用浏览器兼容性工具（Babel）支持旧的浏览器",
        ],
    }

    # Python 项目最佳实践
    PYTHON_BEST_PRACTICES = {
        "高": [
            "使用虚拟环境（venv、poetry）隔离项目依赖",
            "使用 .env 文件管理环境变量，不要提交到版本库",
            "为所有公共函数添加 docstring 文档",
            "使用 try-except 处理异常，避免裸 except",
            "使用 f-string 进行字符串格式化",
        ],
        "中": [
            "使用 pyproject.toml 替代 setup.py（现代 Python 项目）",
            "使用 Black 格式化代码，isort 排序导入",
            "使用 PyTest 进行单元测试，覆盖率 >= 80%",
            "使用 Type Hints 提高代码可读性",
            "遵循 PEP 8 编码规范",
        ],
        "低": [
            "使用 logging 模块而非 print",
            "使用 pathlib 操作路径替代 os.path",
            "为项目添加 requirements.txt 文件",
            "使用 dataclass 简化数据类定义",
            "使用 typing 提高类型注解。",
        ],
    }

    # Java 项目最佳实践
    JAVA_BEST_PRACTICES = {
        "高": [
            "使用 Lombok 减少样板代码，确保团队统一",
            "使用 Spring Boot Actuator 监控应用健康状态",
            "正确使用 @Transactional 管理数据库事务",
            "避免使用 System.out.println，使用日志框架",
            "使用配置中心管理敏感信息",
        ],
        "中": [
            "使用 Spring Boot 进行快速开发",
            "配置 CI/CD 自动化测试和部署",
            "使用 Checkstyle、PMD 等工具进行代码审查",
            "遵循领域驱动设计（DDD）分层架构",
            "使用 Docker 容器化应用",
        ],
        "低": [
            "使用 IntelliJ IDEA 的代码风格配置",
            "使用 Spring AOP 处理横切关注点",
            "使用 Spring Security 进行身份认证和授权",
            "为 API 添加 Swagger 文档",
            "使用 Redis 缓存提升性能",
        ],
    }

    # 通用最佳实践
    COMMON_BEST_PRACTICES = {
        "高": [
            "使用版本控制（.gitignore 包含 node_modules、dist、build）",
            "添加 LICENSE 文件明确版权和许可",
            "包含 README.md 文档，说明项目、安装、使用方法",
            "遵循语义化版本号（Semantic Versioning）",
            "配置自动化测试，确保核心功能可靠",
        ],
        "中": [
            "使用 CI/CD 自动化构建、测试、部署",
            "为代码编写单元测试，覆盖率 >= 70%",
            "使用代码审查流程（Pull Request）",
            "配置 Linter 和 Formatter 统一代码风格",
            "为项目添加贡献指南（CONTRIBUTING.md）",
        ],
        "低": [
            "使用包管理器管理依赖，避免手动下载",
            "定期更新依赖库，修复安全漏洞",
            "为 API 添加文档（OpenAPI/Swagger）",
            "使用性能监控工具跟踪应用性能",
            "配置错误监控和告警系统",
        ],
    }

    def __init__(self, project_path: Path):
        """
        初始化建议器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)

    def suggest(
        self,
        tech_stack: Any = None,
        architecture: Any = None
    ) -> List[Tuple[str, str]]:
        """
        生成最佳实践建议

        Args:
            tech_stack: 技术栈信息
            architecture: 架构信息

        Returns:
            建议列表，每项为 (优先级, 建议)
        """
        suggestions = []

        # 根据技术栈生成专属建议
        if tech_stack:
            suggestions.extend(self._suggest_for_tech_stack(tech_stack))

        # 根据架构生成建议
        if architecture:
            suggestions.extend(self._suggest_for_architecture(architecture))

        # 通用最佳实践
        suggestions.extend(self._suggest_common())

        # 根据项目检查生成针对性建议
        suggestions.extend(self._suggest_from_project_inspection())

        return suggestions

    def _suggest_for_tech_stack(self, tech_stack: Any) -> List[Tuple[str, str]]:
        """根据技术栈生成建议"""
        suggestions = []

        if not tech_stack:
            return suggestions

        language = tech_stack.language.lower() if hasattr(tech_stack, "language") else ""
        framework = tech_stack.framework.lower() if hasattr(tech_stack, "framework") else ""

        # React 建议
        if "react" in language or "react" in framework:
            for priority, practices in self.REACT_BEST_PRACTICES.items():
                for practice in practices:
                    suggestions.append((priority, practice))

        # Vue 建议
        if "vue" in framework:
            for priority, practices in self.VUE_BEST_PRACTICES.items():
                for practice in practices:
                    suggestions.append((priority, practice))

        # JavaScript/TypeScript 建议
        if "javascript" in language or "typescript" in language:
            for priority, practices in self.JAVASCRIPT_BEST_PRACTICES.items():
                for practice in practices:
                    suggestions.append((priority, practice))

        # Node.js 特定建议
        if "node" in framework.lower() or "express" in framework.lower() or "nest" in framework.lower():
            suggestions.append(("中", "使用 PM2 或 forever 保持 Node.js 进程运行"))
            suggestions.append(("高", "使用 helmet 中间件增强安全性"))
            suggestions.append(("中", "使用 Winston 或 pino 记录应用日志"))

        # Python 建议
        if "python" in language:
            for priority, practices in self.PYTHON_BEST_PRACTICES.items():
                for practice in practices:
                    suggestions.append((priority, practice))

        # Java 建议
        if "java" in language:
            for priority, practices in self.JAVA_BEST_PRACTICES.items():
                for practice in practices:
                    suggestions.append((priority, practice))

        return suggestions

    def _suggest_for_architecture(self, architecture: Any) -> List[Tuple[str, str]]:
        """根据架构生成建议"""
        suggestions = []

        if not architecture:
            return suggestions

        pattern = architecture.pattern.lower() if hasattr(architecture, "pattern") else ""

        # 模块化建议
        if hasattr(architecture, "modules"):
            module_count = len(architecture.modules)
            if module_count < 3:
                suggestions.append((
                    "中",
                    "建议将项目拆分为更多模块，提升代码组织和可维护性"
                ))
            elif module_count > 15:
                suggestions.append((
                    "中",
                    "模块过多可能导致过度设计，建议合并相似功能的模块"
                ))

        return suggestions

    def _suggest_common(self) -> List[Tuple[str, str]]:
        """生成通用最佳实践建议"""
        suggestions = []

        for priority, practices in self.COMMON_BEST_PRACTICES.items():
            for practice in practices:
                suggestions.append((priority, practice))

        return suggestions

    def _suggest_from_project_inspection(self) -> List[Tuple[str, str]]:
        """基于项目检查生成建议"""
        suggestions = []

        # 检查是否有 .gitignore
        if not (self.project_path / ".gitignore").exists():
            suggestions.append((
                "高",
                "添加 .gitignore 文件，避免提交不必要的文件到版本库"
            ))

        # 检查是否有 README
        if not (self.project_path / "README.md").exists():
            suggestions.append((
                "高",
                "添加 README.md 文件，说明项目用途、安装和使用方法"
            ))

        # 检查是否有 LICENSE
        if not list(self.project_path.glob("LICENSE*")):
            suggestions.append((
                "中",
                "添加 LICENSE 文件，明确项目的开源许可证"
            ))

        # 检查是否有 .env 示例
        if not (self.project_path / ".env.example").exists() and not (self.project_path / ".env.template").exists():
            if (self.project_path / ".env").exists():
                suggestions.append((
                    "中",
                    "创建 .env.example 或 .env.template 模板，不要将真实的 .env 文件提交到版本库"
                ))

        # 检查是否有测试目录
        test_dirs = ("tests", "test", "__tests__", "spec")
        if not any((self.project_path / d).exists() for d in test_dirs):
            suggestions.append((
                "高",
                "创建 tests 或 test 目录，为项目添加单元测试"
            ))

        # 检查是否有 CI/CD 配置
        ci_files = (".github/workflows", ".gitlab-ci.yml", "circleci", "travis.yml", "azure-pipelines.yml")
        if not any((self.project_path / d).exists() for d in ci_files):
            suggestions.append((
                "中",
                "配置 CI/CD 自动化测试和部署流程（如 GitHub Actions、GitLab CI）"
            ))

        # 检查是否有文档目录
        if not (self.project_path / "docs").exists():
            suggestions.append((
                "低",
                "创建 docs 目录，存放项目文档和 API 说明"
            ))

        # 检查是否有贡献指南
        if not (self.project_path / "CONTRIBUTING.md").exists():
            suggestions.append((
                "低",
                "添加 CONTRIBUTING.md 贡献指南，说明如何参与项目开发"
            ))

        # 检查是否有安全策略
        if not (self.project_path / "SECURITY.md").exists():
            suggestions.append((
                "低",
                "添加 SECURITY.md 安全策略，说明如何报告安全漏洞"
            ))

        return suggestions
