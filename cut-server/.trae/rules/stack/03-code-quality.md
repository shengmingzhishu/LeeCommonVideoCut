---
alwaysApply: false
description: 代码质量与审查规则，包括质量标准、代码审查清单、测试规范（分类存放+时间戳输出）、性能规范、安全规范、重构规则。进行代码审查、编写测试、性能优化、安全检查、代码重构时使用此规则。
---

# 代码质量与审查规则（通用）

> 本规范适用于所有 Python 项目，可直接复制使用。

## 1. 代码质量标准

### 1.1 可读性

- 代码应该像散文一样清晰易读
- 函数体不超过 50 行，超过时考虑拆分
- 嵌套层级不超过 4 层，超过时考虑提前返回或提取函数
- 单个文件不超过 500 行，超过时考虑拆分模块

### 1.2 可维护性

- 修改代码时，相关的测试必须同步更新
- 公共接口变更必须更新文档
- 删除代码时确认没有其他地方依赖
- 修复 Bug 时必须补充对应的回归测试

### 1.3 可测试性

- 依赖通过参数注入，避免硬编码依赖
- 副作用与纯逻辑分离，纯逻辑部分必须可单元测试
- 避免在类构造函数中做复杂初始化
- 避免使用全局状态

## 2. 代码审查清单

### 2.1 必查项（P0 - 必须通过）

- [ ] 代码能正常运行，没有语法错误
- [ ] 单元测试通过，覆盖率不降低
- [ ] 没有硬编码的密钥、密码等敏感信息
- [ ] 没有 SQL 注入、命令注入等安全漏洞
- [ ] 异常处理正确，没有静默吞掉异常
- [ ] 命名清晰，符合项目命名规范
- [ ] 没有重复代码（重复超过 3 行需要提取）
- [ ] 所有方法有文档字符串（见编码规范 5.2 节）
- [ ] 配置项有注释（见编码规范 5.3 节）

### 2.2 重要项（P1 - 尽量通过）

- [ ] 类型提示完整
- [ ] 文档字符串齐全
- [ ] 函数职责单一，没有上帝函数
- [ ] 没有过度设计
- [ ] 日志适当，包含事务 ID，既不缺失也不冗余
- [ ] 性能考虑合理（避免 N+1 查询等）
- [ ] 边界条件处理正确
- [ ] 分层正确（未跨层调用）

### 2.3 建议项（P2 - 可选优化）

- [ ] 代码风格一致性
- [ ] 注释清晰解释"为什么"
- [ ] 变量名可以更精准
- [ ] 可以进一步抽象复用
- [ ] 测试用例更全面

## 3. 测试规范

### 3.1 测试层级

| 层级 | 测试对象 | 工具 | 要求 |
|------|---------|------|------|
| 单元测试 | 单个函数/类 | pytest | 核心逻辑必须覆盖 |
| 集成测试 | 模块间协作 | pytest + testcontainers | 关键流程必须覆盖 |
| 接口测试 | API 接口 | httpx / pytest | 对外接口必须覆盖 |
| E2E 测试 | 完整业务流程 | 按需 | 核心流程可选 |

### 3.2 测试目录分类规范

测试文件**按分类存放**，每个分类对应一个子目录，避免所有测试堆在同一层级。

```
tests/
├── unit/                       # 单元测试
│   ├── services/               # 服务层测试
│   │   ├── test_eval_service.py
│   │   └── test_task_service.py
│   ├── managers/               # 管理层测试
│   │   └── test_eval_manager.py
│   ├── models/                 # 模型层测试
│   │   └── test_eval_suite.py
│   └── utils/                  # 工具类测试
│       └── test_string_utils.py
├── integration/                # 集成测试
│   ├── test_eval_flow.py       # 评测流程集成测试
│   └── test_task_flow.py       # 任务流程集成测试
├── api/                        # 接口测试
│   ├── test_eval_api.py
│   └── test_auth_api.py
└── e2e/                        # 端到端测试（可选）
    └── test_full_eval_pipeline.py
```

### 3.3 测试输出结果管理

**每个测试的输出结果按「日期+时间戳」文件夹独立存放**，避免不同次测试结果混淆。

```
tests/output/                              # 测试输出根目录
├── 20260812_103000/                       # 2026-08-12 10:30:00 的测试输出
│   ├── pytest_report.html                 # HTML 测试报告
│   ├── pytest_report.xml                  # XML 测试报告（CI 用）
│   ├── coverage/                          # 覆盖率报告
│   │   ├── index.html
│   │   └── ...
│   └── logs/                              # 测试期间的日志输出
│       └── test_run.log
├── 20260812_143000/                       # 同日不同时间的另一次测试
│   ├── pytest_report.html
│   └── ...
└── 20260813_090000/                       # 不同日期
    └── ...
```

**实现方式：** 在 `conftest.py` 中通过 fixture 自动创建时间戳目录：

```python
# tests/conftest.py
import os
import pytest
from datetime import datetime

@pytest.fixture(scope="session", autouse=True)
def test_output_dir():
    """为每次测试运行创建独立的输出目录。"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("tests", "output", timestamp)
    os.makedirs(os.path.join(output_dir, "logs"), exist_ok=True)
    os.environ["TEST_OUTPUT_DIR"] = output_dir
    return output_dir
```

