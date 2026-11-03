# Python最佳实践

遵循这些最佳实践，写出更Pythonic、更高效的代码。

## 代码风格

### PEP8遵循

严格遵循PEP8规范，使用工具自动检查：

```bash
# 使用flake8检查
flake8 my_script.py

# 使用black自动格式化
black my_script.py
```

### 避免重复代码（DRY原则）

不要复制粘贴代码，提取公共逻辑。

```python
# 不好：重复代码
def process_user_a(user):
    if user.age >= 18:
        user.can_vote = True
        user.can_drive = True
    else:
        user.can_vote = False
        user.can_drive = False

def process_user_b(user):
    if user.age >= 18:
        user.can_vote = True
        user.can_drive = True
    else:
        user.can_vote = False
        user.can_drive = False

# 好：提取公共逻辑
def check_adult_status(user):
    """检查用户成年状态。"""
    is_adult = user.age >= 18
    user.can_vote = is_adult
    user.can_drive = is_adult

def process_user_a(user):
    check_adult_status(user)

def process_user_b(user):
    check_adult_status(user)
```

## Pythonic写法

### 使用列表推导式

```python
# 不好：使用循环
result = []
for i in range(10):
    result.append(i * 2)

# 好：使用列表推导式
result = [i * 2 for i in range(10)]
```

### 使用enumerate遍历

```python
# 不好：单独维护索引
index = 0
for item in items:
    print(index, item)
    index += 1

# 好：使用enumerate
for index, item in enumerate(items):
    print(index, item)
```

### 使用zip并行遍历

```python
# 不好：使用索引
for i in range(len(names)):
    print(names[i], ages[i])

# 好：使用zip
for name, age in zip(names, ages):
    print(name, age)
```

### 使用字典.get()方法

```python
# 不好：先检查键是否存在
if "age" in user_dict:
    age = user_dict["age"]
else:
    age = 0

# 好：使用get方法
age = user_dict.get("age", 0)
```

### 使用with语句管理资源

```python
# 不好：手动管理文件
f = open("file.txt", "r")
try:
    content = f.read()
finally:
    f.close()

# 好：使用with语句
with open("file.txt", "r") as f:
    content = f.read()
```

### 使用上下文管理器

```python
# 创建上下文管理器
class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        print(f"耗时: {self.end - self.start:.2f}秒")

# 使用
with Timer():
    # 执行一些操作
    time.sleep(1)
```

### 使用装饰器

```python
# 不好：重复代码
def function_a():
    start = time.time()
    # 逻辑
    print(f"耗时: {time.time() - start}")

def function_b():
    start = time.time()
    # 逻辑
    print(f"耗时: {time.time() - start}")

# 好：使用装饰器
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.2f}秒")
        return result
    return wrapper

@timer
def function_a():
    pass

@timer
def function_b():
    pass
```

### 使用生成器

```python
# 不好：使用列表（内存消耗大）
def get_numbers(n):
    result = []
    for i in range(n):
        result.append(i ** 2)
    return result

# 好：使用生成器（内存高效）
def get_numbers(n):
    for i in range(n):
        yield i ** 2
```

### 使用数据类（dataclass）

```python
# 不好：手动写类
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

# 好：使用dataclass
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
```

## 异常处理

### 捕获具体异常

```python
# 不好：捕获所有异常
try:
    result = 10 / 0
except Exception:
    print("出错")

# 好：捕获具体异常
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零")
```

### 使用else和finally

```python
# 好：完整的异常处理结构
try:
    file = open("data.txt", "r")
    data = file.read()
except FileNotFoundError:
    print("文件不存在")
except IOError:
    print("读取文件出错")
else:
    # 没有异常时执行
    print("文件读取成功")
    process(data)
finally:
    # 无论是否有异常都执行
    if 'file' in locals():
        file.close()
```

### 不使用异常进行控制流

```python
# 不好：使用异常控制流程
try:
    value = get_value()
except ValueError:
    value = default_value

# 好：预先检查
if value := get_value_if_exists():
    # 使用value
else:
    value = default_value
```

### 自定义异常

```python
# 好：定义有意义的异常类
class InvalidUserInputError(Exception):
    """用户输入无效。"""
    pass

class DatabaseConnectionError(Exception):
    """数据库连接失败。"""
    pass

def process_input(user_input):
    if not isinstance(user_input, str):
        raise InvalidUserInputError("输入必须是字符串")
```

## 数据结构选择

### 使用集合进行成员检查

```python
# 不好：用于成员检查的列表
items = [1, 2, 3, 4, 5]
if 3 in items:
    print("找到")

# 好：使用集合
items = {1, 2, 3, 4, 5}
if 3 in items:
    print("找到")
```

### 使用Counter进行计数

```python
from collections import Counter

# 好：使用Counter
words = ['apple', 'banana', 'apple', 'orange', 'banana', 'apple']
word_counts = Counter(words)
print(word_counts['apple'])  # 3
```

### 使用defaultdict避免键错误

```python
from collections import defaultdict

# 不好：需要检查键是否存在
result = {}
for item in items:
    if item not in result:
        result[item] = []
    result[item].append(value)

# 好：使用defaultdict
result = defaultdict(list)
for item in items:
    result[item].append(value)
```

## 字符串处理

### 使用f-string格式化

```python
name = "Alice"
age = 25

# 不好：使用%格式化
print("Name: %s, Age: %d" % (name, age))

# 不好：使用.format()
print("Name: {}, Age: {}".format(name, age))

# 好：使用f-string
print(f"Name: {name}, Age: {age}")
```

