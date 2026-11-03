# Python代码组织和结构规范

良好的代码组织使项目更易理解、维护和扩展。

## 文档字符串位置

每个模块、类和函数都应该有文档字符串，放在定义之后。

### 模块结构

```python
# module.py

"""
模块文档字符串
简要描述模块的用途。
"""

import sys

CONSTANT = "value"

def function_one():
    """函数文档字符串。"""
    pass

class MyClass:
    """类文档字符串。"""
    pass
```

### 导入顺序

1. **标准库导入**
2. **第三方库导入**
3. **本地应用/库导入**

每组导入之间用一个空行分隔。

### 正确示例
```python
# 1. 标准库
import os
import sys
from pathlib import Path

# 2. 第三方库
import numpy as np
import pandas as pd
from requests import get
from flask import Flask, jsonify

# 3. 本地导入
from myapp.config import settings
from myapp.utils import helpers
from myapp.models import User
```

### 不正确示例
```python
# 不好：混合导入顺序
from flask import Flask
import os
from myapp.config import settings
import sys
```

### 组内排序

每个导入组内部按字母顺序排列：

```python
# 正确：同一组内按字母顺序
import os
import sys
import time

from pathlib import Path
from typing import List, Optional

# 不正确：没有按字母顺序
import sys
import os
import time
```

### 避免通配符导入

不要使用 `from module import *`，明确导入需要的名称。

### 正确示例
```python
# 好的：明确导入
from datetime import datetime, timedelta
from typing import List, Dict, Optional
```

### 不正确示例
```python
# 不好：通配符导入
from datetime import *
from typing import *
```

## 模块内容顺序

一个Python模块应该按照以下顺序组织：

1. **模块文档字符串**（#!/usr/bin/env python 等 shebang 行如果有）
2. **导入语句**
3. **模块级别的常量和全局变量**
4. **异常类定义**
5. **辅助函数**
6. **类定义**
7. **主函数或main执行代码**

### 模板结构

```python
"""
模块文档字符串。

详细描述模块的功能、用法和注意事项。
"""

# ========== 导入 ==========
import sys
from typing import List, Optional
import requests

# ========== 常量 ==========
MAX_SIZE = 100
DEFAULT_TIMEOUT = 30

# ========== 异常类 ==========
class CustomError(Exception):
    """自定义异常类。"""
    pass

# ========== 辅助函数 ==========
def helper_function():
    """辅助函数。"""
    pass

# ========== 类定义 ==========
class MyClass:
    """主类定义。"""

    def __init__(self):
        """初始化方法。"""
        pass

    def method(self):
        """实例方法。"""
        pass

# ========== 主执行代码 ==========
def main():
    """主函数。"""
    pass


if __name__ == "__main__":
    main()
```

## 类的组织

### 类结构顺序

类成员应该按照以下顺序排列：

1. **类文档字符串**
2. **类变量/常量**
3. **__init__ 方法**
4. **类方法**（@classmethod）
5. **静态方法**（@staticmethod）
6. **属性装饰器**（@property）
7. **公共方法**
8. **私有方法**（以 `_` 开头）
9. **魔术方法**（以 `__` 开头和结尾）

### 正确示例

```python
class OrderProcessor:
    """
    订单处理器类。

    负责处理订单的创建、更新和查询。
    """

    # 类变量
    MAX_ORDERS = 1000
    DEFAULT_STATUS = "pending"

    def __init__(self, user_id: str):
        """
        初始化订单处理器。

        Args:
            user_id: 用户ID
        """
        self.user_id = user_id

    @classmethod
    def create_from_dict(cls, data: dict):
        """
        从字典创建实例。

        Args:
            data: 包含用户数据的字典

        Returns:
            OrderProcessor实例
        """
        return cls(user_id=data["user_id"])

    @staticmethod
    def validate_data(data: dict) -> bool:
        """
        验证数据格式。

        Args:
            data: 要验证的数据

        Returns:
            验证结果，True表示有效
        """
        return "user_id" in data

    @property
    def is_valid(self) -> bool:
        """检查处理器是否有效。"""
        return bool(self.user_id)

    def create_order(self, items: list) -> dict:
        """
        创建订单。

        Args:
            items: 商品列表

        Returns:
            订单信息字典
        """
        pass

    def update_order(self, order_id: str, updates: dict) -> bool:
        """
        更新订单。

        Args:
            order_id: 订单ID
            updates: 更新内容字典

        Returns:
            更新是否成功
        """
        pass

    def _send_notification(self, message: str) -> None:
        """
        发送通知（私有方法）。

        Args:
            message: 通知消息
        """
        pass

    def __len__(self) -> int:
        """返回订单数量。"""
        return 0

    def __repr__(self) -> str:
        """返回对象表示。"""
        return f"OrderProcessor(user_id={self.user_id})"
```