### 3.4 单元测试要求

- 测试文件与源代码对应：`tests/` 目录结构镜像 `src/`
- 测试文件命名：`test_<module_name>.py`
- 测试函数命名：`test_<场景>_<预期结果>`
- 每个测试函数只验证一个场景

**示例：**
```python
# tests/unit/services/test_eval_service.py
"""测试评测服务模块。"""

import pytest


class TestEvalService:
    """测试 EvalService 类。"""

    def test_run_eval_valid_suite_returns_results(self):
        """有效套件应成功返回评测结果。"""
        pass

    def test_run_eval_invalid_suite_id_raises_error(self):
        """无效套件 ID 应抛出错误。"""
        pass
```

### 3.5 测试覆盖率

- 核心业务代码覆盖率 ≥ 80%
- 工具类覆盖率 ≥ 90%
- 新增代码覆盖率必须 ≥ 80%
- 不追求 100% 覆盖率，但关键路径必须覆盖

### 3.6 测试原则

- 测试应该快速、独立、可重复
- 使用 fixture 共享测试数据和 setup/teardown
- 避免测试之间互相依赖
- Mock 外部依赖（数据库、API 调用等）
- 测试数据应该具有代表性，覆盖边界情况
- 测试输出不互相覆盖，每次运行结果可追溯

## 4. 性能规范

### 4.1 常见性能问题检查

- 避免在循环中做数据库查询（N+1 问题）
- 避免在循环中调用外部 API
- 大文件处理使用流式读取，避免一次性加载到内存
- 批量操作减少 I/O 次数
- 缓存可复用的计算结果

### 4.2 内存使用

- 大数据集按需加载，不一次性全部加载
- 大文件分块处理
- 及时释放不再需要的资源（使用 `with` 语句）
- 避免保留对大对象的引用

## 5. 安全规范

> 涉及安全相关代码时必须遵守本节全部规则。

### 5.1 输入校验

- **所有外部输入必须校验**：API 参数、文件内容、外部系统返回值
- 使用 Pydantic Schema 校验请求体，禁止直接使用 `dict` 接收输入
- 字符串输入必须限制最大长度，防止缓冲区攻击
- 文件路径输入必须校验，禁止 `..` 路径穿越

```python
# 正确：Pydantic Schema 校验
class EvalCaseCreate(BaseModel):
    title: str = Field(..., max_length=200)
    direction: EvalDirection

# 错误：直接使用 dict
async def create_case(data: dict): ...  # 禁止
```

### 5.2 密钥管理

- **禁止硬编码密钥**：API Key、Token、密码、数据库连接串必须走环境变量
- `.env` 文件不提交到 Git
- 日志中敏感信息必须脱敏（Token 只显示前 4 位 + `***`）

```python
API_KEY = os.getenv('LLM_API_KEY')  # 正确
API_KEY = "sk-xxxxxxxxxxxx"         # 禁止
LOGGER.info(f"Key: {API_KEY[:4]}***")  # 正确
```

### 5.3 文件上传安全

- 校验扩展名白名单 + 文件大小（默认 10MB）
- 文件名必须重命名或 sanitize，防止路径穿越
- 上传文件存储路径不可由用户输入控制

### 5.4 密码存储

- 用户密码必须加盐哈希存储（`bcrypt` 或 `argon2`），禁止明文
- 密码强度校验：最少 8 位，包含字母和数字

### 5.5 SQL 注入防护

- **禁止拼接 SQL 字符串**，必须使用 ORM 或参数化查询
- 如需原生 SQL，必须使用 `text()` + 绑定参数

```python
# 正确：ORM 或参数化
session.query(EvalCase).filter(EvalCase.id == case_id).first()
session.execute(text("SELECT * FROM t WHERE id = :id"), {"id": case_id})

# 错误：字符串拼接
session.execute(text(f"SELECT * FROM t WHERE id = {case_id}"))  # 禁止
```

### 5.6 接口鉴权

- 所有业务接口必须校验 JWT Token（登录/注册除外）
- Token 从 `Authorization: Bearer <token>` 获取，过期返回 401
- 用户只能访问自己的数据，查询必须包含 `user_id` 过滤

### 5.7 其他安全规则

- CORS 必须限制允许的域名，禁止 `*`
- 生产环境关闭 `debug=True`，错误响应不返回堆栈信息
- 外部 API 调用必须设置超时（默认 30s）
- 日志中禁止记录完整的请求体/响应体

## 6. 重构规则

### 6.1 重构时机

- 三次重复：相同逻辑出现第三次时必须重构
- 需求变化：现有结构无法优雅支撑新需求时
- Bug 修复：为修复 Bug 而导致代码混乱时
- 代码审查：审查中提出的结构性问题

### 6.2 重构原则

- 重构前确保有测试覆盖
- 小步重构，每步都可运行可验证
- 重构不改变外部行为
- 重构后运行完整测试套件

### 6.3 常见坏味道

- 重复代码 → 提取函数/类
- 长函数 → 拆分函数
- 大类 → 拆分类
- 长参数列表 → 引入参数对象
- 霰弹式修改 → 调整职责边界
- 发散式变化 → 拆分关注点
