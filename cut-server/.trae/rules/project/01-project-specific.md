---
alwaysApply: true
version: 2.0.0
lastUpdated: 2026-09-08
description: cut-server 项目特定规则（v2.0）。业务术语、数据约束、复刻旧项目注意事项、与前端的硬约束。
---

# cut-server 项目特定规则

> 本文档是 cut-server 的项目级硬约束，补充共享层规则的不足。
> 与共享层 + Python 栈层规则**叠加生效**（冲突时以本文档为准）。
> v2.0 重写：删除股票/关注相关条款，调整为 PostgreSQL + 简化角色。

## 1. 业务术语词典（前后端统一）

| 中文 | 英文（snake_case） | 说明 |
|------|--------------------|------|
| 漫剧 | manga | 用户创作的"作品"单位 |
| 项目 | project | 漫剧元信息容器（含素材目录） |
| 剧集 | episode | 项目下的具体一集 |
| 创作 | creation | 一次"7 步生成"流程实例 |
| 步骤 | step | 7 步流程中的某一步（1~7） |
| 口播文案 | script | Step3 生成的长文 |
| TTS 音频 | tts_audio | Step4a 生成的 mp3 |
| 视频标记 | video_marks | Step4b 生成的时间段 JSON |
| 切片段 | clip | 视频标记对应的实际片段 |
| 成品 | final_video | Step7 导出的 mp4 |
| 会员等级 | membership_tier | free / pro / enterprise |
| 配额 | quota | 月度 Step 调用/项目数/存储上限 |

## 2. 数据库（PostgreSQL 18 · 本地已装）

```bash
# 服务名：postgresql-x64-18（已 Running）
# 连接：postgres / 1234 / localhost:5432
# 开发库：cut_video
DATABASE_URL=postgresql+psycopg://postgres:1234@localhost:5432/cut_video
```

**库表准备**：

```sql
-- 首次手动创建库（psql / pgAdmin）
CREATE DATABASE cut_video
  WITH ENCODING='UTF8'
       LC_COLLATE='en_US.UTF-8'
       LC_CTYPE='en_US.UTF-8'
       TEMPLATE=template0;

-- Alembic 迁移会自动建表
```

**驱动**：`psycopg[binary] >= 3.1`（PostgreSQL 18 官方推荐）。

## 3. 数据迁移规则（旧项目兼容）

旧项目 SQLite 表结构在 `AI漫剧剪辑师旧参考项目代码/app/database/db.py`，新版 PostgreSQL 必须保证字段兼容：

| 兼容项 | 处理方式 |
|--------|---------|
| 旧 `users` 表 | 字段保留（id, username, password_hash, created_at）；新增 is_admin / email / display_name / avatar_url / bio / membership_tier / is_active |
| 旧 `projects` 表 | 全部字段保留，新增 user_id（必填）、status |
| 旧 `episodes` 表 | 字段保留，新增 user_id |
| 旧 `creations` 表 | 字段保留，新增 user_id（冗余便于权限校验） |
| 旧 `generation_history` 表 | 直接迁移 |
| 旧 Token 字段 | **新版切到 JWT**，提供一次性迁移脚本读取旧 token → 重新签发 JWT |

## 4. 鉴权与角色（简化版）

### 4.1 角色判定（v2.0 仅两档）

```python
# users 表 is_admin 布尔字段即可，不要做角色枚举
is_admin: bool = False  # True → 管理员，访问 /api/admin/*
```

### 4.2 JWT Token

```python
{
  "sub": "<user_id>",
  "username": "<username>",
  "is_admin": true|false,
  "membership_tier": "free|pro|enterprise",
  "exp": <unix_timestamp>,
  "iat": <unix_timestamp>
}
```

### 4.3 权限校验层级

```
请求进入 → JWT 中间件解析 → 设置 request.state.user
        → Depends(get_current_user) 注入
        → Depends(get_admin_user) 注入（仅管理员接口）
        → 资源所有权检查（resource.user_id == current_user.id）
        → 业务执行
```

**禁止在 service 层做权限校验**。

## 5. 会员配额硬约束

