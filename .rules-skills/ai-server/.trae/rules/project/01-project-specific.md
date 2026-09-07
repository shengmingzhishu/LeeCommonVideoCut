---
alwaysApply: true
---
# 项目特定规则

> 本文档定义 ai-server 项目特有的命名约定、模块结构和领域规则。

## 1. 命名约定

### 1.1 领域前缀

| 领域 | 前缀（类/函数） | 示例 |
|------|-----------------|------|
| 评测 | `Eval` / `eval_` | `EvalRunner`, `eval_suite` |
| 任务 | `Task` / `task_` | `TaskManager`, `task_id` |
| MCP 工具调用 | `Mcp` / `mcp_` | `McpToolEvaluator`, `mcp_server` |
| 用户认证 | `User` / `Auth` / `user_` / `auth_` | `UserService`, `AuthToken`, `user_id` |
| 文件导入 | `File` / `Import` / `file_` / `import_` | `FileImportService`, `import_cases` |
| 历史记录 | `History` / `Record` / `history_` / `record_` | `HistoryService`, `eval_record` |
| 报告 | `Report` / `report_` | `ReportGenerator`, `report_id` |
| 被测系统 | `Target` / `Provider` / `target_` / `provider_` | `TargetSystem`, `provider_config` |

服务类以 `Service` 结尾，管理器类以 `Manager` 结尾，评测器类以 `Evaluator` 或 `Runner` 结尾。

### 1.2 评测相关命名

- 评测套件：`eval_suite`
- 评测用例：`eval_case`
- 评测结果：`eval_result`
- 评测方向：`eval_direction`（如 `text_qa` / `sql_correctness` / `rag_scoring`）
- 测试方式：`eval_method`（如 `ai_model` / `rag_scoring`）
- 任务：`task`
- 模型/供应商：`provider`、`model`

### 1.3 评测方向与测试方式枚举

```python
class EvalDirection(str, Enum):
    """评测方向。"""
    TEXT_QA = "text_qa"                  # 文本问答
    SQL_CORRECTNESS = "sql_correctness"  # SQL 脚本正确性
    RAG_SCORING = "rag_scoring"          # RAG 评分
    # 新增方向在此扩展...


class EvalMethod(str, Enum):
    """测试方式。"""
    AI_MODEL = "ai_model"      # AI 模型测试
    RAG_SCORING = "rag_scoring"  # RAG 评分测试
    # 新增方式在此扩展...
```

### 1.4 异常类命名

```
EvalServerError                      # 项目根异常
├── EvalSuiteError                   # 评测套件错误
├── EvalCaseError                    # 评测用例错误
├── EvalDirectionError               # 评测方向不支持或配置错误
├── TaskError                        # 任务错误
│   ├── TaskNotFoundError
│   ├── TaskStatusError
│   └── TaskTimeoutError
├── McpClientError                   # MCP 客户端错误
│   ├── McpToolCallError
│   └── McpServerError
├── AuthError                        # 认证错误
│   ├── InvalidTokenError
│   └── PermissionDeniedError
├── FileImportError                  # 文件导入错误
│   ├── FileFormatError
│   └── FileSizeExceededError
└── TargetSystemError                # 被测系统错误
    ├── TargetConnectionError
    └── TargetResponseError
```

## 2. 模块结构

> 各层职责定义见 `common/02-architecture-patterns.md` §1（分层架构）、§1.3（core/ 定位）、§1.4（何时用 Manager 层）。

