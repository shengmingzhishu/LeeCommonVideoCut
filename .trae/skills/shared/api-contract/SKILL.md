---
name: api-contract
version: 1.0.0
description: API 契约定义与类型同步。生成/维护 OpenAPI 定义，自动生成前端 TS 类型，生成 mock 数据，验证契约一致性。
---

# API 契约技能

## 定位

管理前后端 API 契约的全生命周期：定义 → 同步 → 验证 → 变更管控。

## 核心能力

### 1. OpenAPI 定义生成

- 从后端 FastAPI 路由提取 OpenAPI 定义
- 生成结构化的 `openapi.yaml` 设计稿
- 确保每个接口定义完整（summary、parameters、requestBody、responses、error-codes）

### 2. 前端类型同步

- 使用 `openapi-typescript` 从 OpenAPI 生成 TS 类型
- 生成的文件放在 `src/types/api/`，禁止手动修改
- 前端 Service 层引用生成的类型

```bash
# 同步命令
pnpm run sync-api
# 等价于
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api/generated.ts
```

### 3. Mock 数据生成

- 从 OpenAPI Schema 生成 mock 数据
- 支持 faker.js 生成真实感数据
- 输出 MSW handler 配置

### 4. 契约验证

- 后端：CI 中运行 `openapi schema validator`，确保实现与契约一致
- 前端：CI 中检查生成的 TS 类型是否最新
- 联调时：前后端响应格式对比

## 使用流程

```
1. 后端定义/修改接口 → 更新 OpenAPI
2. 运行 api-contract 生成契约文件
3. 前端拉取 → 生成 TS 类型
4. 前端实现 Service 层（引用生成类型）
5. 联调验证契约一致性
```

## 产出物

| 产出物 | 位置 | 说明 |
|--------|------|------|
| `openapi.yaml` | 后端 `docs/` | API 设计稿 |
| `generated.ts` | 前端 `src/types/api/` | 自动生成的 TS 类型 |
| `mock-handlers.ts` | 前端 `src/mocks/` | MSW mock handler |
| 契约验证报告 | CI 产物 | 契约一致性检查结果 |
