---
alwaysApply: false
description: 测试分层策略，包括单元/集成/E2E 测试边界、覆盖率门槛、mock 策略、联调测试流程。涉及编写测试、规划测试策略、前后端联调时使用此规则。
---

# 测试策略（共享层）

> 前后端共用同一套测试分层策略，确保质量可控、边界清晰。

## 1. 测试金字塔

```
            /\
           /  \
          / E2E \        ← 关键业务流程，数量少但价值高
         /--------\
        / Integration \   ← 前后端联调、API 契约验证
       /--------------\
      /    Unit Tests   \ ← 核心逻辑，数量最多
     /--------------------\
```

## 2. 测试层级定义

### 2.1 单元测试（Unit Test）

| 维度 | 后端 | 前端 |
|------|------|------|
| 测试对象 | 函数/类/模块 | 函数/Hook/组件 |
| 工具 | pytest | Vitest + @testing-library/react |
| 覆盖率门槛 | ≥ 80% | ≥ 80% |
| 执行速度 | < 10s | < 15s |
| Mock 策略 | Mock 外部 API、DB | Mock API 调用、浏览器 API |
| 文件位置 | `tests/unit/` | co-location 或 `tests/unit/` |

**单元测试规则：**
- 每个测试函数只验证一个场景
- 命名：`test_<场景>_<预期结果>`
- 三个阶段：Arrange → Act → Assert
- 禁止测试之间互相依赖
- 禁止使用 `sleep()`，用 mock 控制时间

### 2.2 集成测试（Integration Test）

| 维度 | 后端 | 前端 |
|------|------|------|
| 测试对象 | 模块间协作 | 组件组合 + API 调用 |
| 工具 | pytest + testcontainers | Vitest + MSW |
| 覆盖率门槛 | ≥ 60% | ≥ 50% |
| Mock 策略 | 使用真实 DB 容器 | MSW Mock API 响应 |
| 文件位置 | `tests/integration/` | `tests/integration/` |

**集成测试规则：**
- 测试跨模块的数据流和业务流程
- 后端：Controller → Service → Manager → Model 全链路
- 前端：Page → Hook → Service → API（Mock）→ Store 更新 → 组件渲染
- 每个集成测试场景必须对应一个业务用例

### 2.3 E2E 测试（End-to-End）

| 维度 | 工具 | 覆盖范围 |
|------|------|---------|
| 后端 | httpx | API 端到端测试 |
| 前端 | Playwright | 浏览器端到端测试 |
| 覆盖率门槛 | 关键路径 100% | 关键路径 100% |
| 执行时机 | PR + 发布前 | PR + 发布前 |

**E2E 测试规则：**
- 只覆盖核心业务流程，不追求高覆盖率
- 每个场景独立运行，不共享状态
- 使用真实环境（或接近真实的 staging）
- 失败时自动截图/录屏，便于排查

## 3. 前后端联调测试

### 3.1 联调测试流程

```
后端完成 API → 更新 OpenAPI → 前端拉取类型 → 前端实现 → 联调测试 → 通过
```

### 3.2 契约测试（Contract Testing）

- 后端：CI 中运行 OpenAPI schema 验证，确保实现与契约一致
- 前端：MSW 模拟 API 响应，确保前端按契约消费
- 联调时：前端直连后端，运行集成测试验证端到端

### 3.3 联调检查清单

- [ ] 接口 Path 和 Method 对齐
- [ ] 请求参数类型和必填项对齐
- [ ] 响应字段名和类型对齐
- [ ] 错误码定义对齐
- [ ] 分页参数和返回格式对齐
- [ ] 认证 Token 格式对齐
- [ ] CORS 配置正确

## 4. 测试数据管理

### 4.1 后端

- 单元测试：使用 fixture 工厂函数生成测试数据
- 集成测试：使用 testcontainers 创建真实 DB，测试前 seed 数据
- 禁止：硬编码测试数据、测试间共享 DB 状态

### 4.2 前端

- 单元测试：mock 数据工厂函数
- 集成测试：MSW handler 返回 mock 数据
- E2E 测试：使用专用测试账号和环境

## 5. 测试输出管理

- 每次测试运行结果按 `日期_时间戳` 文件夹独立存放
- 输出内容：测试报告（HTML/XML）、覆盖率报告、日志
- 测试输出目录：`tests/output/{timestamp}/`

## 6. 持续集成中的测试

| 阶段 | 触发 | 执行内容 | 失败处理 |
|------|------|---------|---------|
| push | push 到任意分支 | lint + type-check + unit test | 阻止合并 |
| PR | PR 创建/更新 | + integration test + coverage check | 阻止合并 |
| merge | 合并到 main | + build + E2E（staging） | 通知 |
| release | tag 发布 | + full E2E（prod-like） | 阻止发布 |
