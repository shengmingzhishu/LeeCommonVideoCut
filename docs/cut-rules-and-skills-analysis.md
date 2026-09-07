# cut-server / cut-web · Rules 与 Skills 体系评估与建议

> **评估目标**：分析 `cut-server` 与 `cut-web` 两个项目当前携带的 `.trae/rules/` 与 `.trae/skills/` 是否好用、是否各自成体系、有什么优点与缺点，并给出明确建议。
>
> **评估时间**：2026-09-03
> **评估对象**：仓库根目录 → `cut-server/.trae/` 与 `cut-web/.trae/`
> **历史包袱**：两套配置最初是为 ai-eval-server / ai-eval-web 这一对老项目沉淀的（同一份规则在 .trae/rules/server、.trae/rules/web 下也保留了"上一代"作为模板）。已针对 video-cut 的 PRD、7 步流程做了一轮定制（详见各项目 `docs/01-项目初始化问卷.md`、`docs/02-项目上下文.md`、`docs/04-接口契约.md`）。

---

## 1. 一句话结论（TL;DR）

| 维度 | cut-server | cut-web | 结论 |
|------|------------|---------|------|
| **规则（rules）自成体系** | ✅ 四层架构 + 事务 ID 日志 + 接口模板，闭环可用 | ✅ feature-based + traceId 日志 + 组件/Hook/Service/Store 分层，闭环可用 | 两个项目均能单独驱动完整开发 |
| **技能（skills）自成体系** | ✅ 后端工作流（qa-reset → request-analysis → task-spliter → design-doc-code-completion → python-testing → code-review）5 条工作流齐全 | ⚠️ 前端偏重"设计与质检"，**缺少编码实现 + 单测 + E2E** 的端到端技能链 | 后端技能链完整；前端技能链有缺口 |
| **复用性** | `common/` 可直接复制，`project/` 需替换 | 同上 | 通用规则已具备良好的"项目间迁移能力" |
| **最大优点** | 接口契约走 `04-接口契约.md`，前后端字段映射有附录，避坑到位 | README 速查 + SKILL_REGISTRY.md + 版本管理（frontmatter version / CHANGELOG.md）做得最用心 | 两端都已工程化 |
| **最大缺点** | 项目名仍写"ai-eval-server"，领域是测评而非视频剪辑，规则需要"降级"才能用 | 同样：项目名仍为"ai-eval-web"；Vite 默认端口仍是 5173，PRD 假设是 5173，规则已对；最大的缺口是"编码实现类"技能几乎全无 | 两端的 `project/00-01` 都还是上一代项目的"模板"，未深度裁剪到 video-cut 7 步流程 |
| **是否值得保留** | ✅ 强烈建议保留并按本文整改 | ✅ 强烈建议保留并按本文整改 | 两套体系都值，但必须做一次"主题替换 + 缺口补齐" |

---

## 2. 各自现状摸底

### 2.1 目录结构对比

```
cut-server/.trae/
├── rules/
│   ├── README.md                       (索引 + 迁移指南)
│   ├── common/
│   │   ├── 01-coding-standards.md      (Python 编码规范 + 编码铁律 + 注释强制)
│   │   ├── 02-architecture-patterns.md (四层架构 + core/ + 事务ID日志 + 错误体系)
│   │   ├── 03-code-quality.md          (审查清单 + 测试 + 安全 + 重构)
│   │   ├── 04-dev-workflow.md          (零干预流程 + plan 目录 + 卡点恢复 + Git)
│   │   └── templates/
│   │       ├── 00-项目初始化问卷.md
│   │       ├── 01-新增模块checklist.md
│   │       ├── 02-接口变更模板.md
│   │       └── 03-code-review-checklist.md
│   └── project/
│       ├── 00-project-overview.md      ⛔ 仍叫 ai-eval-server
│       └── 01-project-specific.md      ⛔ 命名/异常/模块结构都还是评测领域
├── skills/
│   ├── WORKFLOW.md                     (5 套工作流矩阵)
│   ├── code-review/
│   ├── coding-skill/                   (Controller/业务层/接口层三规范)
│   ├── design-doc-code-completion/
│   ├── design-skill/
│   ├── docs-design/
│   ├── eval-case-design/
│   ├── eval-direction-extension/
│   ├── fastapi-python/
│   ├── find-skills/
│   ├── karpathy-guidelines/
│   ├── project-analysis/
│   ├── pymupdf-pdf/                    (与项目无关，建议移走)
│   ├── python-code-standards-validator/
│   ├── python-project-bootstrap/
│   ├── python-scaffold/
│   ├── python-testing/
│   ├── qa-reset/
│   ├── request-analysis/
│   ├── target-system-integration/
│   └── task-spliter/
└── docs/
    ├── 01-项目初始化问卷.md            ✅ 已针对 video-cut 填写（基于 PRD）
    ├── 02-项目上下文.md                ✅ 待生成
    └── 04-接口契约.md                  ✅ 已针对 video-cut 7 步 + 项目 + 配置起草
```

