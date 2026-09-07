---
name: python-scaffold
description: VS Code Copilot 用的团队共享 Python 项目脚手架 Skill，在当前目录一次性渲染并生成完整项目结构、模板代码、检查脚本与测试脚本，便于团队后续个性化修改。
agent_created: true
---

# VS Code Copilot Python 脚手架 Skill

> **定位**：完整项目脚手架生成器。一次性产出包含模板代码、测试、CI 的完整项目。
>
> **与 python-project-bootstrap 的区别**：
> - `python-scaffold` = 完整脚手架（含模板代码、测试脚本、CI 配置、检查脚本），适合团队规范化项目
> - `python-project-bootstrap` = 轻量初始化（目录 + pyproject.toml + .gitignore + README），适合快速起步
>
> **选择建议**：需要"开箱即用的完整项目"用 scaffold；需要"能跑的最小项目"用 bootstrap。

## 职责

**核心功能：**
1. **一次性生成**：在当前目录直接生成完整 Python 项目结构与标准模板
2. **模板化落盘**：统一使用 `assets/` 下的模板生成代码，方便不同成员后续个性化修改
3. **校验与冒烟测试**：生成结构检查脚本、启动冒烟测试脚本与 pytest 测试，用于验证目录结构和项目是否可启动

**重要原则：**
- ✅ 技能仅在**当前工作目录**下生成目标项目结构
- ❌ **绝不**创建新的项目根目录
- **当前目录就是项目根目录 `PROJECT_ROOT`**
- ❌ **不生成 Docker 相关目录或文件**
- ✅ **不是最小实现**，默认直接生成可安装、可测试、可启动、可继续扩展的完整初版
- ✅ 默认不反复向用户确认中间步骤；只在存在明显冲突或会覆盖已有文件时才提示一次

**使用场景：**
1. 新建项目：用户先创建目录（`mkdir myproject && cd myproject`），然后调用此技能
2. 团队标准化起步：需要快速落一个统一目录、统一模板、统一验证入口的 Python 项目
3. 作为 VS Code Copilot 共享 Skill：将本目录放入 `.github/skills/python-scaffold/` 后复用

## 团队共享方式

- 这是一个**工作区级共享 Skill**，用于团队统一复用，不是个人 profile 级定制
- 推荐目录：`.github/skills/python-scaffold/`
- `SKILL.md` 文件名必须保持为 `SKILL.md`
- Skill 目录名应与 frontmatter 中的 `name: python-scaffold` 保持一致，避免发现失败
- 团队成员应共享整个 skill 目录，包括 `SKILL.md` 和 `assets/` 下全部模板文件

## 模板渲染规则

- 使用技能时，必须把 `assets/` 下的模板文件生成到最终目标文件中，不能把模板原样留在生成项目里
- 模板文件统一采用无后缀命名，技能只负责把模板内容落到目标文件，不要求保留任何模板后缀
- 目标文件名应与项目结构一致，例如 `main.py` 模板生成 `main.py`
- 模板中的变量占位符必须替换为实际值，至少包括 `project_name`、`package_name`、`description`、`python_version`、`author`
- 只有 `assets/` 目录保留模板；生成出来的项目目录中不应出现任何模板后缀文件
- 若某个模板对应的条件不满足，则跳过该模板，而不是渲染一个空白或无效文件
- 渲染完成后再统一执行校验，不要在每个文件生成后单独插入确认或检查

## 触发条件

用户包含以下意图时立即触发：
- "新建/创建/初始化一个 Python 项目/工程/项目"
- "创建一个 Python 脚手架"
- "帮我搭一个 Python 项目结构"
- "在当前目录一次生成完整 Python 项目"
- "生成一个 VS Code Copilot 用的 Python skill / 脚手架"
- "生成带检查脚本和测试脚本的 Python 模板项目"
- 任何其他表明需要在当前目录生成完整 Python 项目的请求

## 输入参数

从用户输入中提取以下参数：

| 参数 | 说明 | 必需 | 默认值 |
|------|------|------|--------|
| `project_name` | 项目名称 | 否 | 当前目录名 |
| `description` | 项目描述 | 否 | 空字符串 |
| `python_version` | Python 版本 | 否 | `3.13` |
| `package_name` | Python 包名（src 下的目录名） | 否 | project_name 的 snake_case |
| `framework` | 项目框架类型 | 否 | `script`（可选 `fastapi` / `flask` / `script`） |
| `author` | 作者名 | 否 | `""` |