### 使用join连接字符串

```python
# 不好：使用+连接
result = ""
for item in items:
    result += item + ","

# 好：使用join
result = ",".join(items)
```

### 使用strip处理空白字符

```python
# 好：使用strip去除首尾空白
name = input("姓名: ").strip()
if not name:
    print("姓名不能为空")
```

## 性能优化

### 避免在循环中重复计算

```python
# 不好：循环中重复计算
for i in range(1000):
    result = compute_expensive_value(i)

# 好：预先计算或缓存
value = compute_expensive_value()
for i in range(1000):
    result = value * i
```

### 使用局部变量加速

```python
# 好：将频繁访问的函数赋给局部变量
import math

sin = math.sin
cos = math.cos

for i in range(1000000):
    result = sin(i) + cos(i)
```

### 使用生成器减少内存

```python
# 好的处理大文件：逐行读取
def process_large_file(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield process_line(line)
```

### 使用适当的数据结构

根据使用场景选择合适的数据结构：

- 列表（List）：有序、可重复的数据
- 元组（Tuple）：不可变的序列
- 集合（Set）：去重、快速成员检查
- 字典（Dict）：键值对映射

## 代码组织

### 函数应该专注单一职责

```python
# 不好：函数做太多事情
def process_user_order(user_id, order_data):
    # 验证用户
    user = get_user(user_id)
    if not user:
        return False

    # 验证订单
    if not validate_order(order_data):
        return False

    # 计算价格
    total = calculate_total(order_data)

    # 保存订单
    order_id = save_order(user_id, order_data, total)

    # 发送邮件
    send_email(user.email, f"订单{order_id}已创建")

    return order_id

# 好：拆分成小函数
def process_user_order(user_id, order_data):
    user = validate_user(user_id)
    if not user:
        return False

    if not validate_order(order_data):
        return False

    total = calculate_total(order_data)
    order_id = save_order(user_id, order_data, total)
    send_confirmation(user, order_id)

    return order_id
```

### 使用参数默认值

```python
# 好：使用默认参数
def connect_to_database(
    host: str = "localhost",
    port: int = 5432,
    timeout: int = 30
) -> bool:
    """连接到数据库。"""
    pass
```

### 使用关键字参数

```python
# 好：对于有多个参数的函数，使用关键字参数
function_with_many_params(
    first_arg,
    second_arg,
    third_arg="default",
    fourth_arg=None
)
```

## 安全实践

### 不使用pickle从不可信源加载

```python
# 危险：不要这样做
import pickle

data = pickle.loads(untrusted_data)

# 安全：使用JSON或更安全的序列化格式
import json
data = json.loads(untrusted_data)
```

### 避免eval和exec

```python
# 危险：执行任意代码
user_input = "os.system('rm -rf /')"
eval(user_input)

# 安全：使用替代方案
from ast import literal_eval
data = literal_eval(user_input)
```

### 敏感信息不硬编码

```python
# 不好：硬编码敏感信息
api_key = "sk-1234567890abcdef"
database_password = "secret123"

# 好：使用环境变量
import os

api_key = os.getenv("API_KEY")
database_password = os.getenv("DB_PASSWORD")
```

## 测试实践

### 编写单元测试

```python
import pytest

def test_calculate_total():
    """测试总价计算。"""
    items = [{'price': 10}, {'price': 20}]
    assert calculate_total(items) == 30
```

### 使用mock隔离外部依赖

```python
from unittest.mock import patch, MagicMock

def test_api_call():
    """测试API调用。"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'status': 'ok'}
        result = make_api_call()
        assert result['status'] == 'ok'
```

## 代码审查清单

提交代码前检查：

- [ ] 代码遵循PEP8规范
- [ ] 有适当的文档字符串
- [ ] 有必要的类型提示
- [ ] 没有重复代码
- [ ] 异常处理适当
- [ ] 资源使用with语句管理
- [ ] 敏感信息不硬编码
- [ ] 命名清晰有意义
- [ ] 函数职责单一
- [ ] 有测试覆盖

## 性能提示

1. **考虑使用缓存**：对于频繁调用且结果不变的函数
2. **避免不必要的类型转换**：提前确定数据类型
3. **使用向量化操作**：数值计算考虑numpy
4. **合理使用多线程/多进程**：I/O密集型用多线程，CPU密集型用多进程
5. **优化算法复杂度**：优先考虑时间复杂度而非代码简洁性

## 调试技巧

1. **使用print调试**：快速简单
2. **使用pdb调试器**：交互式调试
3. **使用logging模块**：生产环境日志
4. **使用assert**：开发时验证假设
5. **使用type hints**：IDE静态检查

## 工具和库

推荐使用这些工具提高代码质量：

- **格式化**：black, autopep8
- **检查**：flake8, pylint, mypy
- **测试**：pytest, unittest
- **文档**：sphinx, mkdocs
- **性能**：cProfile, memory_profiler
- **安全**：bandit, safety

```bash
# 常用命令组合
black my_module.py
flake8 my_module.py
mypy my_module.py
pytest tests/
```

## 持续改进

1. **定期重构**：保持代码清晰
2. **关注代码度量**：圈复杂度、重复率
3. **学习新特性**：掌握最新的Python特性
4. **参与社区**：学习他人的最佳实践
5. **编写文档**：帮助团队和未来的自己