```
cut-web/.trae/
├── rules/
│   ├── README.md                       (非常完整：5 分钟入门 + 速查 + FAQ + 迁移指南)
│   ├── common/
│   │   ├── 01-coding-standards.md      (TS/React 编码规范 + TSDoc 强制)
│   │   ├── 02-architecture-patterns.md (含 §7 新模块定位指南，版本 v1.1.0)
│   │   ├── 03-code-quality.md          (审查 + Vitest + Playwright + XSS/CSRF/Token)
│   │   ├── 04-dev-workflow.md          (零干预 + plan + 卡点恢复 + 浏览器用 Playwright)
│   │   └── templates/00-项目初始化问卷.md
│   └── project/
│       ├── 00-project-overview.md      ⛔ 仍叫 ai-eval-web，且功能列表全是评测/Bug/笔记
│       └── 01-project-specific.md      ⛔ 命名/领域前缀/3.x 模块规则都还是上一代
├── skills/
│   ├── SKILL_REGISTRY.md               (技能注册表 + 依赖图 + 冲突解决) ⭐ 设计感最强
│   ├── CHANGELOG.md                    (版本演进记录)
│   ├── docs-design/
│   ├── find-skills/
│   ├── frontend-design/
│   ├── karpathy-guidelines/
│   ├── model-design/
│   ├── project-analysis/
│   ├── qa-reset/
│   ├── ui-ux-pro-max/
│   ├── vercel-react-best-practices/
│   └── web-design-guidelines/
└── docs/
    ├── 01-项目初始化问卷.md            ✅ 已针对 video-cut 填写（视频剪辑 7 步）
    └── 02-项目上下文.md                ✅ 待生成
```

### 2.2 数量与体量

| 维度 | cut-server | cut-web |
|------|-----------|---------|
| rules 数 | 4 common + 2 project + 4 templates = **10** | 4 common + 2 project + 1 template = **7** |
| skills 数 | **18** | **10**（另含 SKILL_REGISTRY + CHANGELOG） |
| skill 是否带 REFERENCE/脚本 | 大部分带（templates/checklist/skills 各 1 份） | 几乎全是纯 SKILL.md，无附带产物 |
| README 工程化程度 | 中（索引 + 速查 + 迁移） | **高**（快速入门 + 速查 + FAQ + 迁移 + 版本号） |

---

## 3. cut-server 评估

### 3.1 优点（值得保留的部分）

1. **四层架构规则扎实**（`02-architecture-patterns.md`）
   - Controller / Service / Manager / Model 四层职责边界写得很清楚，并明确禁止反向依赖与跨层调用。
   - `core/` 目录定位写得很到位：仅由 Manager 调用、纯算法/策略实现、不依赖任何层。这是 video-cut 这边能复用的（裁切、字幕合成等都可以装到 `core/`）。
   - 给出"何时用 Manager 层"决策表，单领域 CRUD 用 Service、跨领域编排用 Manager，颗粒度刚好。

2. **编码规范"事无巨细"**（`01-coding-standards.md`）
   - 含命名速查表、Google 风格 docstring、类型提示、配置项注释强制。
   - 第 7 章"文件编码规范"把 BOM / GBK / UTF-8 踩坑史固化下来，并通过 `.editorconfig` + `.gitattributes` 强约束，**这是从血泪教训里总结出来的铁律**，对 video-cut 这种"长期被 Windows 记事本编辑 .md"的项目尤其有用。
   - 含 Python 读写文件的 UTF-8 标准模板。

3. **接口契约链路完整**（`WORKFLOW.md` + `02-接口变更模板.md` + 已起草的 `docs/04-接口契约.md`）
   - `02-接口变更模板.md` 强制每改一个接口都要走 Request / Response / 影响范围 / 安全 / Review 记录五段式。
   - `docs/04-接口契约.md` 已经按 video-cut 7 步流程起草到 v1.0.0，且在附录 A 把前后端字段映射全部列出来（snake_case ↔ camelCase）。这一份对 cut-web 的收益巨大，能显著降低字段名踩坑概率。

4. **事务 ID 日志体系**（`02-architecture-patterns.md §6.2`）
   - 格式规范：`时间 | 级别 | tx:xxx | 模块 | 函数 | 行号 | 消息`
   - 跨层调用要记录入口与出口耗时。
   - 对应 video-cut 这种"长任务（音频合成 / 视频切片 / 合成）多、需要排错"的场景再合适不过。

5. **错误体系有"层级骨架 + 项目填充"两层**（`02-architecture-patterns.md §4` + `01-project-specific.md §1.4`）
   - 通用规则只给出"应该有哪些层级"，项目特定规则负责"具体叫 EvalSuiteError 还是 VCCutError"，这种"骨架通用 + 血肉定制"的拆分很好。
   - 切到 video-cut 时，把根异常从 `EvalServerError` 改成 `VideoCutServerError`，再加 `StepLockError / MarkerRangeError / AudioTTSError / FfmpegError / TaskNotFoundError / ProjectNotFoundError` 等即可。

