---
alwaysApply: true
description: 四层架构设计规则，包括分层职责（Controller/Service/Manager/Model）、模块划分、数据流规范、错误处理、配置管理、事务ID日志规范。设计项目架构、划分模块、编写各层代码时使用此规则。
---

# 架构设计规则（通用）

> 本规范适用于采用四层架构的 Python 后端项目，可直接复制使用。
> 项目特定的模块划分请在 `project/01-project-specific.md` 中定义。

## 1. 分层架构

项目采用四层架构，严格遵守分层职责。在经典三层架构基础上新增 **Manager 层**，用于处理跨服务编排、复杂业务流程管理和外部系统对接。

```
┌─────────────────────────────────────────────┐
│         Controllers (控制层)                  │
│  路由定义 / 参数校验 / 鉴权 / 响应封装         │
├─────────────────────────────────────────────┤
│          Services (服务层)                    │
│  单领域业务逻辑 / 规则处理 / 数据组装          │
├─────────────────────────────────────────────┤
│          Managers (管理层)                    │
│  跨服务编排 / 复杂流程 / 外部系统对接 / 事务   │
├─────────────────────────────────────────────┤
│           Models (模型层)                     │
│  数据模型 / 数据库访问 / 外部接口封装          │
└─────────────────────────────────────────────┘
```

### 1.1 分层依赖规则

- **上层依赖下层**：Controller → Service → Manager → Model
- **禁止反向依赖**：Service 层不能 import Controller，Manager 层不能 import Service，Model 层不能 import Manager
- **禁止跨层调用**：Controller 不能直接调用 Manager 或 Model，Service 不能直接操作 Model 层的数据库
- **同层可横向调用**：Service 之间可以互相调用，Manager 之间可以互相调用，但避免循环依赖

### 1.2 各层职责

#### Controllers 层
- 路由定义与接口暴露
- 请求参数接收、解析与基础校验
- 身份识别、权限校验
- 调用 Service 层完成业务编排
- 统一响应封装与错误返回

**禁止事项：**
- 禁止直接操作数据库
- 禁止编写复杂业务规则
- 禁止跨模块数据拼装
- 禁止直接调用 Manager 层

#### Services 层
- 单一领域的业务逻辑实现
- 领域内业务规则校验与执行
- 调用 Manager 层完成跨领域协作
- 数据转换与组装

**禁止事项：**
- 禁止接收 HTTP 请求参数（应使用明确的业务参数）
- 禁止返回 HTTP 响应对象
- 禁止打印 HTTP 相关日志
- 禁止直接操作数据库（通过 Model 层）

#### Managers 层
- **跨服务编排**：协调多个 Service 完成复杂业务流程
- **外部系统对接**：封装第三方系统调用、协议适配
- **事务管理**：跨数据源的分布式事务或复合事务
- **流程状态管理**：管理多步骤业务流程的状态流转
- **策略路由**：根据配置动态选择执行策略或接入系统

**禁止事项：**
- 禁止包含单一领域的细粒度业务规则（放 Service 层）
- 禁止直接暴露给 Controller 层
- 禁止包含 HTTP 相关逻辑
- 禁止直接操作 ORM Session（通过 Model 层）

#### Models 层
- 数据模型定义（ORM Model、Pydantic Schema）
- 数据库访问封装（CRUD）
- 外部 API 客户端封装
- 数据持久化操作

**禁止事项：**
- 禁止包含业务规则判断
- 禁止直接调用 Manager 或 Service 层

### 1.3 core/ 目录定位

`core/` 目录存放**核心业务组件**（如评测器、评分器、报告生成器），不属于四层架构中的任何一层，而是 **Service 层和 Manager 层共享的策略实现**。

- `core/` 中的组件由 Manager 层调用，Service 层不直接调用
- `core/` 中的组件不依赖任何层，只定义抽象接口和算法实现
- 新增业务策略时（如新增评测方向），在 `core/` 中新增实现类，在配置中注册

```
Manager 层 → 调用 → core/ 中的策略实现
core/      → 不依赖 → 任何层（纯算法/策略）
```

### 1.4 何时使用 Manager 层

| 场景 | 使用层 | 说明 |
|------|--------|------|
| 单表 CRUD | Service | 直接在 Service 调用 Model |
| 单领域业务逻辑 | Service | 如评测用例管理 |
| 跨领域业务编排 | Manager | 如评测任务调度涉及用例+任务+结果 |
| 外部系统接入适配 | Manager | 如接入不同 LLM 提供商 |
| 多步骤事务流程 | Manager | 如评测任务创建→执行→评分→报告 |
| 配置驱动的策略选择 | Manager | 如根据配置选择评测方向和方式 |

## 2. 模块设计原则

### 2.1 设计原则

1. **单一职责**：每个模块只负责一个功能领域
2. **高内聚低耦合**：模块内部高度相关，模块之间低依赖
3. **依赖注入**：通过参数传递依赖，避免硬编码依赖关系
4. **接口抽象**：依赖抽象而非具体实现，便于替换
5. **配置驱动**：通过配置切换行为，而非修改代码

### 2.2 推荐目录结构

