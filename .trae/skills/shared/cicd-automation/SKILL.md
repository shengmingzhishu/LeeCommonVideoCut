---
name: cicd-automation
version: 1.0.0
description: CI/CD 自动化配置生成。GitHub Actions 工作流模板、部署脚本、环境配置管理。
---

# CI/CD 自动化技能

## 定位

为项目生成和管理 CI/CD 流水线配置，覆盖从代码提交到生产部署的全流程自动化。

## 核心能力

### 1. GitHub Actions 工作流模板

#### 后端 CI 模板

```yaml
# .github/workflows/backend-ci.yml
name: Backend CI
on:
  push:
    paths: ['ai-server/**']
  pull_request:
    paths: ['ai-server/**']

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install ruff mypy pytest pytest-cov
      - run: ruff check .
      - run: mypy --strict src/
      - run: pytest --cov --cov-fail-under=80

  integration:
    needs: quality
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8
        env:
          MYSQL_ROOT_PASSWORD: test
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/integration/

  security:
    needs: quality
    runs-on: ubuntu-latest
    steps:
      - run: pip install pip-audit
      - run: pip-audit
```

#### 前端 CI 模板

```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI
on:
  push:
    paths: ['ai-web/**']
  pull_request:
    paths: ['ai-web/**']

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm tsc --noEmit
      - run: pnpm test --coverage
      - run: pnpm audit --audit-level=high

  build:
    needs: quality
    runs-on: ubuntu-latest
    steps:
      - run: pnpm build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

### 2. 部署脚本

#### 后端 Docker 部署

```dockerfile
# Dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端 CDN 部署

```bash
# scripts/deploy-frontend.sh
pnpm build
aws s3 sync dist/ s3://$BUCKET_NAME/
aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
```

### 3. 环境配置管理

- `.env.example` 模板生成（列出所有需要的环境变量）
- CI/CD Secret 配置清单
- 多环境配置切换

## 使用流程

```
1. 确认项目技术栈（Python/React/全栈）
2. 生成对应的 CI 工作流文件
3. 生成部署脚本（Dockerfile / 部署脚本）
4. 配置环境变量（Secret/Vault）
5. 测试流水线（手动触发验证）
6. 上线流水线（自动触发）
```

## 产出物

| 产出物 | 位置 | 说明 |
|--------|------|------|
| CI 工作流 | `.github/workflows/` | GitHub Actions YAML |
| Dockerfile | 项目根目录 | 后端容器化 |
| 部署脚本 | `scripts/` | 部署+回滚脚本 |
| 环境配置 | `.env.example` | 环境变量清单 |
