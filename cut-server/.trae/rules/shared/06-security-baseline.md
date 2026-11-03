---
alwaysApply: false
description: 安全基线规则，包括输入校验、密钥管理、文件上传安全、SQL 注入防护、接口鉴权、CORS 配置。涉及安全相关代码、认证、文件操作、数据库操作时使用此规则。
---

# 安全基线（共享层）

> 前后端共用安全基线，涉及安全相关代码时必须遵守。

## 1. 输入校验

### 1.1 后端

- **所有外部输入必须校验**：API 参数、文件内容、外部系统返回值
- 使用 Pydantic Schema 校验请求体，禁止直接使用 `dict` 接收输入
- 字符串输入必须限制最大长度，防止缓冲区攻击
- 文件路径输入必须校验，禁止 `..` 路径穿越

```python
# 正确
class EvalCaseCreate(BaseModel):
    title: str = Field(..., max_length=200)
    direction: EvalDirection

# 错误
async def create_case(data: dict): ...  # 禁止
```

### 1.2 前端

- 用户输入必须做前端校验（Form rules）
- 前端校验仅为体验优化，**后端必须再次校验**
- 输入框限制最大字符数
- 富文本输入必须做 XSS 过滤（DOMPurify）

## 2. 密钥管理

### 2.1 禁止硬编码

- API Key、Token、密码、数据库连接串必须走环境变量
- `.env` 文件不提交到 Git（`.gitignore` 必须包含）
- 日志中敏感信息必须脱敏

```python
# 后端正确
API_KEY = os.getenv('LLM_API_KEY')
# 后端错误
API_KEY = "sk-xxxxxxxxxxxx"  # 禁止
```

```typescript
// 前端正确
const API_BASE = import.meta.env.VITE_API_BASE_URL;
// 前端错误
const API_KEY = "sk-xxxx";  // 禁止，前端不应有任何密钥
```

### 2.2 密钥脱敏规则

- Token 只显示前 4 位 + `***`
- 密码字段日志中显示为 `***`
- 数据库连接串中密码替换为 `***`

## 3. 文件上传安全

- 校验扩展名白名单 + 文件大小（默认 10MB）
- 文件名必须重命名或 sanitize，防止路径穿越
- 上传文件存储路径不可由用户输入控制
- 前端上传前校验文件类型和大小

## 4. 密码存储

- 用户密码必须加盐哈希存储（`bcrypt` 或 `argon2`），禁止明文
- 密码强度校验：最少 8 位，包含字母和数字
- 前端密码输入框禁止 autocomplete

## 5. SQL 注入防护

- **禁止拼接 SQL 字符串**，必须使用 ORM 或参数化查询
- 如需原生 SQL，必须使用 `text()` + 绑定参数

```python
# 正确
session.query(EvalCase).filter(EvalCase.id == case_id).first()
session.execute(text("SELECT * FROM t WHERE id = :id"), {"id": case_id})

# 错误
session.execute(text(f"SELECT * FROM t WHERE id = {case_id}"))  # 禁止
```

## 6. 接口鉴权

- 所有业务接口必须校验 JWT Token（登录/注册除外）
- Token 从 `Authorization: Bearer <token>` 获取，过期返回 401
- 用户只能访问自己的数据，查询必须包含 `user_id` 过滤
- 前端 Token 存储在 localStorage（非 sessionStorage），刷新机制保证不中断

## 7. XSS / CSRF 防护

### 7.1 XSS

- 前端禁止 `dangerouslySetInnerHTML`（除非经过 DOMPurify 清洗）
- 后端返回的 HTML 内容必须转义
- React 默认转义，但注意 `href` 属性中的 `javascript:` 协议

### 7.2 CSRF

- 使用 SameSite Cookie 属性（`SameSite=Strict` 或 `Lax`）
- 敏感操作要求二次确认（如删除操作需前端弹窗确认）
- API 使用 JWT Bearer Token 而非 Cookie 认证，天然免疫 CSRF

## 8. CORS 配置

- CORS 必须限制允许的域名，禁止 `*`
- 允许的 Methods：`GET, POST, PUT, DELETE, OPTIONS`
- 允许的 Headers：`Authorization, Content-Type, X-Trace-Id`
- 预检请求缓存时间：3600s

## 9. 生产环境安全

- 关闭 `debug=True`，错误响应不返回堆栈信息
- 外部 API 调用必须设置超时（默认 30s）
- 日志中禁止记录完整的请求体/响应体
- 前端生产构建禁用 sourcemap（或使用 hidden sourcemap）

## 10. 依赖安全

- 定期运行依赖漏洞扫描（后端 `pip-audit`，前端 `pnpm audit`）
- 发现高危漏洞必须在 3 天内修复
- 禁止使用已废弃或无维护的包
- CI 中集成安全扫描步骤
