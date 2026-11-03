---
name: integration-testing
version: 1.0.0
description: 前后端集成测试。联调测试、契约测试（Pact 模式）、API 集成测试。确保前后端接口对齐。
---

# 集成测试技能

## 定位

验证前后端接口对接的正确性，确保契约一致、数据流通、错误处理对齐。

## 核心能力

### 1. 联调测试

前后端直连环境下的端到端接口验证：

```
前端 dev server → 后端 staging API → 数据库
```

**联调检查清单**：
- [ ] Path 和 Method 对齐
- [ ] 请求参数类型和必填项对齐
- [ ] 响应字段名和类型对齐
- [ ] 错误码定义对齐
- [ ] 分页参数和返回格式对齐
- [ ] 认证 Token 格式对齐
- [ ] CORS 配置正确

### 2. 契约测试（Contract Testing）

使用 Pact 模式验证前后端契约：
- 消费端（前端）定义期望的请求和响应
- 提供端（后端）验证是否满足所有消费者期望
- CI 中自动运行，变更时自动检测影响

### 3. API 集成测试

后端 API 端到端测试：
- 启动真实服务（或 testcontainers）
- 通过 httpx 调用完整 API 流程
- 验证数据库状态变化

```python
# 后端集成测试示例
async def test_eval_full_flow(client, db_session):
    # 1. 创建评测套件
    resp = await client.post("/api/eval/suites", json={...})
    assert resp.status_code == 200
    suite_id = resp.json()["id"]

    # 2. 添加用例
    resp = await client.post(f"/api/eval/suites/{suite_id}/cases", json={...})
    assert resp.status_code == 200

    # 3. 运行评测
    resp = await client.post(f"/api/eval/suites/{suite_id}/run")
    assert resp.status_code == 200

    # 4. 查看结果
    resp = await client.get(f"/api/eval/suites/{suite_id}/results")
    assert resp.status_code == 200
```

### 4. 前端集成测试

使用 Vitest + MSW 测试组件与 API 的集成：
- MSW 模拟后端响应
- 验证组件渲染、数据流、状态变化

```typescript
// 前端集成测试示例
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/eval/suites', (req, res, ctx) => {
    return res(ctx.json({ items: [...], total: 10 }));
  }),
);

test('EvalListPage displays suites from API', async () => {
  render(<EvalListPage />);
  expect(await screen.findByText('Test Suite 1')).toBeInTheDocument();
});
```

## 使用流程

```
1. 确认 API 契约已定义（api-contract skill）
2. 后端实现完成 → 运行后端集成测试
3. 前端实现完成 → 运行前端集成测试（MSW Mock）
4. 前后端联调 → 运行联调测试
5. 运行契约测试（Pact）→ 验证契约一致性
6. 全部通过 → 可进入发布阶段
```

## 产出物

| 产出物 | 位置 | 说明 |
|--------|------|------|
| 联调测试报告 | `tests/output/` | 联调检查清单结果 |
| 契约测试结果 | CI 产物 | Pact 验证结果 |
| 集成测试代码 | `tests/integration/` | 后端+前端集成测试 |
