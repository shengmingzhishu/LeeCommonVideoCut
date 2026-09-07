---
name: eval-direction-extension
version: "1.0.0"
lastUpdated: "2026-09-03"
description: "适用于 ai-server 项目新增评测方向场景：基于现有架构快速扩展新的评测能力（如代码评测、多模态评测等），包含 Evaluator 实现、Scorer 配置、Schema 定义、路由接入的完整模板。"
user-invocable: true
---

# 评测方向扩展

## 技能目标

当需要在 ai-server 中**新增一种评测方向**时，使用本技能。

本技能提供标准化的扩展流程和代码模板，确保新评测方向与现有架构（四层架构 + core/ 策略模式）完全兼容，无需修改 Manager 层逻辑。

## 适用场景

- 新增评测方向（如 `code_review`、`multimodal`、`translation` 等）
- 需要为新方向实现自定义 Evaluator 和 Scorer
- 需要在配置中注册新方向并支持前端调用

## 前置依赖

- 已阅读 `rules/project/01-project-specific.md` §1.2（评测相关命名）和 §3.8（评测方向配置）
- 已阅读 `rules/common/02-architecture-patterns.md` §1.3（core/ 目录定位）
- 当前项目已存在至少一个可运行的评测方向（如 text_qa）作为参考

## 扩展步骤

### 第 1 步：确定方向标识与枚举值

在 `models/` 或配置中新增枚举：

```python
# 在 EvalDirection 枚举中新增
class EvalDirection(str, Enum):
    TEXT_QA = "text_qa"
    SQL_CORRECTNESS = "sql_correctness"
    RAG_SCORING = "rag_scoring"
    CODE_REVIEW = "code_review"          # 新增
    # 新增方向在此扩展...
```

**命名规范**：使用 snake_case，语义清晰，避免缩写。

### 第 2 步：在 core/ 中实现 Evaluator

创建或扩展现有 `core/evaluator.py`：

```python
from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class EvalContext:
    """评测上下文，包含执行所需的全部信息。"""
    case_id: str
    case_input: Dict[str, Any]
    provider_config: Dict[str, Any]
    direction: str  # 评测方向标识
    method: str     # 测试方式


class BaseEvaluator(ABC):
    """评测器基类，所有方向必须继承此类。"""

    @abstractmethod
    async def evaluate(self, context: EvalContext) -> Dict[str, Any]:
        """
        执行评测。

        Args:
            context: 评测上下文，包含用例输入、被测系统配置等

        Returns:
            评测结果字典，必须包含：
            - score: float (0-100)
            - details: Dict (评分明细)
            - raw_response: str (原始响应)
            - latency_ms: int (耗时)
        """
        ...

    @abstractmethod
    def validate_input(self, case_input: Dict[str, Any]) -> tuple[bool, str]:
        """
        校验用例输入是否合法。

        Returns:
            (是否合法, 错误信息)
        """
        ...
```

实现具体 Evaluator：

```python
# core/evaluators/code_review_evaluator.py
class CodeReviewEvaluator(BaseEvaluator):
    """代码评审评测器。"""

    def __init__(self, llm_client):
        self._llm = llm_client

    async def evaluate(self, context: EvalContext) -> Dict[str, Any]:
        # 1. 从 context 获取代码输入
        code = context.case_input.get("code")
        language = context.case_input.get("language", "python")

        # 2. 构造 prompt
        prompt = self._build_prompt(code, language)

        # 3. 调用 LLM
        start_time = time.monotonic()
        response = await self._llm.chat(prompt)
        latency = int((time.monotonic() - start_time) * 1000)

        # 4. 解析评分
        score = self._extract_score(response)

        return {
            "score": score,
            "details": {"language": language, "response_preview": response[:200]},
            "raw_response": response,
            "latency_ms": latency,
        }

    def validate_input(self, case_input: Dict[str, Any]) -> tuple[bool, str]:
        if "code" not in case_input:
            return False, "缺少必填字段: code"
        return True, ""
```

### 第 3 步：在 core/ 中实现 Scorer

创建或扩展现有 `core/scorer.py`：