```
src/ai_eval_server/
├── main.py                         # 应用入口
├── config/                         # 配置模块
│   └── settings.py                 # 配置加载与管理
├── controllers/                    # 控制层（职责见 02 §1.1）
│   ├── __init__.py
│   ├── controller.py               # 基础控制器（通用接口 + 健康检查）
│   ├── eval_controller.py          # 评测相关接口
│   ├── task_controller.py          # 任务相关接口
│   ├── user_controller.py          # 用户认证接口
│   └── file_controller.py          # 文件导入接口
├── services/                       # 服务层（单领域业务逻辑，职责见 02 §1.1）
│   ├── __init__.py
│   ├── eval_service.py             # 评测用例管理（CRUD、校验）
│   ├── task_service.py             # 任务管理（创建、查询、状态更新）
│   ├── user_service.py             # 用户管理（注册、登录、权限）
│   ├── file_service.py             # 文件解析与导入
│   ├── history_service.py          # 历史记录管理
│   └── report_service.py           # 报告生成
├── managers/                       # 管理层（跨领域编排，何时使用见 02 §1.4）
│   ├── __init__.py
│   ├── eval_manager.py             # 评测流程编排（用例加载→执行→评分→记录）
│   ├── target_manager.py           # 被测系统接入与路由（配置驱动选择目标系统）
│   ├── mcp_manager.py              # MCP 工具调用管理
│   └── task_scheduler.py           # 任务调度器（批量任务、并发控制、重试）
├── models/                         # 模型层（职责见 02 §1.1）
│   ├── __init__.py
│   ├── schemas/                    # Pydantic 数据模型
│   │   ├── eval.py                 # 评测相关 Schema（套件、用例、结果）
│   │   ├── task.py                 # 任务相关 Schema
│   │   ├── user.py                 # 用户相关 Schema
│   │   ├── mcp.py                  # MCP 相关 Schema
│   │   └── report.py               # 报告相关 Schema
│   └── entities/                   # ORM 实体模型
│       ├── eval_suite.py           # 评测套件表
│       ├── eval_case.py            # 评测用例表
│       ├── eval_record.py          # 评测记录表（历史记录）
│       ├── task.py                 # 任务表
│       ├── user.py                 # 用户表
│       └── target_system.py        # 被测系统配置表
├── utils/                          # 工具集（通用工具，与业务无关）
│   ├── asynchttp.py
│   ├── llmclient.py
│   ├── logs.py
│   ├── env.py
│   └── ...
└── core/                           # 核心业务组件（定位见 02 §1.3，由 Manager 调用）
    ├── evaluator.py                # 评测器抽象（不同方向的评测策略）
    ├── scorer.py                   # 评分器（不同评分规则）
    └── reporter.py                 # 报告生成器
```

## 3. 领域特定规则

### 3.1 评测执行

- 评测执行必须支持重试与超时控制
- 同一评测套件内用例按配置顺序或并行度执行
- 评测输入/输出必须完整记录，便于复现与审计
- 评分规则应可配置，支持人工规则与模型打分
- **评测方向扩展**：新增评测方向时，只需在 `core/evaluator.py` 新增对应 Evaluator 实现并在配置中注册，不修改 Manager 层逻辑

### 3.2 被测系统接入

- 被测系统通过配置管理，支持动态切换（LLM 服务、RAG 系统、MCP 工具服务器等）
- `TargetManager` 根据配置路由到对应的被测系统，对上层透明
- 新增被测系统类型时，只需实现统一接口并在配置中注册
- 被测系统调用需记录入参、返回、异常和耗时

### 3.3 MCP 工具调用

- MCP 客户端连接与调用必须支持超时、重试和错误码映射
- 工具调用结果需记录入参、返回、异常和耗时
- 工具列表缓存需设置合理过期时间，避免频繁刷新

### 3.4 任务管理

- 大批量评测必须异步处理，接口立即返回任务 ID
- 任务状态：pending / running / completed / failed / cancelled
- 失败任务支持重试
- 任务进度按用例/套件粒度更新
- 任务结果需可查询、可导出
- **复测支持**：任务可基于历史记录中的用例集合重新执行，不依赖原始测试集是否存在

### 3.5 历史记录与复测

- 每次评测执行的结果（含输入、输出、评分明细）必须持久化存储
- 历史记录按用户隔离，支持按时间、方向、状态等条件查询
- **复测**：用户可勾选历史记录中的若干条目，一键重新执行评测
- **反复测试**：同一测试内容可多次执行，每次结果独立存储，支持结果对比
- 历史记录保留策略可配置（按时间或数量清理）

### 3.6 用户认证

- 用户登录通过用户名/密码验证，签发 JWT Token
- Token 在请求头中传递：`Authorization: Bearer <token>`
- 所有业务接口必须校验 Token（登录/注册接口除外）
- 用户只能访问自己的测试数据和历史记录
- Token 支持过期刷新机制

### 3.7 文件导入

- 支持的文件格式：Excel（.xlsx）、JSON、CSV
- 文件大小限制可配置，默认 10MB
- 导入前校验文件格式和内容合法性
- 导入结果返回成功/失败条目明细
- 导入的测试用例归属当前用户
- 支持批量导入到指定测试集

### 3.8 评测方向与测试方式配置

- 评测方向和测试方式通过配置组合，非代码硬编码
- 配置示例：

```python
# 评测方向配置
EVAL_DIRECTIONS = {
    "text_qa": {
        "name": "文本问答评测",
        "evaluator": "TextQaEvaluator",      # 对应 core/evaluator.py 中的实现
        "scorer": "RuleBasedScorer",          # 对应 core/scorer.py 中的实现
        "supported_methods": ["ai_model"],    # 支持的测试方式
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
}
```
