---
alwaysApply: true
version: 2.0.0
lastUpdated: 2026-09-08
description: cut-server 项目概述（v2.0 重写）。基于旧漫剧剪辑工具 `AI漫剧剪辑师旧参考项目代码/` 重写为前后端分离架构。包含项目目标、技术栈、功能范围（漫剧剪辑 7 步 + 登录注册 + 会员体系 + 管理员后台）和关键约束。
---

# cut-server 项目概述

> 本文档是 cut-server（漫剧推广素材剪辑师后端）的定制规则，仅适用于本项目。
> v2.0 重写原因：v1.0 误将本项目与"股票/关注/RBAC"无关功能混入，已删除重写。

## 项目名称

**cut-server** — 漫剧推广素材剪辑师后端服务（前后端分离）

## 项目目标

构建一个**标准化、规范、本地化**的漫剧推广视频生产工具后端服务。完整复刻旧版 7 步业务功能，并补齐用户体系与会员体系：

- 完整复刻旧版漫剧剪辑师全部 7 步业务功能（前后端分离重构）
- 用户体系：注册、登录、个人中心、修改密码
- 会员体系：Free / Pro / Enterprise 三档，管理员手动分配
- 管理员后台：用户管理、会员分配、全局配置
- 接口契约严格 OpenAPI 3.0，前后端零歧义
- **本项目不涉及股票、关注、社交功能**

## 技术栈

| 类别 | 技术选型 | 说明 |
|------|---------|------|
| 编程语言 | Python 3.11+ | |
| Web 框架 | FastAPI + Uvicorn | 异步高性能，端口 8000 |
| 数据库 | **PostgreSQL 18** | 本地已安装，密码 1234，库名 `cut_video` |
| ORM | SQLAlchemy 2.x | 同步/异步双模式 |
| 数据库驱动 | psycopg[binary] >= 3.1 | PostgreSQL 18 适配 |
| 迁移 | Alembic | 数据库版本化迁移 |
| 鉴权 | JWT Bearer Token | 30 天有效 |
| 密码 | bcrypt (passlib) | 哈希存储 |
| 任务调度 | asyncio + 内存队列 | 长任务异步化 |
| 视频处理 | ffmpeg 系统二进制 + ffmpeg-python | subprocess 封装 |
| TTS | edge-tts（首选）+ pyttsx3（Windows 兜底） | |
| AI 接入 | OpenAI Python SDK（兼容 DeepSeek） | |
| 网络搜索 | httpx + BeautifulSoup | Bing/DuckDuckGo |
| 文件存储 | 本地文件系统 → MinIO/S3（v4.1） | v4.0 阶段本地 |
| 测试 | pytest + pytest-asyncio + httpx | 单元 + 集成 |
| 代码规范 | ruff + mypy + black | |

## 项目范围

### A. 核心业务（来自旧 PRD v1.2 · 100% 复刻）

1. **多项目管理**：新建/打开/复制/删除/封面 emoji
2. **剧集管理**（v3.0 引入）：一个项目可有多集
3. **创作流程**：一个剧集可发起多次"创作"（每次创作独立版本）
4. **Step1 输入漫剧信息**：标题、作者、简介、素材目录、知识库构建
5. **Step2 AI 拆解 + 搜索**：关键词/价值点/建议标题 + Bing/DuckDuckGo 搜索
6. **Step3 口播长文**：基于关键词+大纲+搜索文章生成完整口播文案
7. **Step4 双线并行**：TTS 音频合成 + 视频随机标记时间段
8. **Step5 虚拟串播预览**：0 IO 预览，video.currentTime 模拟
9. **Step6 确认裁切**：ffmpeg 按标记 JSON 切片 + concat 合并
10. **Step7 合成导出**：音视频合成 + 字幕烧录 → 导出 mp4

### B. 用户与会员体系（v4.0 新增·简化版）

11. **用户体系**：
    - 注册（用户名 + 密码）
    - 登录（JWT，30 天有效）
    - 个人资料（头像、昵称、简介、修改密码）
    - 我的项目/我的创作（按用户隔离）

12. **会员等级**：
    - **Free**：默认，3 个项目，50 次 Step 调用/月，500MB 存储
    - **Pro**：20 个项目，500 次 Step 调用/月，5GB 存储
    - **Enterprise**：无限（-1 表示无限）
    - 分配方式：**仅管理员后台手动开/续/停**，v4.0 不接入在线支付
    - 用户可查看自己的会员状态与配额使用情况

13. **管理员后台**：
    - 用户列表（搜索、改密码、改会员等级、停用/启用）
    - 会员分配（开/续/停会员，记录操作人）
    - 全局配置（API Key、TTS 引擎、搜索引擎等）
    - 操作日志（管理员关键操作审计）

### C. 非业务能力