```python
QUOTA_TABLE = {
    "free":       {"projects": 3,   "monthly_step_calls": 50,   "storage_mb": 500},
    "pro":        {"projects": 20,  "monthly_step_calls": 500,  "storage_mb": 5000},
    "enterprise": {"projects": -1,  "monthly_step_calls": -1,   "storage_mb": -1},
}
```

**实现要点**：
- 每次 Step 接口调用前用 `Depends(check_quota)` 校验
- 月度计数用 `usage_records` 表（user_id + year_month + step_calls + storage_bytes）
- 项目配额在 `POST /api/projects` 前校验
- 超额返回 HTTP 402 + `{code: "MEMBER_402_001", msg: "会员配额不足"}`

## 6. 异步任务硬约束

- 任何耗时 **>3 秒**的接口必须异步化
- 任务状态：`pending → running → completed / failed / cancelled`
- `progress` 字段（0~100）反馈
- 任务最长生命周期 **24 小时**，超时自动 failed
- 前端轮询间隔 **≥ 2 秒**

## 7. 文件路径安全

```python
WORKDIR = Path("./workspace").resolve()

def safe_join(workdir: Path, user_path: str) -> Path:
    target = (workdir / user_path).resolve()
    if not str(target).startswith(str(workdir)):
        raise PathTraversalError("路径越界")
    return target
```

**禁止**直接 `os.path.join(user_input)` 拼路径。

## 8. TTS 引擎选择策略

| 优先级 | 引擎 | 条件 |
|--------|------|------|
| 1 | edge-tts | 网络可用 + 配置启用 |
| 2 | pyttsx3 | Windows 平台 + 配置启用 |
| 3 | 报错 | 前两者都不可用 |

引擎选择结果缓存到本次任务。

## 9. AI Prompt 模板管理

`app/managers/prompts/` 目录：

```
prompts/
├── step2_keywords.md
├── step2_search.md
├── step3_outline.md
├── step3_script.md
└── config_test.md
```

每个 .md 含 YAML frontmatter：

```yaml
---
name: step2_keywords
version: 1.0.0
description: 从漫剧简介提取关键词
provider: minimax              # 使用 MiniMax M3（OpenAI 兼容协议）
model: MiniMax-M3
temperature: 0.7
max_tokens: 2000
---
```

加载：`PromptTemplate.from_file("prompts/step2_keywords.md")`

## 10. 旧项目功能复刻硬清单（防遗漏·v2.0）

> 下列功能必须在新版 100% 实现，缺一项视为阶段未通过。

### 10.1 业务功能

- [ ] 多项目管理（新建/打开/复制/删除 + 封面 emoji）
- [ ] 项目列表分页 + 搜索
- [ ] 剧集管理（v3.0 三级结构）
- [ ] 创作流程（同一剧集多次创作实例）
- [ ] Step1~7 完整业务
- [ ] 步骤锁定（前步未完成后步置灰）— 前端
- [ ] 任意步骤"返回上一步"
- [ ] 每步"重新执行"按钮
- [ ] 每步结果存 PostgreSQL + 历史版本（version 自增）
- [ ] TTS 双引擎降级（edge-tts → pyttsx3）
- [ ] Step5 虚拟预览 0 IO（video.currentTime 模拟）
- [ ] 标记总时长比音频长 2 秒（留余量）
- [ ] 时长不匹配只提示不强制平衡
- [ ] ffmpeg 裁切只执行一次（Step6 用户确认后才执行）
- [ ] 字幕烧录（SRT + ffmpeg subtitle filter）

### 10.2 用户与会员

- [ ] 用户注册（用户名+密码）
- [ ] 用户登录（JWT 30 天）
- [ ] 个人资料 CRUD（昵称/简介/头像 URL）
- [ ] 修改密码
- [ ] 我的会员状态查询
- [ ] 我的配额使用查询
- [ ] 管理员：用户列表（分页+搜索+筛选）
- [ ] 管理员：改用户密码 / 停用启用
- [ ] 管理员：开/续/停会员（记录 assigned_by）
- [ ] 管理员：全局配置 CRUD（含测试连接）
- [ ] 管理员：操作审计日志

## 11. 与前端协作的硬约束