**重要说明：**
- 如果未提供 `project_name`，自动使用当前目录名作为项目名称
- 技能默认在**当前工作目录**（`pwd` 的输出）中生成完整项目
- **绝不创建新的项目根目录** - 当前目录就是项目根目录 `PROJECT_ROOT`
- 用户只需 `cd` 到目标目录，然后调用技能即可
- 默认直接生成完整首版，不采用“最小实现后续再补”的策略

## 处理用户额外的集成需求

用户可能在请求中额外提到 OpenAI、MCP、数据库等集成需求。
当检测到以下关键词时，执行对应的额外步骤：

| 关键词 | 行为 |
|--------|------|
| `openai` / `gpt` / `大模型` | 使用 `assets/openai_service` 生成 OpenAI 服务模块，在 `config.py` 中添加 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` 配置项，往 `requirements.txt` 加入 `openai>=1.0.0` |
| `mcp` | 使用 `assets/mcp_service` 生成 MCP 客户端模块，在 `config.py` 中添加 `MCP_SERVER_URL` / `MCP_API_KEY` 配置项，往 `requirements.txt` 加入 `httpx>=0.27.0` |
| 上述任一种 | 创建 `src/{{ package_name }}/routers/__init__.py` + 对应的 router 文件，在 `main.py` 中加入路由注册 |
| 其他模块（数据库、缓存等） | 参照上述模式：新建 Service 类 → config 加配置项 → requirements 加依赖 → 可选 router 暴露 API |

**重要原则：所有 Service 类必须使用懒初始化**（即不在 `__init__` 和模块级别校验凭证/连接，而是在首次调用时初始化），避免导入时因配置缺失而抛异常阻塞整个应用的加载。

**⚠️ 命名注意事项：`package_name`（即 project_name 的 snake_case）不能与 Python 标准库模块重名**（如 `test`、`json`、`os`、`sys` 等）。如果检测到冲突，自动在末尾追加 `_app` 后缀（如 `test` → `test_app`），并向用户说明原因。

**⚠️ 一致性注意事项：`package_name` 必须在参数解析阶段一次性解析完成，并作为本次生成流程的唯一最终值。** 一旦确定（无论是否追加 `_app`），后续所有目录路径、模板变量、`import`、模块字符串、检查脚本、冒烟脚本、pytest、Makefile、shell 脚本都必须复用这个同一个 `package_name`；禁止在后续步骤中再次推导、猜测、拼接或替换出另一个包名变体。

## 执行步骤

### Step 1: 解析参数并准备

- 将 `project_name` 转换为 snake_case 作为 `package_name`（如 `MyProject` → `my_project`）
  - 如果未提供 `project_name`，使用当前目录名
- 若 `package_name` 与 Python 标准库模块名冲突，仅在此处追加一次 `_app` 后缀，并将结果记为本次运行唯一的最终 `package_name`
- 将最终 `package_name` 明确打印/汇报出来，供后续渲染与校验统一使用
- 确定**当前工作目录**为项目根路径 `PROJECT_ROOT`（执行 `pwd`）
- 检测用户输入中是否有 OpenAI / MCP 等额外集成关键词
- 检查 `PROJECT_ROOT` 下是否已有关键文件；若目标文件已存在，默认跳过并在最终结果里汇报，不要中途追问是否继续

### Step 1.5: 计算模板变量并准备渲染

- 至少准备以下渲染变量：`project_name`、`package_name`、`description`、`python_version`、`author`
- 这里的 `package_name` 必须是 Step 1 已解析完成的最终值，后续步骤不得再修改或重新推导
- 根据 `framework`、OpenAI、MCP 等条件决定要渲染哪些模板
- 渲染时统一遵循“模板文件在 `assets/`，目标文件在项目目录；模板后缀不落到项目产物中”的规则
- 模板渲染时，凡是涉及包路径或模块引用的位置，必须统一来自 `{{ package_name }}` 变量，禁止在渲染逻辑中手写具体包名字符串

### Step 2: 创建标准目录结构

**核心原则：当前目录生成 → 模板驱动 → 一次完成**

- **绝不创建** `PROJECT_ROOT` 本身（当前目录就是根目录）
- 创建或确保以下子目录存在
- 统一一次性生成目标文件，避免在模板之间来回确认或分批中断
- 任何模板渲染失败都要立即报错，不能继续生成半成品项目
- 默认按完整项目生成；如遇重名文件，优先提示并避免覆盖用户已有定制内容

**标准目录结构**：

```text
PROJECT_ROOT（当前目录）/
├── src/
│   └── {{ package_name }}/
│       ├── __init__.py
│       ├── config.py
│       ├── exceptions.py
│       ├── main.py               # framework=fastapi 时含路由注册点位
│       └── routers/              # 仅当有额外集成需求时创建
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_main.py
│   └── test_startup.py
├── scripts/
│   ├── start.sh
│   └── stop.sh
├── tools/
│   ├── check_structure.py
│   └── smoke_startup.py
├── logs/                      # 空目录，写入 .gitkeep
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── Makefile
└── README.md
```

创建完后在 `logs/` 目录写入 `.gitkeep` 文件。

### Step 3: 生成源代码文件

**执行要求：** 批量读取 `assets/` 下需要的模板文件，使用当前解析出的变量完成渲染，然后直接写入目标文件路径；不要在文件之间插入额外确认。

**额外要求：** `src/`、`tests/`、`tools/`、`scripts/`、`Makefile`、`README.md` 中凡是出现包导入、模块路径、包目录名的地方，都必须严格使用同一个最终 `package_name`，不能出现与之不一致的旧值、候选值或推测值。

根据 `framework` 和额外集成需求选择对应的模板：

| 条件 | 模板文件 | 目标路径 |
|------|----------|----------|
| 总是生成 | `init.py` | `src/{{ package_name }}/__init__.py` |
| 总是生成 | `config.py` | `src/{{ package_name }}/config.py` |
| 总是生成 | `exceptions.py` | `src/{{ package_name }}/exceptions.py` |
| `framework==script` | `main.py` | `src/{{ package_name }}/main.py` |
| `framework==fastapi` | `main_fastapi.py` | `src/{{ package_name }}/main.py` |
| `framework==flask` | 同 script（使用 `main.py`） | `src/{{ package_name }}/main.py` |
| 检测到 OpenAI | `openai_service.py` | `src/{{ package_name }}/openai_service.py` |
| 检测到 MCP | `mcp_service.py` | `src/{{ package_name }}/mcp_service.py` |
| 检测到任一额外集成 | — | 创建 `routers/__init__.py`（空包文件） |
| 检测到任一额外集成 | `router_example.py.j2` | `src/{{ package_name }}/routers/example_router.py`（可删除） |

**配置项注入**：在生成 `config.py` 时，根据检测到的集成需求，在 `# ─── 服务/工具配置（按需添加） ───` 注释块下方追加对应的配置项。

