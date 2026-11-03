---
alwaysApply: false
description: CI/CD 流水线规则，包括 CI 触发条件、构建/测试/部署阶段、环境管理、回滚机制。涉及 CI/CD 配置、部署、环境管理时使用此规则。
---

# CI/CD 流水线规则（共享层）

> 前后端共用 CI/CD 规范，确保交付流程一致。

## 1. CI 触发条件

| 触发事件 | 执行阶段 | 失败处理 |
|---------|---------|---------|
| push 到任意分支 | lint + type-check + unit test | 不阻塞 |
| PR 创建/更新 | + integration test + coverage + security scan | 阻止合并 |
| 合并到 main | + build + deploy staging | 通知 |
| tag (v*.*.*) | + full E2E + deploy prod | 阻止发布 |

## 2. 流水线阶段定义

### 2.1 代码质量阶段（所有触发）

```yaml
quality:
  steps:
    - name: lint          # 后端 ruff，前端 ESLint + Prettier
    - name: type-check    # 后端 mypy，前端 tsc --noEmit
    - name: unit-test     # 后端 pytest，前端 vitest
    - name: coverage      # 覆盖率门槛检查
```

### 2.2 集成测试阶段（PR 触发）

```yaml
integration:
  needs: quality
  steps:
    - name: integration-test   # 后端 testcontainers，前端 MSW
    - name: contract-test       # OpenAPI 契约验证
    - name: security-scan       # pip-audit / pnpm audit
```

### 2.3 构建阶段（合并 main 触发）

```yaml
build:
  needs: quality
  steps:
    - name: build               # 后端打包 wheel/docker，前端 pnpm build
    - name: push-image           # 推送到镜像仓库
    - name: deploy-staging      # 自动部署到 staging
```

### 2.4 发布阶段（tag 触发）

```yaml
release:
  needs: build
  steps:
    - name: e2e-test             # Playwright E2E（前端+后端）
    - name: security-audit       # 完整安全审计
    - name: deploy-prod          # 部署生产
    - name: smoke-test           # 烟雾测试
    - name: notify               # 通知团队
```

## 3. 环境管理

### 3.1 环境定义

| 环境 | 用途 | 数据 | 访问控制 |
|------|------|------|---------|
| dev | 本地开发 | 本地数据 | 开发者 |
| staging | 集成测试 | 测试数据 | 团队 |
| prod | 生产 | 真实数据 | 受控 |

### 3.2 环境变量管理

- 环境变量通过 CI/CD Secret 或 Vault 注入
- `.env.example` 提交到 Git，列出所有需要的环境变量
- `.env.development` / `.env.production` 不提交
- 前端：Vite 环境变量前缀 `VITE_`
- 后端：通过 `pydantic-settings` 管理

## 4. 部署策略

### 4.1 后端部署

- 容器化部署（Docker）
- 滚动更新策略，最少 1 个实例保持运行
- 健康检查：`/api/health` 端点
- 部署后自动烟雾测试

### 4.2 前端部署

- 静态资源部署到 CDN
- 构建产物 `dist/` 上传
- 版本号注入（`vite-plugin-version`）
- CDN 缓存策略：HTML 不缓存，JS/CSS 长缓存 + hash 文件名

## 5. 回滚机制

### 5.1 后端回滚

- 保留最近 3 个版本的 Docker 镜像
- 回滚命令：指定镜像版本重新部署
- 数据库迁移回滚：Alembic downgrade（如可用）

### 5.2 前端回滚

- 保留最近 3 个版本的构建产物
- 回滚命令：切换 CDN 指向到上一版本
- 前端回滚无需数据库回滚

### 5.3 回滚触发条件

- 部署后烟雾测试失败
- 生产环境错误率 > 5%
- 核心功能不可用
- 安全漏洞被发现且无法热修

## 6. 质量门禁

### 6.1 PR 必须通过

- [ ] lint 无 error
- [ ] type-check 无 error
- [ ] unit test 全部通过
- [ ] coverage ≥ 80%（核心模块）
- [ ] integration test 全部通过
- [ ] security scan 无高危
- [ ] code review 通过（至少 1 人 approve）

### 6.2 发布必须通过

- [ ] 所有 PR 检查通过
- [ ] E2E 测试全部通过
- [ ] 烟雾测试通过
- [ ] 回滚方案已确认

## 7. CI/CD 工具

- 推荐：GitHub Actions
- 后端 CI 模板：`.github/workflows/backend-ci.yml`
- 前端 CI 模板：`.github/workflows/frontend-ci.yml`
- 部署脚本：`scripts/deploy-backend.sh` / `scripts/deploy-frontend.sh`
