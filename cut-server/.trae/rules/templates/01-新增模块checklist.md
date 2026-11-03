# 新增模块 Checklist

> 在 ai-server 四层架构中新增模块时，逐项确认。

## 前置确认

- [ ] 已确定模块所属层级（Controller / Service / Manager / Model / core）
- [ ] 已在 `rules/project/01-project-specific.md` §2 中找到对应目录位置
- [ ] 已确认模块命名符合领域前缀规范

## Controller 层模块

- [ ] 文件名格式：`{domain}_controller.py`
- [ ] 类名：`{Domain}Controller`，继承基类（如有）
- [ ] 路由使用 `APIRouter`，prefix 符合 RESTful 规范
- [ ] 每个端点有 Pydantic 模型做请求/响应校验
- [ ] 调用依赖注入获取 Service 实例（非直接 import 创建）
- [ ] 端点有鉴权装饰器（公开接口除外）
- [ ] 错误返回使用统一格式（非裸抛异常）

## Service 层模块

- [ ] 文件名格式：`{domain}_service.py`
- [ ] 类名：`{Domain}Service`
- [ ] 方法参数使用业务对象/Pydantic 模型（非 Request 对象）
- [ ] 不直接操作数据库（通过 Model/Repository）
- [ ] 不包含 HTTP 相关逻辑
- [ ] 公开方法有完整 docstring（Args / Returns / Raises）

## Manager 层模块

- [ ] 文件名格式：`{domain}_manager.py`
- [ ] 类名：`{Domain}Manager}`
- [ ] 确实需要跨领域编排（否则应放在 Service 层）
- [ ] 不暴露给 Controller 层直接调用
- [ ] 外部系统调用有超时、重试、日志记录

## Model 层模块

### Schema（Pydantic）

- [ ] 文件在 `models/schemas/{domain}.py`
- [ ] 使用 Pydantic v2 BaseModel（非 dataclass，除非有特殊需求）
- [ ] 必填字段有默认值约束或 `Field(...)` 标记
- [ ] 有字段描述（`description`）和示例（`example`）

### Entity（ORM）

- [ ] 文件在 `models/entities/{domain}.py`
- [ ] 表名使用 snake_case
- [ ] 有索引定义（查询字段）
- [ ] `created_at` / `updated_at` 字段齐全
- [ ] 关联关系使用 lazy loading（避免 N+1）

## core/ 组件

- [ ] 文件在 `core/` 目录下
- [ ] 继承对应基类（BaseEvaluator / BaseScorer 等）
- [ ] 不 import 任何层的模块（纯策略实现）
- [ ] 可通过配置名称字符串实例化（支持动态加载）

## 测试

- [ ] 测试文件在 `tests/test_{module}.py`
- [ ] 覆盖正常路径 + 异常路径 + 边界条件
- [ ] 使用 fixture 管理测试数据（非硬编码）
- [ ] Mock 外部依赖（数据库、HTTP 调用等）

## 文档更新

- [ ] `rules/project/01-project-specific.md` §2 模块结构已更新
- [ ] 如涉及新接口，`plan/04-接口文档.md` 已更新
- [ ] 如涉及新评测方向，`project-specific.md` §1.2 枚举已更新
- [ ] `plan/08-代码日志.md` 已追加本次变更记录
