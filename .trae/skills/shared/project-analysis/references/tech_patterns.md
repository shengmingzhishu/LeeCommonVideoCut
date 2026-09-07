# 技术栈特征库

本文件存储各种编程语言、框架和工具的特征识别模式。

## 编程语言特征

### JavaScript / TypeScript

**文件扩展名：**
- .js
- .jsx
- .ts
- .tsx

**标志性文件：**
- package.json
- tsconfig.json
- jsconfig.json
- .eslintrc.js
- .prettierrc

**常见框架：**
- React: react, react-dom, @types/react
- Vue: vue, @vue/*
- Angular: @angular/, angular
- Next.js: next, next-auth
- Nuxt: nuxt
- Express: express
- Nest: @nestjs/
- Svelte: svelte

**构建工具：**
- Vite: vite
- Webpack: webpack
- Rollup: rollup
- esbuild: esbuild
- Parcel: parcel

**测试框架：**
- Jest: jest
- Vitest: vitest
- Mocha: mocha

### Python

**文件扩展名：**
- .py
- .pyw

**标志性文件：**
- requirements.txt
- requirements-dev.txt
- pyproject.toml
- setup.py
- setup.cfg
- Pipfile
- poetry.lock
- venv/
- .venv/

**常见框架：**
- Django: django
- Flask: flask
- FastAPI: fastapi
- Tornado: tornado
- Sanic: sanic
- Pyramid: pyramid
- Bottle: bottle

**测试框架：**
- PyTest: pytest
- unittest: unittest
- nose2: nose2

### Java

**文件扩展名：**
- .java

**标志性文件：**
- pom.xml
- build.gradle
- settings.gradle
- gradlew
- mvnw

**常见框架：**
- Spring Boot: spring-boot
- Spring Framework: springframework
- Hibernate: hibernate
- MyBatis: mybatis
- JUnit: junit

**测试框架：**
- JUnit: junit
- TestNG: testng

### Rust

**文件扩展名：**
- .rs

**标志性文件：**
- Cargo.toml
- Cargo.lock

**常见工具：**
- Cargo: cargo

### Go

**文件扩展名：**
- .go

**标志性文件：**
- go.mod
- go.sum

**常见框架：**
- Gin: gin
- Echo: echo
- Fiber: fiber

### PHP

**文件扩展名：**
- .php

**标志性文件：**
- composer.json
- composer.lock

**常见框架：**
- Laravel: laravel
- Symfony: symfony
- CodeIgniter: codeigniter

### Ruby

**文件扩展名：**
- .rb

**标志性文件：**
- Gemfile
- Gemfile.lock

**常见框架：**
- Rails: rails
- Sinatra: sinatra

## 框架特性

### React

**特征代码：**
```javascript
import React from 'react';
import { useState, useEffect } from 'react';

function Component() {
  return <div>Hello</div>;
}
```

**文件名模式：**
- components/
- hooks/
- use*.js/use*.ts
- *Component.js/*.jsx

### Vue

**特征代码：**
```vue
<template>
  <div>
    <h1>{{ title }}</h1>
  </div>
</template>

<script>
export default {
  name: 'ComponentName'
}
</script>

<style scoped>
</style>
```

**文件扩展名：**
- .vue

### Angular

**特征代码：**
```typescript
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: '<h1>Hello</h1>',
  styles: ['']
})
export class AppComponent {}
```

**文件名模式：**
- *.component.ts
- *.service.ts
- *.module.ts

### Django

**特征代码：**
```python
from django.db import models
from django.http import HttpResponse

def my_view(request):
    return HttpResponse("Hello")
```

**文件名模式：**
- models.py
- views.py
- urls.py
- admin.py
- settings.py

### Spring Boot

**特征代码：**
```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**注解：**
- @RestController
- @Controller
- @Service
- @Repository
- @Entity

## 构建工具特征

### Vite

**配置文件：**
- vite.config.js
- vite.config.ts

**features：**
- 快速冷启动
- 即时热更新
- 原生 ESM 支持

### Webpack

**配置文件：**
- webpack.config.js
- webpack.config.ts

**features：**
- 模块打包
- 代码分割
- Tree Shaking

### Gradle

**配置文件：**
- build.gradle
- build.gradle.kts

### Maven

**配置文件：**
- pom.xml

**features：**
- 依赖管理
- 生命周期管理

## 测试框架特征

### Jest

**配置文件：**
- jest.config.js
- jest.config.ts
- package.json 中的 jest 配置

**测试文件模式：**
- *.test.js
- *.test.ts
- *.spec.js
- *.spec.ts

### PyTest

**特征代码：**
```python
def test_function():
    assert True

class TestClass:
    def test_method(self):
        assert True
```

**测试文件模式：**
- test_*.py
- *_test.py

### JUnit

**特征代码：**
```java
import org.junit.Test;

public class MyTest {
    @Test
    public void testMethod() {
        // test code
    }
}
```

**测试文件模式：**
- *Test.java
- *Tests.java

## 其他特征

### 微前端架构

**特征：**
- packages/ 目录
- apps/ 目录
- lerna.json
- nx.json
- pnpm-workspace.yaml

### Monorepo 架构

**特征：**
- packages/ 目录
- apps/ 目录
- workspace 配置文件

### Serverless

**特征：**
- serverless.yml
- netlify.toml
- vercel.json
- .aws-sam/

### PWA

**特征：**
- manifest.json
- service-worker.js
- sw.js
- workbox 配置

## 版本识别规则

### SemVer

**格式：** MAJOR.MINOR.PATCH

**示例：**
- 1.0.0
- 2.3.4
- 1.2.3-beta.1
- 2.0.0-rc.1

### 其他版本格式

- npm: ^1.2.3, ~1.2.3, 1.2.x, >=1.2.3
- pip: >=1.2.3, ~=1.2.3, ==1.2.3
- maven: 1.2.3-SNAPSHOT, [1.2.3,)
- gradle: 1.2.3+, 1.2.+ (不推荐)

## 安全相关

### 常见漏洞库

- NVD (National Vulnerability Database)
- npm audit
- pip-audit
- Snyk
- OWASP Dependency Check

### 敏感信息模式

- API_KEY, api_key
- SECRET_KEY, secret_key
- PASSWORD, password
- TOKEN, token
- ACCESS_TOKEN, access_token
- PRIVATE_KEY, private_key
- AWS_ACCESS_KEY, aws_access_key
- DATABASE_URL, database_url

## 性能优化特征

### 代码分割

- 动态 import()
- React.lazy()
- import()
- Webpack SplitChunksPlugin

### 图片优化

- sharp
- imagemin
- next/image (Next.js)
- @nuxt/image (Nuxt)

### 缓存

- Redis
- Memcached
- CDN 配置

### 压缩

- Gzip
- Brotli
- zlib
