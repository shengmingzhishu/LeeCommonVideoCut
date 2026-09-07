# 架构模式库

本文件存储常见的项目架构模式和特征识别规则。

## 前端架构模式

### MVC (Model-View-Controller)

**特征目录：**
- models/
- views/
- controllers/

**职责：**
- models: 数据模型和业务逻辑
- views: 用户界面
- controllers: 处理用户输入和协调

**适用场景：**
- 传统 Web 应用
- 需要清晰分离的中小型项目

**示例项目：**
- Django 项目
- Rails 项目

### Micro-Frontend (微前端)

**特征目录：**
- apps/ 或 microfrontends/
- packages/ 或 shared/
- host/ 或 shell/

**特征配置：**
- qiankun 配置
- Webpack Module Federation
- lerna.json
- nx.json

**职责：**
- apps/: 各个独立的微前端应用
- packages/: 共享的组件和工具库

**适用场景：**
- 大型企业级应用
- 多团队协作
- 独立部署需求

**示例项目：**
- 阿里 qiankun 项目
- 微前端电商平台

### Monorepo (单体仓库)

**特征目录：**
- packages/
- apps/
- libs/
- tools/

**特征配置：**
- pnpm-workspace.yaml
- lerna.json
- nx.json
- rush.js

**职责：**
- packages/: 独立的包或组件库
- apps/: 应用程序
- libs/: 共享库

**适用场景：**
- 多包项目
- 组件库 + 应用
- 工具 + 应用

**示例项目：**
- monorepo 组件库
- workspace 项目

### SPA (Single Page Application)

**特征目录：**
- dist/
- public/
- src/
  - components/
  - pages/
  - routes/

**特征配置：**
- router 配置
- 状态管理配置

**适用场景：**
- 单页应用
- 需要流畅用户体验

**示例项目：**
- React SPA
- Vue SPA

### SSR (Server-Side Rendering)

**特征目录：**
- server/
- client/
- pages/ (Next.js)
- render/ (Remix)

**特征配置：**
- server.js 或 server.ts
- Next.js 配置
- Nuxt.js 配置

**适用场景：**
- SEO 优化
- 首屏性能要求高

**示例项目：**
- Next.js 项目
- Nuxt.js 项目
- Remix 项目

## 后端架构模式

### Layered Architecture (分层架构)

**特征目录：**
- controller/ 或 handlers/
- service/ 或 services/
- repository/ 或 dao/
- model/ or entity/
- dto/ 或 vo/

**职责：**
- controller: 控制层，处理 HTTP 请求
- service: 服务层，业务逻辑
- repository: 数据访问层，数据库操作
- model: 数据模型
- dto: 数据传输对象

**适用场景：**
- 中小型后端项目
- 清晰的关注点分离

**示例项目：**
- Spring Boot 应用
- Django 服务

### Event-Driven Architecture (事件驱动)

**特征目录：**
- events/
- handlers/
- subscribers/
- publishers/

**特征配置：**
- 消息队列配置（RabbitMQ, Kafka）
- 事件总线配置

**适用场景：**
- 微服务架构
- 异步处理
- 解耦系统组件

**示例项目：**
- 微服务系统
- 事件处理应用

### Clean Architecture (清洁架构)

**特征目录：**
- domain/
  - entities/
  - usecases/
- application/
  - dto/
  - services/
- infrastructure/
  - persistence/
  - external-services/
- interfases/
  - controllers/

**职责：**
- domain: 核心业务逻辑
- application: 应用服务
- infrastructure: 基础设施实现
- interfaces: 外部接口

**适用场景：**
- 复杂业务系统
- 长期维护的项目

**示例项目：**
- 企业级应用
- 复杂的 DDD 项目

### Hexagonal Architecture (六边形架构)

**特征目录：**
- core/
  - domain/
  - application/
- adapters/
  - web/
  - database/
  - external-apis/

**职责：**
- core: 核心业务逻辑
- adapters: 各种适配器

**适用场景：**
- 可插拔架构
- 多数据源/接口

**示例项目：**
- 可扩展的企业系统

### Microservices (微服务)

**特征结构：**
- 多个独立的服务目录
- 共享的库
- API 网关配置

**特征配置：**
- Docker Compose
- Kubernetes 配置
- 服务发现配置

**适用场景：**
- 大型分布式系统
- 团队独立部署

**示例项目：**
- 微服务平台
- 分布式电商

## 移动端架构模式

### MVVM (Model-View-ViewModel)

**特征目录：**
- models/
- viewmodels/
- views/
- repositories/

**职责：**
- models: 数据模型
- viewmodels: 视图模型
- views: 视图
- repositories: 数据仓库

