---
name: security-audit
version: 1.0.0
description: 安全审计。依赖漏洞扫描、密钥泄露检查、OWASP Top 10 检查清单、安全审计报告生成。
---

# 安全审计技能

## 定位

系统化安全检查，覆盖依赖漏洞、密钥泄露、OWASP Top 10，产出结构化安全审计报告。

## 审计流程

### 1. 依赖漏洞扫描

#### 后端

```bash
# pip-audit 扫描已知漏洞
pip install pip-audit
pip-audit

# 或使用 safety
pip install safety
safety check
```

#### 前端

```bash
# pnpm audit
pnpm audit --audit-level=high

# 或使用 npm audit
npm audit --audit-level=high
```

**漏洞等级分类**：

| 等级 | 响应时间 | 处理方式 |
|------|---------|---------|
| Critical | 24h 内 | 立即修复，阻断发布 |
| High | 3 天内 | 优先修复 |
| Medium | 1 周内 | 计划修复 |
| Low | 下个迭代 | 记录跟踪 |

### 2. 密钥泄露检查

扫描代码仓库中的硬编码密钥：

```bash
# 使用 truffleHog 或 gitleaks
# 扫描 Git 历史中的密钥泄露
trufflehog git file://. --results=verified,unknown

# 或使用 gitleaks
gitleaks detect --source . --verbose
```

**检查清单**：
- [ ] 无硬编码的 API Key / Token
- [ ] 无硬编码的数据库密码
- [ ] `.env` 文件在 `.gitignore` 中
- [ ] 日志中敏感信息已脱敏
- [ ] 配置文件中无明文密钥
- [ ] 前端代码中无任何密钥（前端不应包含密钥）

### 3. OWASP Top 10 检查

#### A01 - 失效的访问控制

- [ ] 所有 API 接口校验 JWT Token
- [ ] 用户只能访问自己的数据（user_id 过滤）
- [ ] 管理接口有额外的权限校验
- [ ] 前端路由有权限守卫

#### A02 - 加密失败

- [ ] 密码使用 bcrypt/argon2 加盐哈希
- [ ] HTTPS 强制（生产环境）
- [ ] 敏感数据传输加密
- [ ] 日志中敏感信息脱敏

#### A03 - 注入

- [ ] SQL 查询使用 ORM 或参数化
- [ ] 无命令注入风险（禁止 `os.system` + 用户输入）
- [ ] 无路径穿越风险（文件路径校验）

#### A04 - 不安全设计

- [ ] 认证流程有速率限制
- [ ] 密码强度校验
- [ ] 关键操作有二次确认

#### A05 - 安全配置错误

- [ ] 生产环境关闭 debug
- [ ] CORS 配置正确（非 `*`）
- [ ] 安全 headers 配置（CSP、X-Frame-Options 等）
- [ ] 错误信息不泄露堆栈

#### A06 - 易受攻击的组件

- [ ] 依赖漏洞扫描通过
- [ ] 无已废弃的依赖
- [ ] 依赖版本锁定

#### A07 - 认证失败

- [ ] Token 有过期时间
- [ ] Token 刷新机制安全
- [ ] 登录失败有锁定机制
- [ ] 会话注销有效

#### A08 - 数据完整性失败

- [ ] CI/CD 流水线有安全门禁
- [ ] 依赖来源可信
- [ ] 构建产物可验证

#### A09 - 日志与监控不足

- [ ] 安全事件有日志记录
- [ ] 日志包含 trace_id
- [ ] 生产环境有错误监控
- [ ] 异常登录有告警

#### A10 - SSRF

- [ ] 外部 URL 请求校验白名单
- [ ] 禁止访问内网 IP
- [ ] 外部请求有超时设置

### 4. 前端安全检查

- [ ] 无 XSS 风险（`dangerouslySetInnerHTML` 已清洗）
- [ ] 无敏感信息存储在 localStorage
- [ ] `href` 属性无 `javascript:` 协议
- [ ] 富文本内容经 DOMPurify 清洗
- [ ] 生产构建无 sourcemap（或使用 hidden sourcemap）

## 产出物

| 产出物 | 位置 | 说明 |
|--------|------|------|
| 安全审计报告 | `docs/security-audit-{date}.md` | 完整检查结果 |
| 漏洞清单 | 报告内 | 按等级排序的漏洞列表 |
| 修复建议 | 报告内 | 每个漏洞的修复方案 |
