---
name: api-mock
version: 1.0.0
description: 前端 API Mock。MSW (Mock Service Worker) 配置、假数据生成、接口 Mock 服务器。后端 API 未就绪时使用。
---

# API Mock 技能

## 定位

在后端 API 未就绪时，为前端提供模拟 API 响应，实现前后端并行开发。

## 核心能力

### 1. MSW 配置

```typescript
// src/mocks/server.ts
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

const handlers = [
  // GET: 获取评测套件列表
  http.get('/api/eval/suites', () => {
    return HttpResponse.json({
      items: [
        { id: 1, title: 'RAG评测套件', direction: 'rag', status: 'active' },
        { id: 2, title: 'SQL评测套件', direction: 'sql', status: 'draft' },
      ],
      total: 2,
      page: 1,
      pageSize: 20,
    });
  }),

  // POST: 创建评测套件
  http.post('/api/eval/suites', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: 3, ...body, status: 'draft' }, { status: 201 });
  }),

  // 模拟错误响应
  http.get('/api/eval/suites/999', () => {
    return HttpResponse.json(
      { code: 'EVAL_404_001', message: '评测套件不存在', trace_id: 'mock-xxx' },
      { status: 404 },
    );
  }),
];

export const server = setupServer(...handlers);
```

### 2. 从 OpenAPI 生成 Mock

```bash
# 使用 openapi-mock-express 或 msw-auto-mock
npx msw-auto-mock --input openapi.json --output src/mocks/handlers.ts
```

### 3. 假数据生成

```typescript
// src/mocks/factories.ts
import { faker } from '@faker-js/faker';

export function createMockSuite(overrides = {}) {
  return {
    id: faker.number.int(),
    title: faker.lorem.words(3),
    direction: faker.helpers.arrayElement(['text_qa', 'sql', 'rag', 'code']),
    status: faker.helpers.arrayElement(['draft', 'active', 'archived']),
    createdAt: faker.date.recent().toISOString(),
    ...overrides,
  };
}

export function createMockSuiteList(count = 10) {
  return Array.from({ length: count }, () => createMockSuite());
}
```

### 4. 开发环境启用 Mock

```typescript
// src/main.tsx
async function enableMocking() {
  if (import.meta.env.VITE_ENABLE_MOCK === 'true') {
    const { worker } = await import('./mocks/browser');
    return worker.start({
      onUnhandledRequest: 'bypass', // 未 mock 的请求正常发出
    });
  }
}

enableMocking().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(<App />);
});
```

### 5. 测试环境启用 Mock

```typescript
// vitest.setup.ts
import { server } from './src/mocks/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## 使用流程

```
1. 从 api-contract 获取 OpenAPI 定义
2. 生成 MSW handlers（手动或自动）
3. 生成假数据工厂函数
4. 开发环境启用 MSW
5. 前端开发完成后，关闭 Mock 直连后端
6. 测试中继续使用 MSW（集成测试）
```

## 环境变量配置

```env
# .env.development
VITE_ENABLE_MOCK=true
VITE_API_BASE_URL=http://localhost:8000

# .env.production
VITE_ENABLE_MOCK=false
VITE_API_BASE_URL=https://api.example.com
```