```python
class BaseScorer(ABC):
    """评分器基类。"""

    @abstractmethod
    def score(self, eval_result: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算最终评分。

        Args:
            eval_result: Evaluator 返回的结果
            expected: 用例中的预期输出（可为空）

        Returns:
            评分结果，包含总分和各维度分
        """
        ...


class CodeReviewScorer(BaseScorer):
    """代码评审评分器。"""

    def score(self, eval_result: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        base_score = eval_result["score"]

        # 可在此加入规则加权、维度拆分等逻辑
        return {
            "total_score": base_score,
            "dimensions": {
                "correctness": base_score * 0.4,
                "style": base_score * 0.3,
                "security": base_score * 0.3,
            },
        }
```

### 第 4 步：注册到配置

在 `config/settings.py` 或独立配置文件中：

```python
# 评测方向配置（新增 code_review）
EVAL_DIRECTIONS = {
    "text_qa": {
        "name": "文本问答评测",
        "evaluator": "TextQaEvaluator",
        "scorer": "RuleBasedScorer",
        "supported_methods": ["ai_model"],
    },
    "sql_correctness": {
        "name": "SQL 脚本正确性测试",
        "evaluator": "SqlCorrectnessEvaluator",
        "scorer": "SqlExecutionScorer",
        "supported_methods": ["ai_model"],
    },
    "rag_scoring": {
        "name": "RAG 评分测试",
        "evaluator": "RagScoringEvaluator",
        "scorer": "RagQualityScorer",
        "supported_methods": ["rag_scoring"],
    },
    # ===== 新增方向 =====
    "code_review": {
        "name": "代码评审评测",
        "evaluator": "CodeReviewEvaluator",   # 第 2 步实现的类
        "scorer": "CodeReviewScorer",          # 第 3 步实现的类
        "supported_methods": ["ai_model"],
        "description": "对提交的代码进行质量评审，涵盖正确性、风格、安全性",
    },
}
```

### 第 5 步：更新 Schema（如需新字段）

在 `models/schemas/eval.py` 中：

```python
# 如果新方向需要特殊输入字段，扩展 CaseInput 模型
class CodeReviewCaseInput(BaseModel):
    """代码评审用例输入。"""
    code: str                           # 待评审代码
    language: str = "python"            # 编程语言
    review_focus: list[str] = []        # 评审关注点（可选）：style, security, performance
    max_lines: int = 500                # 代码行数上限
```

### 第 6 步：验证

```bash
# 1. 单元测试
pytest tests/core/test_code_review_evaluator.py -v

# 2. 集成测试：通过 API 创建该方向的用例并执行
curl -X POST http://localhost:8000/api/eval/suites \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "代码评审测试", "direction": "code_review", ...}'

# 3. 检查日志中的事务 ID 链路是否完整
grep "\[tx:" logs/ai-server/*.log | tail -20
```

## 检查清单

完成扩展后，逐项确认：

- [ ] 枚举值已添加，命名符合 snake_case 规范
- [ ] Evaluator 继承 `BaseEvaluator`，实现了 `evaluate()` 和 `validate_input()`
- [ ] Scorer 继承 `BaseScorer`，返回包含 `total_score` 和 `dimensions` 的结构
- [ ] 配置已注册到 `EVAL_DIRECTIONS` 字典
- [ ] 如需新输入字段，Schema 已定义且带校验
- [ ] 单元测试覆盖了正常路径和异常路径
- [ ] 日志输出包含事务 ID 和耗时
- [ ] 未修改 Manager 层的现有逻辑（仅扩展，不修改）

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 新方向不出现在前端下拉框 | 配置未注册或前端未同步 | 检查 `EVAL_DIRECTIONS` 和前端枚举 |
| Evaluator 未被调用 | 类名与配置不匹配 | 确保配置中的 `evaluator` 值与实际类名一致 |
| 评分始终为 0 | Scorer 返回格式不符合预期 | 检查 `score()` 方法返回值包含 `total_score` |
| 用例输入校验总是失败 | `validate_input()` 逻辑过严 | 调整校验规则，允许合理缺省值 |

## 非目标

- 不修改现有评测方向的逻辑
- 不改动 Manager 层的任务调度机制
- 不涉及前端 UI 改动（除非新方向需要特殊输入组件）
