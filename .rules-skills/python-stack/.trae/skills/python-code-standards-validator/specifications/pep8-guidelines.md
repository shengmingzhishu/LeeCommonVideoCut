# PEP8 Python代码风格指南

遵循 [PEP8](https://peps8.org/) 规范，确保代码风格一致性和可读性。

## 缩进

- **使用4个空格进行缩进**，不要使用Tab
- 对齐的多行代码应该使用垂直对齐的括号
- 续行应该对齐括号、括号中的元素或使用悬挂缩进

### 正确示例
```python
# 好的缩进
def long_function_name(
        var_one, var_two, var_three,
        var_four):
    print(var_one)

# 好的悬挂缩进
def long_function_name(
        var_one, var_two, var_three,
        var_four):
    print(var_one)
```

### 不正确示例
```python
# 不好：使用Tab
def long_function_name():
	var_one = 1
	var_two = 2
    return var_one + var_two
```

## 行长度

- **最大行长度限制为79个字符**
- 文档字符串/注释行长度限制为72个字符
- 对于长行，使用圆括号、反斜杠或隐式行连接

### 正确示例
```python
# 好的续行
def function(arg1, arg2, arg3, arg4,
             arg5, arg6):
    pass

# 好的隐式行连接
long_text = ('This is a very long string that should be '
             'split across multiple lines for readability')
```

### 不正确示例
```python
# 不好：超过79个字符
def very_long_function_name_with_many_parameters(var_one, var_two, var_three, var_four, var_five, var_six):
    pass
```

## 空行

- **顶层函数/类之间使用两个空行**分隔
- **类内部方法之间使用一个空行**分隔
- 相关功能组之间可以额外使用空行分隔
- 函数内部不要有过多的空行

### 正确示例
```python
# 好的空行使用
def function_one():
    """First function."""
    pass


def function_two():
    """Second function."""
    pass


class MyClass:
    """Example class."""

    def method_one(self):
        """First method."""
        pass

    def method_two(self):
        """Second method."""
        pass
```

## 导入

- **导入应该放在文件顶部，在模块文档字符串之后**
- 标准库导入 → 第三方库导入 → 本地应用/库导入
- 每组导入之间用一个空行分隔
- 每次导入一行，避免使用通配符导入

### 正确示例
```python
# 好的导入顺序和格式
import os
import sys

import numpy as np
from requests import get

from myproject import utils
from myproject.constants import MAX_SIZE
```

### 不正确示例
```python
# 不好：多行导入
import os, sys, math

# 不好：使用通配符
from module import *
```

## 空格使用

### 运算符周围空格

二元运算符周围使用空格：

```python
# 好的：运算符周围使用空格
x = 1 + 2
y = x * 3

# 例外：优先级相关时可以省略
z = x*2 - 1
```

### 逗号、冒号、分号

不在逗号、冒号、分号前使用空格：

```python
# 正确
function(arg1, arg2)
x = [1, 2, 3]
for i in range(10):
    pass

# 不正确
function(arg1 , arg2)
x = [1 , 2 , 3]
for i in range(10) :
    pass
```

### 括号内空格

不要在括号内添加空格：

```python
# 正确
function(arg1, arg2)
list = [1, 2, 3]
dict = {'key': 'value'}

# 不正确
function( arg1, arg2 )
list = [ 1, 2, 3 ]
dict = { 'key': 'value' }
```

## 命名风格一致性

代码风格应该一致，全部使用snake_case或camelCase，不要混用。

### 正确示例
```python
# 好的：一致的命名风格
total_score = calculate_score(user_id, test_id)
average_result = compute_average(scores)

# 或一致使用驼峰命名
totalScore = calculateScore(userId, testId)
averageResult = computeAverage(scores)
```

### 不正确示例
```python
# 不好：混用命名风格
total_score = calculateScore(user_id, testId)  # 混用
averageResult = compute_average(scores)         # 混用
```

## 注释风格

### 行内注释

```python
# 正确：行内注释
x = 1  # 设置初始值
y = make_list()  # 创建列表

# 不正确：没有适当间隔
x = 1#设置初始值
y = make_list()#创建列表
```

### 块注释

```python
# 正确的块注释
# 计算文件的哈希值
# 使用MD5算法确保数据完整性
hash_value = compute_hash(file_path)
```

## 字符串引号

- 使用单引号 `''` 或双引号 `""` 皆可，但要保持一致
- 包含引号的字符串使用与字符串不同的引号风格

### 正确示例
```python
# 好的：一致的引号使用
message = 'Hello, World!'
greeting = "Welcome to Python!"

# 好的：避免转义
quote = "He said, 'Hello!'"
```

## 尾随空格

- 不应该在行尾留有尾随空格
- 大多数编辑器可以自动去除尾随空格

## 不要对局部变量名"保护"

如果需要"保护"变量名，请使用其他命名方式，而不是添加下划线后缀。

### 正确示例
```python
# 好的：使用括号或内联形式
def send_data(data):
    import json  # 局部导入
    return json.dumps(data)
```

### 不正确示例
```python
# 不好：使用带下划线的保护名
def send_data(data):
    import json_
    return json_.dumps(data)
```

## 总结

遵循PEP8规范的最佳实践：

1. **缩进统一**：使用4个空格，不使用Tab
2. **控制行长度**：不超过79字符，文档/注释不超过72字符
3. **适当空行**：顶层2行，类内1行
4. **导入规范**：标准库 → 第三方 → 本地，每行一个
5. **空格使用**：运算符周围加空格，括号、逗号内不加
6. **命名一致**：保持命名风格的一致性
7. **注释清晰**：注释与代码有适当间隔
8. **引号一致**：选择一种引号风格并保持一致
9. **去除尾随空格**：不要在行尾留空格