6. **测试 / 安全 / 重构规则齐全**（`03-code-quality.md`）
   - 测试按 unit/integration/e2e 分目录，按"日期+时间戳"输出 → 与 cut-web 完全一致思路。
   - 安全章节覆盖 SQL 注入、命令注入、敏感信息、权限校验、依赖漏洞扫描。
   - 重构章节给出"何时重构"的判定（重复 ≥ 3 次 / 函数 > 50 行 / 模块 > 300 行），避免过早抽象。

7. **零干预开发流程已成体系**（`04-dev-workflow.md`）
   - 功能点状态机：pending → designing → developing → testing → done。
   - 轻量模式 vs 完整模式的判定标准（变更性质 vs 文件数量）。
   - 卡点检测与恢复机制：失败 ≥ N 次自动升级、回滚、跳过。
   - 这个流程模板对任何规模的项目都适用。

8. **新增模块 checklist / 接口变更模板 / 精简审查清单**（`templates/`）
   - 不是装饰，能直接拿来贴进 PR 描述。

9. **领域 skill 全链路 + 5 套工作流**（`skills/WORKFLOW.md`）
   - 工作流 1：新功能开发流（qa-reset → request-analysis → task-spliter → design-doc-code-completion → python-testing → code-review）
   - 工作流 2：Bug 修复流（轻量，跳过需求分析与拆分）
   - 工作流 3：新评测方向扩展流（评测领域特有）
   - 工作流 4：新被测系统接入流（LLM/RAG/MCP 接入）
   - 工作流 5：评测用例设计流
   - **工作流 3/4/5 是上一代 ai-eval-server 特有的**，video-cut 用不上，但"工作流 1 + 2"完全可复用。
   - 领域 skill 中真正可复用的：`fastapi-python`、`coding-skill`、`python-testing`、`python-code-standards-validator`、`request-analysis`、`task-spliter`、`code-review`、`design-doc-code-completion`、`karpathy-guidelines`、`qa-reset`。
   - 评估方向的：`eval-direction-extension`、`eval-case-design`、`target-system-integration`、`design-skill`——这三类都需要"重命名或重写"以匹配 video-cut。

### 3.2 缺点（必须整改）

1. ⛔ **项目名仍是 `ai-eval-server`**
   - `rules/project/00-project-overview.md`、`01-project-specific.md`、`README.md` 第 5 节"与后端项目的关系"全部还是上一代项目名。
   - 7 步流程完全没有提到（毕竟原本就不是 7 步流程），需要新增 video-cut 的项目特定规则章节。

2. ⛔ **领域命名 / 异常体系还是评测**
   - `01-project-specific.md §1.1` 列的领域前缀是 Eval/Task/Mcp/User/File/History/Report/Target。
   - §1.4 异常体系是 EvalSuiteError/EvalCaseError/McpClientError/AuthError/FileImportError 等。
   - 需要替换为 VideoCut 领域前缀（`VC` / `Project` / `Step` / `Marker` / `Audio` / `Cut` / `Compose` / `History` / `Task` / `Config`）。

3. ⛔ **模块结构示例仍是 controller/service/manager/models 按"评测用例/任务/用户/导入"组织**
   - video-cut 后端实际模块（参考 `04-接口契约.md`）应该是：projects / config / step1~7 / task / history / file / dir / system。
   - 应当把"按 step 拆控制器"这种 video-cut 特有的结构沉淀下来。

4. ⛔ **3 个技能完全错位**
   - `eval-direction-extension`、`eval-case-design`、`target-system-integration` 都是评测领域（"加一个新的评测方向如代码评审"），与 video-cut 毫无关系。
   - `design-skill` 与 `docs-design` 在视频处理领域里基本用不到（video-cut 没有"页内嵌原型"的需要），建议改为"PRD-模块-接口分析"或直接移除。

5. ⚠️ **`pymupdf-pdf` skill 与 video-cut 业务无关**
   - 是上代做 PDF 抽取用的，应当移到"通用工具"分组或干脆移除。

6. ⚠️ **`docs/04-接口契约.md` 已经写得很完整，但 `01-project-specific.md` 没有引用它**
   - 建议在 §2 模块结构最上方加一行："接口以 `docs/04-接口契约.md` 为权威，前后端任何修改必须先改契约"。

7. ⚠️ **`WORKFLOW.md` 中的"工作流 3/4/5"对当前项目不适用**
   - 留之无益，建议改为"video-cut 工作流 3：新增 Step 流"+"工作流 4：接入新 TTS/LLM 流"，与 WORKFLOW.md 的命名风格保持一致。

8. ⚠️ **轻量模式 vs 完整模式的边界**（`04-dev-workflow.md §1.5`）"按变更性质判定"是好的，但 **video-cut 这种"频繁改 step 之间的串联"项目**，可能需要为"只调整 step 接口的字段"新增第三种模式（"接口微调模式"），否则每改一个字段都要走完整流程会拖慢节奏。

9. ⚠️ **数据库迁移规则没引用**
   - `common/05-database-migrations.md` 是写在仓库根 `.trae/rules/server/05-database-migrations.md` 的，但 cut-server 里没有，需要补上一份（或直接复用）。
   - video-cut 用 SQLite，目前迁移可能很简单，但既然工程级规则说"声明式 + 每表分节版本追踪"，建议至少把 `05-database-migrations.md` 也复制到 `cut-server/.trae/rules/common/`，并补充 SQLite 的 alembic / 手工 SQL 写法。