14. **历史版本与回滚**：每 Step 结果存 generation_history 表（version 自增）
15. **任务系统**：>3s 长任务异步化，返回 task_id，前端轮询
16. **配置系统**：全局配置表（API Key、TTS 引擎、搜索引擎等）
17. **健康检查** `/api/health`（含 ffmpeg/ffprobe 可用性、PostgreSQL 连接状态）

### 显式排除（NOT in scope）

- ❌ 关注系统 / 粉丝 / 动态流
- ❌ 股票行情 / 自选股 / K 线
- ❌ 完整 RBAC（角色-权限-资源映射）
- ❌ 公开用户主页
- ❌ 评论 / 点赞 / 收藏
- ❌ 在线支付集成
- ❌ 邮件发送 / 短信通知
- ❌ 多租户 / 组织架构

## 非功能需求

- **性能**：单实例支持 100 并发；长任务用异步队列
- **可扩展性**：新 Step、新业务模块按四层架构追加
- **可靠性**：任务失败重试，结果可追溯
- **安全性**：JWT 鉴权、密码 bcrypt、路径遍历防护、SQL 注入防护（ORM）
- **可观测性**：traceId 贯穿前后端，结构化 JSON 日志

## 关键约束

1. **接口契约优先**：任何接口先在 `docs/openapi.yaml` 定义，再编码
2. **错误码体系**：遵循 `.trae/rules/shared/03-error-code-system.md`，格式 `{DOMAIN}_{HTTP}_{SEQ}`
3. **统一响应**：`{code: number, msg: string, data: any, traceId: string}`
4. **snake_case 字段**：后端 Python 风格，前端通过 codegen 转 camelCase
5. **traceId 传递**：每个请求注入 traceId，日志必须包含
6. **四层架构**：Controller → Service → Manager → Model，严格分层
7. **数据库迁移**：所有 schema 变更走 Alembic，必须有 downgrade
8. **旧代码仅参考**：禁止直接复用 `AI漫剧剪辑师旧参考项目代码/` 的代码，仅复用思路、字段、算法
9. **会员配额**：每次 Step 调用前校验用户配额，超额返回 HTTP 402
10. **管理员唯一入口**：所有管理员操作必须经 `/api/admin/*` 并校验 `is_admin=true`

## 角色（简化版·仅两档）

```python
# 角色判定只用一个布尔字段，简化 v4.0 模型
class UserRole(str, Enum):
    USER  = "user"   # 普通用户（含会员分级）
    ADMIN = "admin"  # 管理员（可访问 /api/admin/*）
```

未来需要更细粒度权限时再升级为完整 RBAC。

## 架构层级

```
Controller 层 (app/controllers/)   → 参数校验、鉴权、管理员判定、响应封装
    ↓
Service 层 (app/services/)         → 单领域业务逻辑、事务边界、领域异常
    ↓
Manager 层 (app/managers/)         → 第三方调用封装（ffmpeg/TTS/AI）、跨服务编排
    ↓
Model 层 (app/models/)             → SQLAlchemy ORM、Pydantic Schema
```

## 项目目录结构

```
cut-server/
├── app/
│   ├── main.py                 # FastAPI 入口
│   ├── core/                   # 配置、日志、异常、安全
│   │   ├── config.py           # Settings（读环境变量）
│   │   ├── database.py         # SQLAlchemy 引擎 + Session
│   │   ├── logger.py           # JSON 日志 + traceId
│   │   ├── exceptions.py       # 业务异常体系
│   │   ├── security.py         # JWT + bcrypt
│   │   ├── deps.py             # 依赖注入：get_db / get_current_user / get_admin_user
│   │   └── trace.py            # traceId 中间件
│   ├── controllers/            # 路由层（按业务模块切分）
│   │   ├── auth.py             # 注册/登录/登出
│   │   ├── users.py            # 个人资料
│   │   ├── projects.py
│   │   ├── episodes.py
│   │   ├── creations.py
│   │   ├── step1.py ~ step7.py
│   │   ├── tasks.py
│   │   ├── files.py
│   │   ├── configs.py
│   │   ├── memberships.py      # 我的会员
│   │   └── admin/              # 管理员后台
│   │       ├── users.py
│   │       ├── memberships.py
│   │       └── configs.py
│   ├── services/               # 业务逻辑
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── project_service.py
│   │   ├── step1_service.py ~ step7_service.py
│   │   ├── membership_service.py
│   │   └── admin_service.py
│   ├── managers/               # 第三方封装
│   │   ├── ffmpeg_mgr.py
│   │   ├── tts_mgr.py
│   │   ├── ai_mgr.py
│   │   ├── search_mgr.py
│   │   ├── kb_mgr.py
│   │   └── prompts/            # Prompt 模板
│   ├── models/                 # ORM
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── episode.py
│   │   ├── creation.py
│   │   ├── step_result.py
│   │   ├── history.py
│   │   ├── task.py
│   │   ├── config.py
│   │   ├── membership.py
│   │   └── audit_log.py        # 管理员操作审计
│   ├── schemas/                # Pydantic Schema
│   │   ├── common.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── ...
│   ├── utils/
│   │   ├── ffmpeg.py
│   │   ├── ffprobe.py
│   │   ├── srt.py
│   │   └── safe_path.py        # 路径遍历防护
│   └── tasks/
│       ├── task_queue.py       # asyncio 队列
│       └── task_worker.py      # 异步 worker
├── alembic/                    # 数据库迁移
│   ├── env.py
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   ├── openapi.yaml            # API 契约
│   └── 04-接口契约.md
├── .trae/                      # ⭐ rules + skills 已加载
├── pyproject.toml
└── README.md
```