```
src/{package_name}/
├── main.py                 # 应用入口
├── config/                 # 配置模块
├── controllers/            # 控制层
├── services/               # 服务层（单领域业务逻辑）
├── managers/               # 管理层（跨领域编排、外部对接）
├── models/                 # 模型层
│   ├── schemas/            # Pydantic 数据模型
│   └── entities/           # ORM 实体模型
├── utils/                  # 通用工具（与业务无关）
└── core/                   # 核心业务组件（可选）
```

> 具体模块划分请参考 `project/01-project-specific.md`

### 2.3 新增模块规范

新增模块时必须遵循以下步骤：
1. 明确模块职责边界（写在模块 docstring 中）
2. 确定所属层级（Controller / Service / Manager / Model）
3. 定义对外暴露的接口（`__init__.py` 中显式导出）
4. 编写单元测试
5. 更新项目模块结构文档

## 3. 数据流规范

### 3.1 数据传递对象

- **Controller ↔ Service**：使用 Pydantic Schema 或数据类
- **Service ↔ Manager**：使用领域 DTO 或数据类
- **Manager ↔ Model**：使用 ORM Entity 或专用 DTO
- **禁止在层间传递原始字典**（除非明确约定的通用结构）

### 3.2 参数传递

- 函数参数不超过 5 个，超过时封装为对象
- 使用关键字参数提高可读性
- 避免传递大型对象，只传递必要的字段

## 4. 错误处理规范

### 4.1 异常层级建议

```
Exception
├── ProjectError              # 项目根异常
│   ├── ValidationError       # 数据校验错误
│   ├── NotFoundError         # 资源不存在错误
│   ├── BusinessError         # 业务规则错误
│   ├── ServiceError          # 服务调用错误
│   └── ManagerError          # 编排/流程错误
│       ├── OrchestrationError
│       └── ExternalSystemError
```

> 具体异常类定义请在 `project/` 中补充

### 4.2 异常处理原则

- **早抛出，晚捕获**：在错误发生处立即抛出，在上层合适位置捕获
- **异常链保留**：重新抛出时使用 `raise NewError(...) from original_error`
- **禁止静默失败**：捕获异常后至少要记录日志
- **业务异常 vs 系统异常**：
  - 业务异常：用户可理解、可预期的错误
  - 系统异常：内部错误，不应暴露给用户

## 5. 配置管理

### 5.1 配置来源优先级

1. 环境变量（最高优先级）
2. `.env` 文件
3. 配置文件
4. 代码默认值（最低优先级）

### 5.2 配置定义

- 所有配置集中在 `utils/env.py` 中定义
- 配置项必须有类型、默认值和注释（见编码规范 5.3 节）
- 敏感配置（密钥、密码）不得硬编码
- 新增配置项必须在 .env.example 中说明
- 支持多系统接入的配置应按系统分组，便于管理

## 6. 日志规范

### 6.1 日志级别使用

| 级别 | 使用场景 |
|------|---------|
| DEBUG | 调试信息，开发时使用，生产环境关闭 |
| INFO | 正常业务流程记录（任务开始、完成、状态变更） |
| WARNING | 可恢复的异常情况、重试、非预期但可继续的情况 |
| ERROR | 业务失败、系统错误，需要人工关注 |
| CRITICAL | 系统级严重错误，服务不可用 |

### 6.2 事务 ID（Transaction ID）

**所有业务请求和任务必须携带事务 ID**，用于串联完整调用链路。

- **生成时机**：在 Controller 层入口（中间件）或任务调度入口生成
- **传递方式**：通过请求上下文（contextvars）或显式参数传递
- **日志格式**：每条日志必须包含事务 ID 字段

```python
# 日志格式示例：时间 | 级别 | 事务ID | 模块 | 函数 | 行号 | 消息
# 2026-08-12 10:30:00 | INFO | tx:abc123def | eval_service | run_eval | 45 | 评测任务 task-001 开始执行
```

### 6.3 日志内容要求

- 必须包含上下文信息（事务 ID、任务 ID、关键业务标识等）
- 禁止打印敏感信息（密钥、密码、用户隐私数据）
- 禁止打印完整的大文件内容
- 错误日志必须包含异常堆栈
- **调用链路日志**：跨层调用时需记录入口和出口，标注耗时

```python
# 好的日志 - 有事务ID和上下文
LOGGER.info(f"[tx:{tx_id}] Task {task_id} started, suite={suite_id}, cases={len(case_ids)}")
LOGGER.info(f"[tx:{tx_id}] Task {task_id} completed, duration={elapsed}s, pass_rate={pass_rate}")

# 跨层调用日志
LOGGER.info(f"[tx:{tx_id}] Manager calling eval_service.run_eval, suite={suite_id}")
LOGGER.info(f"[tx:{tx_id}] eval_service.run_eval returned, duration={elapsed}s")

# 不好的日志
LOGGER.info("processing...")  # 无上下文
LOGGER.debug(f"Full data: {big_data}")  # 可能很大
```

### 6.4 日志文件管理

- 日志按日期分文件，保留最近 N 天（可配置）
- 日志目录结构清晰：`logs/{project_name}/{project_name}-YYYY-MM-DD.log`
- 日志排版统一，使用 `|` 分隔字段，便于 grep 和肉眼阅读