10. ⚠️ **`python-project-bootstrap` 与 `python-scaffold` 重复且互不感知**
    - 两个 skill 都做"创建项目脚手架"，区别只在完整度。`bootstrap` SKILL.md 自己说"最小化，不生成模板代码"，`scaffold` 说"完整脚手架"——一个项目里同时存在两个很容易让 AI 选错。建议在 `SKILL.md` 的描述里互相引用对方，明确"何时用哪个"。

---

## 4. cut-web 评估

### 4.1 优点

1. **README 与 SKILL_REGISTRY.md 工程化程度最高**
   - `rules/README.md` 已经做到了"5 分钟入门 + 速查表 + FAQ + 迁移指南 + 与后端协作约定"五位一体，**整个 `.trae/` 子项目里唯一达到"开箱即用"水准的 README**。
   - `skills/SKILL_REGISTRY.md` 给出"快速查找 + 触发冲突解决规则 + 依赖关系图 + 各 Skill 详细信息 + 使用示例 + 维护指南"六位一体，**这种"先注册再触发"的写法值得 cut-server 抄一份**。

2. **feature-based + 横向分层的架构规则已成型**（`02-architecture-patterns.md v1.1.0`）
   - §1.1 各层职责表非常清晰，page / components{basic,business} / hooks / services / store / utils / types / constants / config。
   - §1.2 数据流向单图说清。
   - §1.3 `core/` 定位给出"复杂度高 + 复用性强 + 职责单一"三条件 + 反例，比 cut-server 的版本还具体。
   - §1.4"何时用全局 Store"给出"真共享才用"的判准，避免 Store 滥用。
   - §7 **新模块架构定位指南**，覆盖 Bug/笔记/参考图例/用户管理/用例调试/Dashboard 6 大类，把上一代 ai-eval-web 的沉淀搬过来，新模块照表填即可。video-cut 应当借鉴这种"以模块为单位给定位表"的格式。

3. **Hook 设计规范细致**（`common/02-architecture-patterns.md §3`）
   - `useRequest`、`usePolling`、`useDebounce`、`usePagination` 这种通用 Hook 已写在规则里。
   - 依赖数组规则（`react-hooks/exhaustive-deps`）显式写出。
   - video-cut 的 Step5 虚拟预览本质上是一个"轮询 + 标记编辑状态"复合 Hook，可以直接复用 §3 的范式。

4. **错误体系按 HTTP + 业务码两条线分层**（`01-project-specific.md §1.4`）
   - AppError → ApiError → Network/Unauthorized/Forbidden/NotFound/Business → Validation/Runtime。
   - video-cut 接口契约 `04-接口契约.md §0.3` 的错误码已经按 `40xxx / 50xxx / 60xxx` 分组，刚好可以映射到这套体系。

5. **TSDoc + `strict: true` + 禁止 `any`**（`01-coding-standards.md §3、§4`）
   - 强制 `interface XxxProps`（以 Props 结尾）+ 可选字段 `?` + 默认值。
   - 禁止 `dangerouslySetInnerHTML`、禁止 `// @ts-ignore`、禁止改公共组件 Props 签名。
   - 与 `04-dev-workflow.md §2.3` 一致。

6. **测试/性能/安全规则完整**（`03-code-quality.md`）
   - Vitest 单元测试（不测组件渲染细节）+ Playwright E2E。
   - 性能：首屏 JS ≤ 250KB（gzip）、单路由 chunk ≤ 100KB（gzip）、ECharts 按需引入。
   - 安全：XSS / CSRF / Token（token 存内存 + refreshToken 存 sessionStorage）+ 错误脱敏上报。
   - Bundle 与 Bundle 优化有具体目标（"首屏 chunk ≤ 250KB"）。

7. **零干预流程与卡点恢复写得最用心**（`04-dev-workflow.md §9`）
   - 检测阈值：同文件 ≥ 3 次 / 同错误 ≥ 2 次 / 对话 ≥ 5 轮 / 修复后仍失败 ≥ 2 次。
   - 验证手段选择策略表（单测 → 程序运行 → 浏览器截图/交互）。
   - 浏览器验证统一用 Playwright 脚本（不用 browser_use），避免临时验证漂移。
   - 这套机制直接照搬到 video-cut 即可。

8. **CHANGELOG.md 与 frontmatter version**（管理规范）
   - 文件头 `version: 2.0.0` + `lastUpdated: 2026-09-03` 字段化。
   - CHANGELOG.md 每次变更追加一条。
   - 这套做法比 cut-server 做得更系统，**建议 cut-server 也按这个规范做一次大版本同步**。

9. **契约协作约定已落到具体段**（`00-project-overview.md` 末尾"与后端协作约定"）
   - Base URL、JWT、响应结构 `{code, msg, data, traceId}`、错误码 HTTP+code、跨域代理方式。
   - video-cut 的 `04-接口契约.md §0` 已经把响应结构固定为 `{code, msg, data}`（不带 traceId），应与前端规则一致——**后续应在 cut-web 的 project-overview 末段同步贴上 video-cut 的接口契约链接**。