## 核心数据模型（11 张表）

| 表 | 关键字段 | 说明 |
|----|---------|------|
| `users` | id, username, password_hash, email, display_name, avatar_url, bio, is_admin, membership_tier, is_active, created_at | 用户 |
| `projects` | id, user_id, title, author, intro, cover, video_dir, intro_dir, status, created_at, updated_at | 项目 |
| `episodes` | id, project_id, user_id, title, status, created_at | 剧集 |
| `creations` | id, episode_id, user_id, current_step, status, created_at, updated_at | 创作 |
| `step_results` | id, creation_id, step_no, version, payload(JSON), created_at | 每步当前版本 |
| `generation_history` | id, creation_id, step_no, version, payload, created_at | 历史快照 |
| `tasks` | id, user_id, type, status, progress, payload, result, error, started_at, finished_at | 异步任务 |
| `files` | id, user_id, path, size, mime, created_at | 文件元数据 |
| `configs` | key, value, scope(user_id NULL=全局) | 配置 |
| `memberships` | id, user_id, tier, status, started_at, expires_at, assigned_by, created_at | 会员 |
| `audit_logs` | id, admin_user_id, action, target_type, target_id, payload, created_at | 管理员操作审计 |

## 会员配额表（硬约束·配置化）

```python
QUOTA_TABLE = {
    "free":       {"projects": 3,   "monthly_step_calls": 50,   "storage_mb": 500},
    "pro":        {"projects": 20,  "monthly_step_calls": 500,  "storage_mb": 5000},
    "enterprise": {"projects": -1,  "monthly_step_calls": -1,   "storage_mb": -1},  # -1 = 无限
}
```

超额返回 HTTP 402 + 错误码 `MEMBER_402_001`。

## 与前端协作约定

- 前端服务：`cut-web`（React + TS + Vite）
- 接口契约：`docs/openapi.yaml`（本项目维护）+ 后端 `/openapi.json`（运行时）
- 前端 TS 类型：由 `openapi-typescript` 从 openapi.yaml 自动生成
- 鉴权：JWT Bearer Token，请求头 `Authorization: Bearer <token>`
- 统一响应：`{code, msg, data, traceId}`
- traceId：后端中间件注入，日志 + 响应头 `X-Trace-Id` 双写

## 启动与运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 数据库迁移（首次会自动创建库 alembic_version 表）
alembic upgrade head

# 3. 启动开发服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. 访问
# Swagger UI:    http://localhost:8000/docs
# ReDoc:         http://localhost:8000/redoc
# 健康检查:      http://localhost:8000/api/health
```

## 环境变量（`.env`）

```bash
DATABASE_URL=postgresql+psycopg://postgres:1234@localhost:5432/cut_video
JWT_SECRET=change-me-in-production
JWT_EXPIRE_DAYS=30
JWT_ALGORITHM=HS256

TTS_DEFAULT_ENGINE=edge-tts

# ===== AI 大模型（MiniMax M3 · OpenAI 兼容协议） =====
AI_PROVIDER=minimax
# 从 MiniMax 控制台获取：https://platform.minimaxi.com/user-center/basic-information/interface-key
MINIMAX_API_KEY=sk-cp-***REDACTED***   # 实际 Key 写在本地 .env（不提交）
MINIMAX_BASE_URL=https://api.minimax.cn/v1
MINIMAX_MODEL=MiniMax-M3

SEARCH_ENGINE=duckduckgo
BING_SEARCH_KEY=

WORKDIR=./workspace
LOG_LEVEL=INFO

# 第一个管理员（首次启动时若 users 表为空，可通过环境变量指定）
BOOTSTRAP_ADMIN_USERNAME=admin
BOOTSTRAP_ADMIN_PASSWORD=admin123456
```

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 2.0.0 | 2026-09-08 | 重写。删除误加的股票/关注/完整RBAC。改为 PostgreSQL + 简化角色(admin/user) |
| 1.0.0 | 2026-09-08 | 初版（已被 2.0 取代） |

---

_由 AI 起草，待用户确认定稿_