**适用场景：**
- iOS (SwiftUI)
- Android (Jetpack Compose)
- React Native
- Flutter

**示例项目：**
- 移动应用
- 跨平台应用

### BLOC (Business Logic Component)

**特征目录：**
- bloc/
- states/
- events/
- screens/

**职责：**
- bloc: 业务逻辑组件
- states: 状态定义
- events: 事件定义
- screens: UI 屏幕页面

**适用场景：**
- Flutter 应用

**示例项目：**
- Flutter 应用

## 全栈架构模式

### 12-Factor App

**特征目录：**
- app/
- config/
- public/
- logs/

**特征规则：**
- 基准代码：代码库可追踪和版本化
- 依赖：明确声明和隔离
- 配置：配置与环境分离
- 后端服务：无状态进程
- 端口绑定：通过端口提供服务

**适用场景：**
- 云原生应用
- 容器化部署

**示例项目：**
- Heroku 应用
- Docker 应用

### BFF (Backend for Frontend)

**特征目录：**
- bff/
  - mobile-bff/
  - web-bff/
- api-gateway/

**职责：**
- bff/: 针对不同前端的专用后端
- api-gateway: API 网关

**适用场景：**
- 多端应用
- 需要定制化的 API

**示例项目：**
- 多移动端应用
- Web + Native 应用

### Headless CMS + Frontend

**特征结构：**
- 前端独立项目
- CMS 后台
- API 集成

**特征配置：**
- CMS 配置
- API 调用配置

**适用场景：**
- 内容驱动网站
- 多渠道内容分发

**示例项目：**
- Next.js + Contentful
- Gatsby + Strapi

## 设计模式

### 创建型模式

#### Factory Pattern (工厂模式)

**特征：**
- create*() 工厂方法
- *Factory 类
- build*() 方法

**示例代码：**
```javascript
const user = UserFactory.create(data);
```

#### Builder Pattern (建造者模式)

**特征：**
- Builder 类
- .build() 方法
- .with*() 链式调用

**示例代码：**
```javascript
const user = new UserBuilder()
  .withName('John')
  .withAge(30)
  .build();
```

#### Singleton Pattern (单例模式)

**特征：**
- getInstance() 方法
- 私有构造函数
- 静态实例变量

**示例代码：**
```javascript
const instance = Database.getInstance();
```

### 结构型模式

#### Adapter Pattern (适配器模式)

**特征：**
- Adapter 类
- 包装不兼容的接口

#### Decorator Pattern (装饰器模式)

**特征：**
- @decorator 注解
- 装饰器函数

#### Proxy Pattern (代理模式)

**特征：**
- Proxy 对象
- 拦截器

### 行为型模式

#### Observer Pattern (观察者模式)

**特征：**
- addListener() / on() 方法
- emit() / trigger() 方法
- EventEmitter
- @Subscribe 注解

**示例代码：**
```javascript
eventBus.on('event', handler);
eventBus.emit('event', data);
```

#### Strategy Pattern (策略模式)

**特征：**
- Strategy 接口
- 可互换的算法实现

#### Command Pattern (命令模式)

**特征：**
- Command 接口
- execute() 方法
- Undo/Redo 操作

#### Publisher-Subscriber Pattern (发布-订阅模式)

**特征：**
- pubsub.publish()
- pubsub.subscribe()
- 主题/主题管理器

**示例代码：**
```javascript
PubSub.publish('topic', message);
PubSub.subscribe('topic', handler);
```

## 前端特定模式

### Component Pattern (组件模式)

**特征：**
- 组件化开发
- Props + State
- 生命周期

### Container/Presenter Pattern

**特征：**
- 容器组件（逻辑）
- 展示组件（UI）

### Higher-Order Component Pattern (HOC)

**特征：**
- with*() 高阶函数
- 组件组合

### Render Props Pattern

**特征：**
- render prop 属性
- 动态渲染

### Custom Hook Pattern (自定义 Hook 模式)

**特征：**
- use*() 函数
- 逻辑复用

**示例代码：**
```javascript
const data = useFetch(url);
```

## 后端特定模式

### Repository Pattern (仓储模式)

**特征：**
- Repository 类
- CRUD 操作抽象
- 数据访问封装

**示例代码：**
```typescript
userRepository.findById(id);
userRepository.save(user);
```

### Service Layer Pattern (服务层模式)

**特征：**
- Service 类
- 业务逻辑封装
- 事务管理

### Unit of Work Pattern (工作单元模式)

**特征：**
- 管理多个 Repository
- 统一提交事务

### Data Transfer Object (DTO)

**特征：**
- DTO 类
- 数据传输对象
- 序列化/反序列化

<div style="font-size: 10px; margin-top: 20px; display: none;">

</div>