### 4.2 缺点

1. ⛔ **`00-project-overview.md` 与 `01-project-specific.md` 还是 ai-eval-web**
   - 项目名写"ai-eval-web（AI 测评系统 Web 前端）"。
   - 15 大功能模块里 12 个都跟评测/Bug/笔记/参考图例/Dashboard/检索相关，video-cut 用不上。
   - 命名约定 §1.1 领域前缀是 Eval/Plan/Task/Mcp/User/File/History/Report/Target/Bug/Note/RefGallery/Retrieval/Dashboard/PromptPreset。
   - 异常体系 §1.4 是 AppError/ApiError/Network/Unauthorized 等通用，与 video-cut 无关但仍要按 video-cut 错误码体系做适配。
   - 需要"换主题"为 video-cut：项目名、模块列表、领域前缀、3.12-3.17 这 6 个 Mxx 模块规则全部删掉/替换，新增"7 步流程 7 个页面"对应的规则段。

2. ⛔ **缺少"按 video-cut step1~7 拆页面"的目录骨架**
   - `src/pages/` 目录树全是用 feature（login/case/plan/task/history/...）组织的。
   - video-cut 应按 step1~7 拆（或按项目维度 + step 维度混拆），需要新增"video-cut pages 目录骨架"段落。

3. ⛔ **缺少明确的"虚拟预览（0 IO）"实现规则**
   - 视频剪辑师 PRD 的 Step5 是核心创新点（`<video>.currentTime` 串播，不真正 IO），但前端规则里没有相关章节。
   - 应当在 `01-project-specific.md` 新增 §4.1"虚拟预览实现规范"：禁止在编辑阶段触发 ffmpeg IO、`<video>` 跨源注意事项、`seeked` 事件节流、媒体资源回收等。

4. ⛔ **缺少"长任务统一轮询 Hook"(`useTaskPoll`)规范**
   - PRD §8.1 提到"长任务提交-轮询约定"，Step4 的音频、Step6 的裁切、Step7 的合成都是长任务。
   - 应当在 `01-project-specific.md` 新增 §4.2 给 hook 的参数、清理、错误处理约定（页卸载必须取消轮询，避免 setState on unmounted）。

5. ⛔ **缺少"标记（Marker）编辑"相关组件规则**
   - Step5 的标记起止编辑 / 删除 / 拖拽 / 添加 / 随机重标 / 时长匹配检查，本质是一个"时间轴编辑器"。
   - 应当在 `01-project-specific.md` 新增 §4.3 给 Marker 的数据结构（与 `04-接口契约.md §4.5.1 VideoMarker` 对齐）+ `core/MarkerTimeline/` 的定位判定（按 §1.3 三条件判定核心组件）。

6. ⚠️ **Vite 端口 / 环境变量默认值与 video-cut 不一致**
   - 默认 `5173` 在 video-cut 项目里仍是合理选择（PRD 假设前端 5173、后端 8000），但要显式写一遍。
   - `04-dev-workflow.md` 已经在最后更新过，未发现明显偏差。

7. ⚠️ **`01-project-specific.md §3.x` 大量模块规则超出 video-cut 范围**
   - §3.12 智能笔记 V2、§3.13 Bug 管理、§3.14 参考图例、§3.15 Dashboard、§3.16 上下文检索、§3.17 用例调试——这些 M10~M12 模块与 video-cut 无关。
   - **直接整段删除**或者**移到一个 `archive/` 子目录**，避免新来的 AI 误以为这些是 video-cut 必须实现的功能。

8. ⚠️ **缺少"前端 TypeScript 类型与后端 Pydantic 字段映射"规则**
   - `04-接口契约.md 附录 A` 已经列出全部字段映射，但项目规则里没有"前端类型必须严格与之对齐 + 改名后端要同步"这条铁律。
   - 建议在 `01-project-specific.md §4.4` 新增这条约束。

9. ⚠️ **缺少"启动前端后端联调"的步骤**
   - `04-dev-workflow.md §7` 是问题排查 + Bug 报告，但缺少 video-cut 场景的"同时启动前后端 + 联调 checklist"。
   - 建议新增 §10 "前后端联调"小节，含：先后启动顺序（先 server 8000 再 web 5173）、CORS 检查、Health 接口探测、Vite proxy 配置、traceId 联查步骤。

10. ⚠️ **`project-analysis` skill 仍带 `scripts/*.py`**（详见 README 与 SKILL.md）
    - 上次清查已标记为"待清理"，但 `scripts/` 目录里 7 个脚本仍在。
    - 与前端工程完全无关，建议直接删除 `assets/scripts/` 整目录。

11. ⚠️ **`web-design-guidelines` 依赖外部 GitHub URL**（`SKILL_REGISTRY.md` 已警告）
    - 离线/无网场景不可用，建议改成本地 references/。

