# Python命名规范

遵循清晰、一致的命名约定，提高代码可读性和维护性。

## 通用命名原则

1. **使用描述性名称**：名称应该清楚地表达其用途
2. **避免使用单字符变量**：除循环计数器(i, j, k)外
3. **不使用Python关键字**：避免与Python保留字冲突
4. **名称要简洁而完整**：在清晰的前提下尽可能简短

## 模块命名（Modules）

- **全小写**：使用小写字母
- **下划线分隔**：多个单词用下划线 `_` 连接
- **避免使用下划线开头/结尾**（特殊的除外）

### 正确示例
```python
# 好的模块名
import os
import sys
import my_module
import data_processing
import http_server
```

### 不正确示例
```python
# 不好：驼峰命名
import MyModule
import dataProcessing

# 不好：大写
import DATA_PROCESSING
```

## 类命名（Classes）

- **首字母大写驼峰命名**（CapWords/PascalCase）
- 每个单词首字母大写，不使用分隔符
- 私有类以单下划线 `_` 开头

### 正确示例
```python
# 好的类名
class User:
    pass

class HttpRequest:
    pass

class DatabaseConnection:
    pass

class _InternalClass:  # 私有类
    pass
```

### 不正确示例
```python
# 不好：小写
class user:
    pass

# 不好：下划线分隔
class http_request:
    pass

# 不好：蛇形命名
class database_connection:
    pass
```

## 函数/方法命名（Functions/Methods）

- **小写字母+下划线**：使用小写蛇形命名（snake_case）
- 使用描述性动词开头
- 私有方法以单下划线 `_` 开头

### 正确示例
```python
# 好的函数名
def calculate_total(price, quantity):
    pass

def get_user_info(user_id):
    pass

def process_data(input_data):
    pass

class MyClass:
    def public_method(self):
        pass

    def _private_method(self):  # 私有方法
        pass
```

### 不正确示例
```python
# 不好：驼峰命名
def calculateTotal(price, quantity):
    pass

# 不好：不描述性
def do_it():
    pass

# 不好：单字符
def a():
    pass
```

## 变量命名（Variables）

- **小写字母+下划线**：使用小写蛇形命名（snake_case）
- 私有变量以单下划线 `_` 开头
- 避免使用 'l', 'O', 'I' 等易混淆字符

### 正确示例
```python
# 好的变量名
user_name = "John"
total_count = 100
is_valid = True
file_path = "/path/to/file"

# 私有变量
_internal_value = "private"
```

### 不正确示例
```python
# 不好：驼峰命名
userName = "John"
totalCount = 100

# 不好：大写
UserName = "John"

# 不好：使用易混淆字符
l = 1  # 看起来像1或I
O = 0  # 看起来像0
I = 1  # 看起来像l或1
```

## 常量命名（Constants）

- **全大写+下划线**：使用全大写蛇形命名（UPPER_CASE）
- 通常在模块级别定义

### 正确示例
```python
# 好的常量名
MAX_SIZE = 100
DEFAULT_TIMEOUT = 30
API_KEY = "your-api-key"
DATABASE_URL = "postgresql://localhost/db"
ERROR_MESSAGE = "Operation failed"

# 常量通常放在模块顶部
import math

PI = 3.14159265359
MAX_RETRY_COUNT = 3
```

### 不正确示例
```python
# 不好：小写
max_size = 100
default_timeout = 30

# 不好：驼峰命名
MaxSize = 100
DefaultTimeout = 30
```

## 特殊方法命名（Dunder Methods）

- **双下划线开头和结尾**：使用 `__name__` 格式
- 用于Python魔术方法

### 正确示例
```python
class MyClass:
    def __init__(self):
        pass

    def __str__(self):
        return "MyClass instance"

    def __len__(self):
        return 0

    def __repr__(self):
        return "MyClass()"
```

## 参数命名（Function Parameters）

- **小写字母+下划线**：使用小写蛇形命名
- 使用描述性名称
- 'self' 用于实例方法第一个参数
- 'cls' 用于类方法第一个参数