**路由注册注入**：在生成 `main_fastapi.py.j2` 时，找到 `# ─── 子路由注册 ───` 注释块，替换为实际的 `import` 和 `include_router` 代码。

### Step 4: 生成测试文件

| 模板文件 | 目标路径 | 说明 |
|----------|----------|------|
| `test_main.py` | `tests/test_main.py` | 主模块测试 |
| `test_startup.py` | `tests/test_startup.py` | 启动冒烟测试 |
| `conftest.py` | `tests/conftest.py` | pytest 配置 |
| `init_test.py` | `tests/__init__.py` | 测试包标记 |

### Step 5: 生成脚本文件

对生成的 `.sh` 文件执行 `chmod +x`。

| 模板文件 | 目标路径 | 说明 |
|----------|----------|------|
| `start.sh` | `scripts/start.sh` | 启动脚本 |
| `stop.sh` | `scripts/stop.sh` | 停止脚本 |

### Step 6: 生成检查与启动验证脚本

| 模板文件 | 目标路径 | 说明 |
|----------|----------|------|
| `check_structure.py` | `tools/check_structure.py` | 校验目录结构与关键文件是否存在 |
| `smoke_startup.py` | `tools/smoke_startup.py` | 验证项目入口是否可导入、可启动 |

### Step 7: 生成项目配置文件

| 模板文件 | 目标路径 | 说明 |
|----------|----------|------|
| `gitignore` | `.gitignore` | Git 忽略规则 |
| `pyproject.toml` | `pyproject.toml` | 项目元数据与构建配置 |
| `requirements.txt` | `requirements.txt` | 依赖清单（按额外需求追加依赖） |
| `env.example` | `.env.example` | 环境变量模板 |
| `Makefile` | `Makefile` | 常用命令封装 |