12. ⚠️ **CHANGELOG.md 里有 `## v2.0.0 (2026-09-03) — 大规模同步更新` 等条目记录的是 ai-eval-web 的更新**
    - 这些条目可以保留作为"本文件原属于 ai-eval-web 的历史"，但应在文件顶部加一段"本 CHANGELOG 现归 video-cut 使用，从 X 日期起开始记录 video-cut 的更新"，避免误解。

---

## 5. 两端共同的缺点

1. **主题未彻底切换到 video-cut**
   - `project/00-project-overview.md` 与 `project/01-project-specific.md` 两端都还残留 ai-eval 的痕迹（项目名、功能列表、领域前缀、异常体系、模块规则）。
   - 急需要做一次"主题替换"——参照 PRD + `docs/01-项目初始化问卷.md` + `docs/04-接口契约.md` 三个权威输入，把项目规则彻底 video-cut 化。

2. **`docs/` 目录里没有"rules 现状评估与整改计划"**——本文档就是补这一块。

3. **没有"前后端规则不一致约定"的文件**
   - 比如 cut-server 的规则要求"前后端字段一致"，但 cut-web 里却允许 `historyService` 引用（已废弃）——两端没有互相"握手"。
   - 建议在仓库根 `.trae/rules/project/` 写一份 `00-跨端协作约定.md`，固化：接口契约权威路径、字段命名策略（camelCase 请求/响应 vs snake_case 内部命名）、traceId 贯穿方式、CORS/JWT 配置、错误码分级（40xxx 参数 / 41xxx 业务 / 50xxx 外部 / 60xxx 长任务）。

4. **缺乏对 SQLite / 7 步流程的领域建模示例**
   - `02-architecture-patterns.md` 给的是"通用四层"骨架，没给"vc_project / vc_generation_history / vc_config 3 张表的建模示例"。
   - `01-project-specific.md §2 模块结构`也只列到 `controllers/services/managers/models/utils/core`，没有针对 Step1~7 的控制器布局示范。
   - 建议两端都补一份"video-cut 模块结构示例图"，作为新加模块时的参考。

5. **没有"skill 的版本与废弃状态表"**
   - cut-server 18 个 skill 中真正活跃的可能只有 7~9 个；cut-web 10 个 skill 中真正活跃的可能只有 7 个。
   - 建议两个项目都补一份"skill 使用统计 / 最近 30 天调用频次"统计脚本（简单的 grep 即可），便于淘汰无用的 skill。

6. **`examples/` 目录两端都没有**
   - 建议增加 `cut-server/examples/` 与 `cut-web/examples/`，把"如何起一个新功能模块"的最佳实践样例代码放进去，比纯文字规则更好理解。

---

## 6. 整改建议（按优先级排序）

### 6.1 P0（必须立即做）

| 序号 | 任务 | 负责项目 | 工作量 |
|------|------|---------|--------|
| 1 | 重写 `cut-server/rules/project/00-project-overview.md`：替换项目名 + 功能列表（7 步流程）+ 技术栈 + 与前端协作 | server | 1h |
| 2 | 重写 `cut-server/rules/project/01-project-specific.md`：替换命名约定（VC / Project / Step / Marker / Audio / Cut / Compose / History / Task / Config）+ 异常体系（VideoCutServerError 为根）+ 模块结构（按 step 拆 controllers）+ 7 步流程领域规则 | server | 2h |
| 3 | 重写 `cut-web/rules/project/00-project-overview.md`：替换为 video-cut，移除 M10/M11/M12 | web | 1h |
| 4 | 重写 `cut-web/rules/project/01-project-specific.md`：替换领域前缀、模块规则；删除 §3.12~3.17；新增 §4.x 虚拟预览、轮询 Hook、Marker 编辑、前后端字段对齐、联调 | web | 2h |
| 5 | 把 `docs/04-接口契约.md` 的权威地位写进两端 `rules/project/00-project-overview.md` 末尾"与（前后端）协作约定" | 两端 | 0.5h |
| 6 | 新增仓库根 `.trae/rules/project/00-跨端协作约定.md`（接口契约权威、字段命名、traceId、错误码分级、CORS/JWT） | 根 | 1h |

### 6.2 P1（建议本周内做）

| 序号 | 任务 | 工作量 |
|------|------|--------|
| 7 | cut-server: 删除/归档 `eval-direction-extension`、`eval-case-design`、`target-system-integration`、`pymupdf-pdf` 4 个 skill；新增 `step-feature-extension`、`tts-llm-integration` 两个 video-cut 专用 skill 草案 | 4h |
| 8 | cut-server: 改写 `skills/WORKFLOW.md` 工作流 3/4/5 为 video-cut 场景（新增 Step 流 / 接入新 TTS 流） | 1h |
| 9 | cut-web: 新增 `virtual-preview` skill（指导 Step5 0 IO 预览）+ `task-poll` skill（指导长任务轮询）+ `marker-timeline` skill（指导时间轴组件） | 6h |
| 10 | cut-web: 新增 `playwright-e2e-7-step` skill（覆盖 7 步完整 E2E） | 4h |
| 11 | cut-server: 把 `database-migrations` 规则从仓库根 `.trae/rules/server/05-...` 复制到 `cut-server/.trae/rules/common/` 并改成"SQLite + alembic"风格 | 2h |
| 12 | cut-web: 仿照 cut-server 新增 `01-coding-standards.md §7 文件编码规范`（虽然前端不太用 .md 但 SCSS / tsconfig 偶发会有 BOM 问题） | 1h |
| 13 | cut-server: 把 `PROJECT_RULES_REVIEW.md`（类似仓库根 README）放出去，提供给未来"评估某个项目是否这套规则够用"的快速判断脚本 | 1h |