### 正确示例
```python
# 好的参数名
def calculate_area(width, height):
    return width * height

class Circle:
    def __init__(self, radius):
        self.radius = radius

    def calculate_area(self):
        import math
        return math.pi * self.radius ** 2

    @classmethod
    def from_diameter(cls, diameter):
        radius = diameter / 2
        return cls(radius)
```

## 类型提示命名（Type Hints）

- 使用大驼峰命名式作为类型提示或其别名
- 简单类型使用小写

### 正确示例
```python
from typing import List, Dict, Optional

def process_items(items: List[str]) -> Optional[Dict[str, int]]:
    """Process a list of strings and return a dictionary."""
    pass

# 类型别名使用大驼峰命名
Item = Dict[str, int]
UserInfo = Tuple[str, int, bool]
```

## 包命名（Packages）

- **全小写**：使用小写字母
- 尽量简短
- 不鼓励使用下划线

### 正确示例
```
# 好的包名
mypackage/
data/
utils/
```

### 不正确示例
```
# 不好：使用下划线
my_package/
data_processing/
```

## 命名冲突处理

当需要覆盖或保护变量名时：

### 正确示例
```python
# 好的处理方式
def function_with_parameter(data):
    from json import loads  # 局部导入
    return loads(data)

print_ = print  # 覆盖print函数

# 使用三元运算符避免保护变量
data = local_data if local_data else default_value
```

### 不正确示例
```python
# 不好：使用下划线保护名
def function_with_parameter(data):
    from json import loads_  # 不应该这样
    return loads_(data)
```

## 特殊命名约定

### 布尔变量名

使用 `is_`, `has_`, `can_`, `should_` 等前缀：

```python
# 好的布尔变量名
is_valid = True
has_permission = False
can_edit = True
should_retry = False
is_empty = len(items) == 0
```

### 集合变量名

集合变量通常使用复数形式：

```python
# 好的集合变量名
users = []        # list
items = {}        # dict
results = set()   # set
```

### 迭代器变量

使用简短但有意义的名称：

```python
# 好的迭代器变量
for index, item in enumerate(items):
    pass

for user_id, user_data in user_dict.items():
    pass

for row in rows:
    pass
```

## 异常命名

- **异常类名应该以 'Error' 结尾**
- 使用大驼峰命名

### 正确示例
```python
# 好的异常名
class ValueError(Exception):
    pass

class CustomError(Exception):
    pass

class DatabaseConnectionError(Exception):
    pass
```

## 命名规范总结表

| 类型 | 命名规范 | 示例 |
|------|---------|------|
| 模块 | snake_case | `my_module`, `data_processing` |
| 类 | CamelCase | `User`, `HttpRequest` |
| 函数/方法 | snake_case | `calculate_total`, `get_user_info` |
| 变量 | snake_case | `user_name`, `total_count` |
| 常量 | UPPERCASE | `MAX_SIZE`, `DEFAULT_TIMEOUT` |
| 私有成员 | _snake_case | `_private_method`, `_internal_var` |
| 特殊方法 | __dunder__ | `__init__`, `__str__` |
| 异常类 | CamelCase + Error | `ValueError`, `CustomError` |

## 最佳实践

1. **一致性优先**：在项目中保持一致的命名风格
2. **可读性**：名称应该让人一眼就能理解其用途
3. **避免缩写**：除非是广为人知的缩写（如id, url, api）
4. **描述性名称**：使用动词+名词的形式表示函数
5. **避免使用魔法数字**：使用有名称的常量替代
6. **遵循项目约定**：在现有项目中遵循既定约定

## 常见错误

❌ `def Calculate(val):` - 函数名应该小写
❌ `class user:` - 类名应该大驼峰
❌ `constValue = 10` - 常量应该全大写
❌ `is_valid_check = True` - `is_` 已经是布尔，不需要`_check`
❌ `x = 1` - 使用有意义的变量名