往 `requirements.txt` 追加依赖的规则：
- 检测到 OpenAI → 追加 `openai>=1.0.0`
- 检测到 MCP → 追加 `httpx>=0.27.0`
- 检测到 fastapi → 由模板自带 `fastapi` 和 `uvicorn`

### Step 8: 生成 README.md

| 模板文件 | 目标路径 |
|----------|----------|
| `README.md` | `README.md` |

### Step 9: 初始化 Git 仓库（默认跳过）

检查 `PROJECT_ROOT` 下是否已存在 `.git` 目录：
- 如果**已存在** Git 仓库，跳过初始化步骤
- 如果**不存在** Git 仓库，只有在用户明确希望顺便初始化版本控制时才执行：
  - `git init`
  - `git add .`
  - `git commit -m "chore: init {{ project_name }} project"`

### Step 10: 项目完整性校验

生成完成后，自动执行以下校验；优先把检查合并成尽量少的命令，避免重复安装、重复导入、重复冒烟。

0. **模板残留检查** — 确认最终生成的项目目录中不存在模板后缀文件；若存在，说明模板未正确渲染，立即报错。

0.5. **`package_name` 一致性检查** — 确认所有生成产物使用的是同一个最终 `package_name`：
   - `src/{{ package_name }}/` 目录存在，且不存在本次运行中误生成的其他候选包目录
   - `tests/`、`tools/`、`scripts/`、`Makefile`、`README.md`、`pyproject.toml` 中涉及模块导入、模块字符串、包路径的位置，均引用最终 `package_name`
   - 若发现 `test_create` / `test_create_app` 这类并存的包名漂移现象，立即报错并在继续校验前修复

1. **目录和文件完整性检查** — 确认以下关键路径均存在：

   **核心文件（必须存在）：**
   - `src/{{ package_name }}/__init__.py`
   - `src/{{ package_name }}/main.py`
   - `src/{{ package_name }}/config.py`
   - `tests/test_main.py`
   - `scripts/start.sh`
   - `scripts/stop.sh`
   - `tools/check_structure.py`
   - `tools/smoke_startup.py`
   - `.gitignore`
   - `pyproject.toml`
   - `requirements.txt`
   - `Makefile`
   - `README.md`

   **条件文件（framework / 集成相关）：**
   - 如果检测到额外集成：`src/{{ package_name }}/routers/__init__.py`
   - 如果检测到 OpenAI：`src/{{ package_name }}/openai_service.py`
   - 如果检测到 MCP：`src/{{ package_name }}/mcp_service.py`

   **检查结果处理：**
   - 列出所有缺失的文件（如果有）
   - 列出所有新建的文件
   - 列出所有已存在的文件（未被覆盖）
   - 如果有缺失文件，立即报错并终止

2. **Python 语法检查** — 对所有新生成的 `.py` 文件执行一次批量检查：
   ```bash
   python -m compileall src tests tools
   ```
   确保语法正确，无语法错误。

3. **结构检查与启动冒烟** — 在 `PROJECT_ROOT` 下先执行结构检查，再执行启动冒烟：
   ```bash
   python tools/check_structure.py
   python tools/smoke_startup.py
   ```
   验证生成结果是否与 skill 约定的目录结构一致，并且入口能够导入、可启动。

4. **包导入与 pytest** — 在 `PROJECT_ROOT` 下执行一次安装后直接导入和测试：
   ```bash
   python -m pip install -e .
   python -c "from {{ package_name }} import __version__; print(f'包导入成功: {{ package_name }} v{__version__}')"
   pytest
   ```
   验证包可被 Python 正确导入。若导入失败，检查是否有模块级 Service 实例化导致的异常，修复后重试。

5. **脚本可执行性检查** — 确保启动和停止脚本可执行：
   ```bash
   # Linux/macOS: 检查执行权限
   ls -l scripts/start.sh scripts/stop.sh
   # Windows: .sh 文件需要 Git Bash 等 POSIX shell 执行
   ```

6. **生成校验报告** — 汇总以上检查结果，生成简洁的校验报告，包括：
   - ✅ 模板渲染：通过/失败（是否有 `.j2` 残留）
   - ✅ package_name 一致性：通过/失败（是否所有生成文件都引用同一个最终包名）
   - ✅ 文件完整性：通过/失败
   - ✅ 语法检查：通过/失败（列出失败的文件）
   - ✅ 结构检查脚本：通过/失败
   - ✅ 包导入：通过/失败
   - ✅ 启动冒烟测试：通过/失败
   - ✅ pytest：通过/失败
   - ✅ 脚本权限：通过/失败

