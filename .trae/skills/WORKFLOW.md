# 统一工作流编排

> **版本**: v1.0.0
> **最后更新**: 2026-09-04
> **定位**: 跨端开发流程编排，串联前后端技能

---

## 工作流总览

| # | 工作流 | 适用场景 | 步骤 |
|---|--------|---------|------|
| 1 | 新功能开发流 | 新增 Step / 新增页面 | qa-reset → request-analysis → task-spliter → 后端+前端并行 → 联调 → code-review |
| 2 | Bug 修复流 | 前后端 Bug | 定位端 → 该端编码 → 测试 → code-review |
| 3 | 接口变更流 | 新增/修改 API | 改契约 → 后端实现 → 前端对齐 → 联调 |
| 4 | 新增 Step 流 | 扩展 7 步流程 | 契约 → 后端(Controller/Service/Manager) → 前端(页面/Service/Hook) → 联调 |
| 5 | 接入新 TTS/LLM 流 | 替换/新增外部系统 | 配置项 → 后端适配器 → 测试连接 → 前端配置面板 |

## 工作流 1: 新功能开发流

```
用户提出需求
    │
    ▼
[qa-reset] 需求润色与结构化
    │  产出: 结构化需求描述
    ▼
[request-analysis] 需求分析（新增类/修改类）
    │  产出: 接口设计草案 + 数据模型变更
    ▼
[task-spliter] 任务拆分
    │  产出: 后端任务清单 + 前端任务清单 + 联调任务
    ▼
┌─────────────────┬─────────────────┐
│   后端并行       │   前端并行       │
│                 │                 │
│ 改契约文档      │ 对齐 TS 类型    │
│ Controller      │ Service 层      │
│ Service         │ Hook 层         │
│ Manager（如需） │ Component 层    │
│ Model（如需）   │ Store（如需）    │
│ python-testing  │ Vitest          │
│ code-review     │ code-review     │
└────────┬────────┴────────┬────────┘
         │                 │
         └────────┬────────┘
                  ▼
         联调验证（联调 checklist）
                  │
                  ▼
            更新开发进度
```

**路由规则**:
- 后端任务 → 使用 `cut-server/.trae/skills/` 中的技能
- 前端任务 → 使用 `cut-web/.trae/skills/` 中的技能
- 联调任务 → 使用根级 `templates/00-前后端联调checklist.md`

## 工作流 2: Bug 修复流

```
用户报告 Bug
    │
    ▼
定位 Bug 所属端
    │
    ├── 后端 Bug
    │   │
    │   ▼
    │   [coding-skill / fastapi-python] 修复
    │   │
    │   ▼
    │   [python-testing] 验证
    │   │
    │   ▼
    │   [code-review] 审查
    │
    └── 前端 Bug
        │
        ▼
        [frontend-design / vercel-react-best-practices] 修复
        │
        ▼
        [Vitest] 验证
        │
        ▼
        [code-review] 审查
        │
        ▼
        如涉及跨端 → 对照接口契约验证字段
```

## 工作流 3: 接口变更流

```
确定需要新增/修改接口
    │
    ▼
填写「跨端接口变更模板」(templates/01-跨端接口变更模板.md)
    │
    ▼
更新 04-接口契约.md
    │  - 方法/路径
    │  - 请求 Schema
    │  - 响应 Schema
    │  - 错误码
    │  - 附录 A 字段映射
    ▼
后端实现
    │  - Controller 路由
    │  - Service 业务逻辑
    │  - 单元测试
    ▼
前端对齐
    │  - TypeScript 类型（与契约附录 A 一致）
    │  - Service API 调用
    │  - Hook 数据逻辑
    │  - Component UI
    ▼
联调验证
    │  - 启动两端
    │  - 按联调 checklist 验证
    │  - 检查错误码处理
    ▼
code-review（两端各一次）
```

## 工作流 4: 新增 Step 流

适用: 在 7 步流程中新增一个步骤（如 Step3.5 添加图片生成）

```
1. 契约设计
   - 定义新接口（POST /api/step{N}/{action}）
   - 定义任务状态（如为长任务）
   - 定义错误码
   - 更新步骤状态机

2. 后端实现
   - Controller: Step{N}Controller
   - Service: Step{N}Service
   - Manager: Step{N}Manager（如涉及外部系统编排）
   - core/: 纯算法实现（如裁切计算、字幕生成）
   - Model: 数据模型变更（vc_generation_history 新增 result_type）

3. 前端实现
   - Page: Step{N}Panel
   - Service: step{N}Service
   - Hook: useStep{N}
   - Component: Step{N} 相关组件
   - Store: 更新 currentStep 状态机

4. 联调验证
   - 步骤前置条件校验
   - 步骤锁定验证
   - 长任务轮询验证（如适用）
   - 历史版本保留验证
```

## 工作流 5: 接入新 TTS/LLM 流

适用: 替换 edge-tts 为其他 TTS 引擎，或替换 DeepSeek 为其他 LLM

```
1. 配置项设计
   - 在 vc_config 表新增配置项
   - 在 04-接口契约.md Config Schema 中补充
   - 在 ConfigService 中添加默认值

2. 后端适配器
   - Manager 层新增适配器（如 TTSEngineManager / LLMProviderManager）
   - 适配器实现统一接口（synthesize() / chat()）
   - 原有引擎通过适配器接口调用
   - 新引擎实现相同接口

3. 测试连接
   - POST /api/config/test-connection 验证新引擎可用性
   - 记录耗时和错误信息

4. 前端配置面板
   - 全局配置页新增引擎选择下拉框
   - 新增对应配置项表单
   - 测试连接按钮反馈

5. 联调验证
   - 切换引擎 → Step4 验证 TTS
   - 切换引擎 → Step2/3 验证 LLM
   - 兜底机制验证（新引擎失败时回退）
```

## 技能选择决策树

```
用户需求
    │
    ├── 需求不明确?
    │   └── qa-reset 润色
    │
    ├── 是新功能?
    │   ├── 涉及前后端? → 工作流 1
    │   ├── 纯后端? → 后端技能链
    │   └── 纯前端? → 前端技能链
    │
    ├── 是 Bug?
    │   └── 工作流 2
    │
    ├── 涉及接口变更?
    │   └── 工作流 3
    │
    ├── 新增 Step?
    │   └── 工作流 4
    │
    └── 接入新外部系统?
        └── 工作流 5
```

## 后端技能链

```
qa-reset → request-analysis → task-spliter → design-doc-code-completion → fastapi-python/coding-skill → python-testing → code-review
```

详细见: `cut-server/.trae/skills/WORKFLOW.md`

## 前端技能链

```
qa-reset → project-analysis → docs-design → frontend-design/vercel-react-best-practices → Vitest → code-review
```

详细见: `cut-web/.trae/skills/SKILL_REGISTRY.md`