## 函数/方法内部组织

### 函数结构

1. **文档字符串**
2. **类型提示**（可选但推荐）
3. **参数验证**
4. **主要逻辑**
5. **返回值**

### 最佳实践

```python
def process_user_data(
    user_id: str,
    data: dict,
    validate: bool = True
) -> dict:
    """
    处理用户数据。

    Args:
        user_id: 用户ID
        data: 用户数据字典
        validate: 是否验证数据，默认为True

    Returns:
        处理后的数据字典

    Raises:
        ValueError: 当数据无效时
    """
    # 参数验证
    if not user_id:
        raise ValueError("user_id不能为空")

    if validate:
        if not isinstance(data, dict):
            raise TypeError("data必须是字典类型")

    # 数据处理
    processed_data = {
        "user_id": user_id,
        "data": data,
        "status": "processed"
    }

    # 返回结果
    return processed_data
```

## 文件和目录组织

### 包结构

```
my_package/
├── __init__.py           # 包初始化文件
├── core/                 # 核心功能
│   ├── __init__.py
│  ── module_a.py
│   └── module_b.py
├── utils/                # 工具函数
│   ├── __init__.py
│   └── helpers.py
├── config/               # 配置
│   ├── __init__.py
│   └── settings.py
├── models/               # 数据模型
│   ├── __init__.py
│   └── schemas.py
└── tests/                # 测试
    ├── __init__.py
    └── test_module_a.py
```

### 文件组织原则

1. **一个文件一个主要类或一组相关功能**
2. **文件名使用 snake_case 命名**
3. **测试文件以 `test_` 开头**
4. **测试目录结构与源代码结构对应**

## 空行使用

### 函数间空行

```python
# 正确：函数间使用两个空行
def function_one():
    pass


def function_two():
    pass
```

### 类内方法间空行

```python
# 正确：类内方法间使用一个空行
class MyClass:

    def method_one(self):
        pass

    def method_two(self):
        pass
```

### 不要过度的空行

```python
# 不正确：函数内部有过多的空行
def function():
    value = 1


    value += 2


    return value
```

## 代码分组

通过空行和相关注释，将代码按功能逻辑分组。

```python
def process_order(order):
    # 验证订单
    if not order:
        raise ValueError("无效订单")

    # 计算数量
    total = sum(item["price"] for item in order["items"])

    # 应用折扣
    if total > 100:
        total *= 0.9

    # 保存订单
    save_to_database(order, total)

    # 发送通知
    send_notification(order)

    return total
```

## 主程序入口

使用 `if __name__ == "__main__":` 来保护主执行代码。

```python
def main():
    """主函数。"""
    # 主程序逻辑
    print("程序启动")

if __name__ == "__main__":
    main()
```

## 组织原则总结

1. **导入规范**：标准库 → 第三方 → 本地
2. **模块顺序**：文档 → 导入 → 常量 → 异常 → 类 → 主函数
3. **类内顺序**：__init__ → 类方法 → 静态方法 → 公共方法 → 私有方法
4. **适当的空行**：函数间2行，方法间1行
5. **保护主入口**：使用 `if __name__ == "__main__":`
6. **逻辑分组**：使用空行和注释对相关代码分组
7. **单一职责**：每个模块/类/函数专注于一个目的
8. **清晰的命名**：文件和目录名使用 snake_case

## 测试文件组织

测试应该反映源代码结构：

```
my_package/
├── core/
│   ├── __init__.py
│   └── processor.py
└── tests/
    ├── __init__.py
    └── test_processor.py   # 对应 processor.py
```

测试文件应该包含：

```python
"""
测试 processor 模块的功能。
"""
import pytest
from my_package.core.processor import Processor


class TestProcessor:
    """测试 Processor 类。"""

    def test_init(self):
        """测试初始化。"""
        processor = Processor()
        assert processor is not None

    def test_process(self):
        """测试处理功能。"""
        processor = Processor()
        result = processor.process(input_data)
        assert result is not None
```