### 6.3 P2（项目稳定后做）

| 序号 | 任务 | 工作量 |
|------|------|--------|
| 14 | cut-server: 把 `python-project-bootstrap` 与 `python-scaffold` 互相在 SKILL.md frontmatter 引用，避免 AI 选错 | 0.5h |
| 15 | cut-web: 删除 `assets/scripts/` 整目录（project-analysis 的死代码） | 0.5h |
| 16 | cut-web: `web-design-guidelines` 改成纯本地引用 | 1h |
| 17 | 两端：补一份"skill 调用统计"脚本（基于 plan/08-代码日志.md 中提到的 skill 名，统计 30 天调用次数） | 1h |
| 18 | 两端：补一份"快速检视本项目 rules 是否覆盖到了"的 checklist（10 题，5 分钟自检） | 1h |

---

## 7. 综合评分

| 维度 | cut-server | cut-web | 改进后目标 |
|------|------------|---------|-----------|
| 规则可读性 | 8/10 | 9/10 | 9/10 |
| 架构合理性（四层 / feature-based） | 9/10 | 9/10 | 维持 |
| 编码规范完整性 | 9/10 | 8/10 | 维持 |
| 与 video-cut 业务契合度 | 5/10 | 5/10 | **9/10** |
| 测试/质量/安全规则 | 9/10 | 9/10 | 维持 |
| 技能链完整性（端到端可驱动） | 8/10 | 6/10 | 9/10 |
| 工程化（README/CHANGELOG/版本） | 7/10 | 9/10 | 9/10（server 也升一档） |
| 文档与 skill 一致性 | 7/10 | 8/10 | 9/10 |
| **整体** | **7.5/10** | **7.9/10** | **9.0/10** |

---

## 8. 回答最初的问题

### "两套 rules 好不好用？是否各自成体系？"

- **cut-server 的 rules 成体系，能用，但"长得像而不是真用得着"**。四层架构 + 事务 ID + 接口模板 + 卡点恢复的工程闭环很完整，是一套可独立运行的体系。但内容是上一代 ai-eval-server 的"骨架通用 + 项目特定"两层结构，project/ 层必须重写。
- **cut-web 的 rules 成体系，可用，工程化程度最高**。README + SKILL_REGISTRY + CHANGELOG 三件套值得 cut-server 抄。但内容也是 ai-eval-web 的，project/ 层同样必须重写，并且 §3.12-3.17 这些 Mxx 模块规则要全删。
- **两套之间没有强耦合**——后端规则讲四层 + Python，前端规则讲 feature + TS，各自独立，通过各自的 `00-project-overview.md` 末尾"协作约定"握手。这是好事，但建议在仓库根加一份 `00-跨端协作约定.md` 作为更强的契约。

### "是否各自成自己的体系可以使用？"

- 各自的 `common/` 完全可以给一个全新前后端分离项目使用，只需替换 `project/`。
- 各自的 skills 都需要"裁剪"：server 砍掉 4 个评测专用 + 1 个 PDF，加 video-cut 专用；web 砍掉或保留"设计类"skill（model-design/docs-design/frontend-design/ui-ux-pro-max）但要新增"编码实现 / 调试 / E2E"类 skill。
- **建议保留**，但必须做 §6 中的 P0 整改，预计 7~8 小时工作量即可让两套体系同时达到"主题纯正 + 端到端可用"的状态。

### "有什么优点？"

- 见 §3.1（cut-server 9 项）和 §4.1（cut-web 9 项）。
- 共性优点：分层清晰、注释强制、测试/质量/安全规则完整、卡点恢复机制扎实、接口契约/协作约定有具体文件支撑。

### "有什么缺点？"

- 见 §3.2（cut-server 10 项）和 §4.2（cut-web 12 项）+ §5 两端共同 6 项。
- 共性缺点：**主题没换**，仍是上一代 ai-eval 项目的"换皮"。skill 缺少 video-cut 专用的实现类、调试类。

---

## 9. 结论

> **保留两套规则体系，做一次"主题切换 + 缺口补齐"整改（约 7~8 小时），即可让 cut-server 与 cut-web 都达到 9/10 的工程化水准，达到"开箱即用 + 端到端可驱动 + 与 video-cut 业务深度契合"。**

---

## 附录 A：建议的 cut-server `/docs` 目录结构（整改后）