## 输出要求

- 输出新建目录与文件清单
- 说明哪些文件来自 `assets/` 模板
- 显式输出本次最终采用的 `package_name`，并说明它是否因标准库重名检查而追加过 `_app`
- 给出推荐验证顺序：`make install` → `make check-structure` → `make smoke` → `make test` → `make run`
- 若检测到已有文件未覆盖，明确指出哪些文件需要用户手动合并
- 尽量把输出控制在一轮生成 + 一轮校验总结内，不要把中间状态拆成多次确认

## 实施约束

- 保持模板变量命名稳定，便于后续维护者修改 `assets/` 中的模板
- 优先生成跨平台的 Python 检查脚本；shell 脚本只承担启动/停止职责
- 不生成 Docker 目录，不引用 Docker 命令，不把容器部署作为默认路径

### Step 11: 汇报结果

向用户汇报已生成的项目结构概览，格式：

```text
✅ Python 项目 "{{ project_name }}" 已生成
   ├── 路径: {{ PROJECT_ROOT }}（当前目录）
   ├── 框架: {{ framework }}
   ├── Python: {{ python_version }}
   ├── 包名: {{ package_name }}
   └── 集成: openai, mcp, ...（按实际情况列出）

📊 生成统计：
   ├── 新建文件: X 个
   ├── 已存在文件: Y 个（未覆盖）
   └── 目录结构: 完整

🎯 校验结果：
   ├── 模板渲染: ✅ 通过
   ├── package_name 一致性: ✅ 通过
   ├── 文件完整性: ✅ 通过
   ├── Python 语法: ✅ 通过
   ├── 结构检查脚本: ✅ 通过
   ├── 包导入测试: ✅ 通过
   ├── 启动冒烟测试: ✅ 通过
   ├── pytest: ✅ 通过
   └── 脚本权限: ✅ 通过

快速开始:
   make install
   make check-structure
   make smoke
   make test
   make run
   make run
```

## 模板变量说明

所有模板文件中可使用以下变量：

| 变量 | 说明 |
|------|------|
| `{{ project_name }}` | 项目名称 |
| `{{ package_name }}` | Python 包名（snake_case） |
| `{{ description }}` | 项目描述 |
| `{{ python_version }}` | Python 版本号字符串 |
| `{{ author }}` | 作者名 |

## 团队使用建议

- 先将本 skill 目录提交到仓库中的 `.github/skills/python-scaffold/`
- 模板个性化修改统一在 `assets/` 中进行，不直接改生成产物作为团队基线
- 如果团队后续增加数据库、缓存、消息队列等集成，继续按“新增 `.j2` 模板 + 在 `SKILL.md` 中登记渲染条件”的方式扩展
| `{{ framework }}` | 框架类型: `script` / `fastapi` / `flask` |

## 最佳实践

### 1. 懒初始化原则

所有 Service 类（OpenAI、MCP、数据库等）必须使用懒初始化模式：

```
# ❌ 错误：导入时校验 → 阻塞整个应用加载
openai_service = OpenAIService()       # 模块级别实例化

# ✅ 正确：调用时初始化 → 按需抛异常
@property
def client(self):
    if self._client is None:
        if not config.OPENAI_API_KEY:
            raise AppError(...)        # 调用时才抛
        self._client = OpenAI(...)
    return self._client
```

### 2. 路由模块化

FastAPI 项目应将不同领域的功能拆分为独立的路由模块，放在 `routers/` 目录下，统一在 `main.py` 的 `# ─── 子路由注册 ───` 处注册。

### 3. 配置分段

`config.py` 使用 `# ───` 注释标记进行分段，新集成需求在 `# ─── 服务/工具配置（按需添加） ───` 下方追加配置项。

### 4. 补充现有项目的建议

当在现有项目上使用此技能时：
- 技能会检查现有文件，默认不覆盖
- 如果确实需要重新生成某个文件，请手动删除或重命名后重新运行技能
- 对于已存在的自定义文件，技能不会修改其内容
- 生成的校验报告会清晰显示哪些是新建、哪些是已存在