| 项 | 规则 |
|----|------|
| 字段命名 | 后端 snake_case，前端 TS 类型由 codegen 转 camelCase |
| 时间格式 | ISO 8601（`2026-09-08T10:30:00Z`） |
| 数字 | 价格用 `Decimal`（字符串传输），步数/计数用 `int` |
| 布尔 | 用 `is_xxx` / `xxx_enabled`，禁止 `0/1` |
| 枚举 | 字符串枚举，不用数字 |
| 错误响应 | 必须含 `traceId` |
| 分页 | `{page, pageSize, total, items}`，page 从 1 开始 |
| 列表查询 | 默认 `pageSize=20, page=1`，最大 `pageSize=100` |

## 12. 数据库迁移纪律

- Alembic 任何 schema 变更都有 upgrade + downgrade
- 破坏性变更分两步：先加新字段 + 双写，再切读 + 删旧字段
- 大表变更（>100 万行）用 `op.execute()` 分批执行

## 13. 测试纪律

- 每个 service 单元测试覆盖率 ≥ 80%
- 每个 controller 至少 1 happy + 2 error 集成测试
- 会员配额必须有专门测试（每档用户 + 每类操作）
- 管理员接口必须有 is_admin 校验测试
- 异步任务必须有 mock 测试
- E2E 用 Playwright 覆盖登录 → 7 步完整流程

## 14. 性能纪律

- 单 SQL 必须有索引依据（EXPLAIN）
- 列表必须分页，禁止 `SELECT *`
- 用户配置、项目元数据用内存 LRU（5min TTL）
- AI/TTS/ffmpeg 调用必须有超时（默认 60s）

## 15. 日志纪律

```python
{
    "timestamp": "2026-09-08T10:30:00.123Z",
    "level": "INFO",
    "trace_id": "abc123",
    "user_id": "u_xxx",
    "module": "controllers.step1",
    "message": "Step1 加载完成",
    "duration_ms": 234
}
```

**禁止**打印完整密码、API Key、用户隐私；禁止用 `print()` 替代 logger。

## 16. 错误响应统一格式

```json
{
  "code": "PROJECT_404_001",
  "message": "项目不存在",
  "detail": "Project ID xxx not found",
  "traceId": "abc123",
  "timestamp": "2026-09-08T10:30:00Z",
  "data": null
}
```

错误码格式：`{DOMAIN}_{HTTP_STATUS}_{SEQ}`，详见共享层规则 03。

## 17. 不允许的反模式

| 反模式 | 正确做法 |
|--------|---------|
| 在 controller 写业务逻辑 | 业务下沉到 service |
| 在 service 写 SQL | SQL 在 model 层 |
| 直接 `import requests` | 用统一 httpx 客户端 |
| 用全局变量存配置 | 用 `core.config.Settings` |
| 用 `try/except` 吞异常 | 记录日志后 re-raise 或转业务异常 |
| 把 token 存数据库 | 用 JWT 无状态 |
| 用 `os.system()` 调 ffmpeg | 用 `subprocess.run(..., check=True)` |
| 硬编码文件路径 | 用 `WORKDIR` 环境变量 |
| 手写 SQL 字符串拼接 | 用 SQLAlchemy ORM / 参数化 |

## 18. 阶段交付纪律

每个开发阶段结束必须：
1. `pytest` 覆盖率达标
2. `ruff check` + `mypy` 无 error
3. 更新 `docs/openapi.yaml`（如新增接口）
4. 更新 `plan/01-开发进度.md` + `plan/08-代码日志.md`
5. `CHANGELOG.md` 记录变更

## 19. 已知技术债务与决策记录

| 议题 | 决策 | 原因 |
|------|------|------|
| 数据库 | PostgreSQL 18（取代原计划的 SQLite） | 用户本地已装，零配置 |
| 鉴权 | JWT | 前后端分离标配 |
| 角色模型 | 仅 `is_admin` 布尔字段（不做枚举） | 用户明确要求简化 |
| 会员支付 | v4.0 仅管理员手动分配 | 用户明确要求 |
| TTS | edge-tts 优先 | 旧项目已验证 |
| 视频处理 | ffmpeg 系统二进制 | 旧项目已验证 |
| AI 调用 | OpenAI SDK 兼容 DeepSeek | 用户常用 |
| 文件存储 | 本地文件系统 | v4.1 升级 MinIO/S3 |
| 邮件/短信 | 不实现 | 用户明确排除 |

---

_由 AI 起草，待用户确认定稿_