```
cut-server/.trae/
├── rules/
│   ├── README.md                                     (更新：与视频剪辑师协作约定指向 04-接口契约)
│   ├── common/
│   │   ├── 01-coding-standards.md                    (维持 + 增加"video-cut 实际代号前缀示例")
│   │   ├── 02-architecture-patterns.md              (维持)
│   │   ├── 03-code-quality.md                        (维持)
│   │   ├── 04-dev-workflow.md                        (维持)
│   │   ├── 05-database-migrations.md                 (新增：SQLite + alembic 写法)
│   │   └── templates/
│   │       ├── 00-项目初始化问卷.md                   (维持)
│   │       ├── 01-新增模块checklist.md               (改：按 step 拆控制器的 checklist)
│   │       ├── 02-接口变更模板.md                     (维持)
│   │       └── 03-code-review-checklist.md           (维持)
│   └── project/
│       ├── 00-project-overview.md                    (重写)
│       └── 01-project-specific.md                    (重写)
├── skills/
│   ├── WORKFLOW.md                                   (工作流 3/4/5 重写)
│   ├── CHANGELOG.md                                  (新增)
│   ├── SKILL_REGISTRY.md                             (新增，抄 web 端样式)
│   ├── code-review/                                  (维持)
│   ├── coding-skill/                                 (维持)
│   ├── design-doc-code-completion/                   (维持)
│   ├── fastapi-python/                               (维持)
│   ├── karpathy-guidelines/                          (维持)
│   ├── python-code-standards-validator/              (维持)
│   ├── python-project-bootstrap/                     (维持)
│   ├── python-scaffold/                              (维持)
│   ├── python-testing/                               (维持)
│   ├── qa-reset/                                     (维持)
│   ├── request-analysis/                             (维持)
│   ├── task-spliter/                                 (维持)
│   ├── find-skills/                                  (维持)
│   ├── project-analysis/                             (维持)
│   ├── step-feature-extension/                       (新增，替代 eval-direction-extension)
│   ├── tts-llm-integration/                          (新增，替代 target-system-integration)
│   └── step-case-design/                             (新增，替代 eval-case-design)
└── docs/
    ├── 01-项目初始化问卷.md                          (✅ 已完成)
    ├── 02-项目上下文.md                              (待 AI 生成)
    ├── 03-开发进度.md                                 (待生成)
    ├── 04-接口契约.md                                (✅ 已完成 v1.0.0)
    └── 07-rules-skills评估与整改.md                  (= 本文档的 server 版)
```

## 附录 B：建议的 cut-web `/docs` 目录结构（整改后）

```
cut-web/.trae/
├── rules/
│   ├── README.md                                     (更新：协作约定指向接口契约)
│   ├── common/
│   │   ├── 01-coding-standards.md                    (维持 + 增加视频资源相关补充)
│   │   ├── 02-architecture-patterns.md              (维持)
│   │   ├── 03-code-quality.md                        (维持)
│   │   ├── 04-dev-workflow.md                        (维持)
│   │   └── templates/
│   │       └── 00-项目初始化问卷.md                   (维持)
│   └── project/
│       ├── 00-project-overview.md                    (重写：video-cut 7 步 + 项目管理 + 全局配置)
│       └── 01-project-specific.md                    (重写 + §4.x 视频领域规则)
├── skills/
│   ├── SKILL_REGISTRY.md                             (维持)
│   ├── CHANGELOG.md                                  (维持)
│   ├── qa-reset/                                     (维持)
│   ├── karpathy-guidelines/                          (维持)
│   ├── find-skills/                                  (维持)
│   ├── project-analysis/                             (维持，删除 scripts/)
│   ├── docs-design/                                  (维持)
│   ├── model-design/                                 (维持)
│   ├── ui-ux-pro-max/                                (维持)
│   ├── frontend-design/                              (维持)
│   ├── vercel-react-best-practices/                  (维持)
│   ├── web-design-guidelines/                        (改为纯本地引用)
│   ├── virtual-preview/                              (新增：0 IO 预览规范)
│   ├── task-poll/                                    (新增：长任务轮询 Hook 规范)
│   ├── marker-timeline/                              (新增：时间轴组件规范)
│   └── playwright-e2e-7-step/                        (新增：7 步 E2E 模板)
└── docs/
    ├── 01-项目初始化问卷.md                          (✅ 已完成)
    ├── 02-项目上下文.md                              (待 AI 生成)
    ├── 03-开发进度.md                                 (待生成)
    └── 07-rules-skills评估与整改.md                  (= 本文档的 web 版)
```

## 附录 C：建议的仓库根目录 `/docs` 文档树（顶层协调）

```
docs/
├── 00-README.md                                      (本仓库"前后端规则体系"总入口)
├── 01-cut-server-rules-skills-analysis.md            (= 本文档的精简 server 版)
├── 02-cut-web-rules-skills-analysis.md               (= 本文档的精简 web 版)
├── 03-跨端协作约定.md                                (= 仓库根跨端协作规则)
├── 04-接口契约权威性说明.md                          (说明 docs/04-接口契约.md 是单一权威)
├── 05-主题切换计划.md                                (本期 ai-eval → video-cut 的整改计划)
└── 99-rules-skills-evaluation.md                     (= 本文档，与 server/web 的精简版指向同一份)
```

---

_评估报告版本：v1.0_
_维护者：AI（按 04-dev-workflow.md §卡点恢复 自动管理变更）_
_最后更新：2026-09-03_
