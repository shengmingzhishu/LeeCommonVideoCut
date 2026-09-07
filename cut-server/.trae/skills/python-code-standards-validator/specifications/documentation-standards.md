# Python文档字符串和注释规范

良好的文档使代码自解释，提高可维护性。

## 文档字符串（Docstrings）

### 模块文档字符串

每个模块都应该有文档字符串，描述模块的用途。

```python
"""
用户管理模块。

提供用户增删改查的基础功能，包括：
- 用户创建和验证
- 用户信息更新
- 用户查询和搜索
"""

import hashlib
from typing import Dict, List, Optional
```

### 类文档字符串

描述类的用途、主要功能和用法示例。

```python
class User:
    """
    用户类。

    表示系统中的用户，包含用户的基本信息和操作方法。

    Attributes:
        user_id: 用户唯一标识符
        username: 用户名
        email: 电子邮箱
        is_active: 是否激活

    Example:
        >>> user = User(user_id="123", username="john")
        >>> user.email = "john@example.com"
        >>> print(user.username)
        'john'
    """

    def __init__(self, user_id: str, username: str):
        """初始化用户对象。"""
        self.user_id = user_id
        self.username = username
```

### 函数文档字符串

描述函数的功能、参数、返回值和可能的异常。

```python
def authenticate_user(username: str, password: str) -> bool:
    """
    验证用户凭据。

    比对用户名和密码与存储的凭据，验证是否匹配。

    Args:
        username: 用户名
        password: 密码

    Returns:
        bool: 验证成功返回True，失败返回False

    Raises:
        ValueError: 当用户名或密码为空时
        Exception: 当数据库连接失败时

    Example:
        >>> authenticate_user("admin", "secure123")
        True
        >>> authenticate_user("admin", "wrong")
        False
    """
    if not username or not password:
        raise ValueError("用户名和密码不能为空")

    # 验证逻辑
    return True
```

### 文档字符串格式

使用Google风格或NumPy风格文档字符串（推荐Google风格）。

#### Google风格

```python
def calculate_discount(price: float, discount_rate: float) -> float:
    """
    计算折扣价格。

    Args:
        price (float): 原价
        discount_rate (float): 折扣率（0-1之间的小数）

    Returns:
        float: 折扣后的价格

    Raises:
        ValueError: 当价格为负数或discount_rate超出范围时

    Examples:
        >>> calculate_discount(100, 0.2)
        80.0
    """
    if price < 0:
        raise ValueError("价格不能为负数")

    if not 0 <= discount_rate <= 1:
        raise ValueError("折扣率必须在0-1之间")

    return price * (1 - discount_rate)
```

#### NumPy风格

```python
def calculate_discount(price: float, discount_rate: float) -> float:
    """
    计算折扣价格。

    Parameters
    ----------
    price : float
        原价
    discount_rate : float
        折扣率（0-1之间的小数）

    Returns
    -------
    float
        折扣后的价格

    Raises
    ------
    ValueError
        当价格为负数或discount_rate超出范围时

    Examples
    --------
    >>> calculate_discount(100, 0.2)
    80.0
    """
    if price < 0:
        raise ValueError("价格不能为负数")

    if not 0 <= discount_rate <= 1:
        raise ValueError("折扣率必须在0-1之间")

    return price * (1 - discount_rate)
```

### 文档字符串内容

对于公共的类和函数，文档字符串应该包含：

1. **总结**：一句话描述功能
2. **详细描述**：详细说明（可选）
3. **参数说明**（Args/Parameters）：每个参数的类型、含义、约束
4. **返回值**（Returns）：返回值的类型和含义
5. **异常**（Raises）：可能抛出的异常及条件
6. **示例**（Examples/Note）：使用示例或重要说明

```python
def send_email(
    to_address: str,
    subject: str,
    body: str,
    attachments: Optional[List[str]] = None
) -> bool:
    """
    发送电子邮件。

    向指定地址发送邮件，支持附件。

    Args:
        to_address (str): 收件人邮箱地址
        subject (str): 邮件主题
        body (str): 邮件正文内容
        attachments (Optional[List[str]]): 附件路径列表，默认为None

    Returns:
        bool: 发送成功返回True，失败返回False

    Raises:
        ValueError: 当邮箱地址格式无效时
        FileNotFoundError: 当附件文件不存在时

    Examples:
        >>> send_email(
        ...     to_address="user@example.com",
        ...     subject="测试邮件",
        ...     body="这是一封测试邮件"
        ... )
        True
    """
    if "@" not in to_address:
        raise ValueError("邮箱地址格式无效")

    # 发送逻辑
    return True
```

## 注释（Comments）

### 行内注释

注释应该解释"为什么"而不是"是什么"。

```python
# 好的注释：解释"为什么"
# 使用幂运算提高性能而不是循环
result = number ** 10  # 相比 for i in range(10): result *= number

# 不好的注释：重复代码
result = number ** 10  # 计算number的10次方
```

### 块注释

用于解释代码块的功能。

```python
# 读取配置文件并解析JSON
with open("config.json", "r") as f:
    config = json.load(f)

    # 验证必需的配置项
    required_keys = ["host", "port", "username"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"缺少必需的配置项: {key}")
```

### TODO和FIXME标记

使用TODO标记待办事项，FIXME标记需要修复的代码。

```python
# TODO: 实现缓存机制以提高性能
def get_data():
    pass

# FIXME: 修复偶发的超时问题
def connect_database():
    pass
```

### 注释位置

注释应该位于被注释的代码上方，而不是行内。

```python
# 好的：注释在上方
# 计算折扣金额
discount_amount = total_price * discount_rate

# 不好的：行内注释
discount_amount = total_price * discount_rate  # 计算折扣金额
```

### 不需要的注释

不要为显而易见的代码添加注释。

```python
# 不需要：明显的代码不需要注释
count = 0  # 初始化计数器 = 0

# 不需要：代码本身已经自解释
# 增加计数
count += 1
```

## 类型提示（Type Hints）

使用类型提示提高代码可读性和IDE支持。

### 基本类型

```python
from typing import List, Dict, Optional, Tuple


def process_data(
    items: List[int],
    config: Dict[str, int],
    threshold: Optional[int] = None
) -> Tuple[int, bool]:
    """
    处理数据。

    Args:
        items: 整数列表
        config: 配置字典
        threshold: 可选的阈值

    Returns:
        处理后的结果和状态元组
    """
    result = sum(items)
    is_valid = result > (threshold or 0)
    return result, is_valid
```

### 类型别名

对于复杂的类型，使用类型别名提高可读性。

```python
from typing import Dict, List

# 类型别名
UserInfo = Dict[str, str]
OrderList = List[Dict[str, int]]


def create_order(user_info: UserInfo, items: OrderList) -> dict:
    """创建订单。"""
    pass
```

### 自定义类型

对于自定义对象，使用类名或字符串。

```python
class User:
    pass


def greet_user(user: User) -> str:
    """问候用户。"""
    return f"Hello, {user}"
```

## README文档

项目根目录应该有README.md，包含：

1. 项目简介
2. 安装和配置说明
3. 使用示例
4. 功能特性
5. API文档链接
6. 贡献指南

```markdown
# 项目名称

简短的项目描述。

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```python
from mypackage import MyFunction

result = MyFunction("input")
print(result)
```

## 功能

- 功能1
- 功能2
- 功能3

## 配置

编辑 `config.json` 文件进行配置。

## 文档

详细文档请参考：[文档链接](doc/index.md)
```

## CHANGELOG记录

维护CHANGELOG.md记录版本变更。

```markdown
# 更新日志

## [1.2.0] - 2024-01-15

### 新增
- 添加了用户认证功能
- 支持批量导入数据

### 改进
- 优化了性能
- 改进了错误处理

### 修复
- 修复了登录超时的问题
- 修复了数据格式转换错误

## [1.1.0] - 2024-01-01

### 新增
- 初始版本发布
```

## 文档最佳实践

### 1. 及时更新文档

代码变更时，同步更新文档。

### 2. 保持文档简洁

不要过度注释，保持代码自解释。

### 3. 使用一致的格式

在整个项目中使用相同的文档风格。

### 4. 文档代码示例

提供可运行的代码示例，帮助用户理解。

### 5. 记录设计决策

对于非显而易见的设计决策，添加注释说明原因。

```python
# 使用Python内置的hash()而不是自定义hash函数，
# 因为内置函数在大数据量时性能更好
def compute_id(name: str) -> int:
    return hash(name)
```

### 6. 文档API接口

公共API需要详细的文档。

```python
def create_user(user_data: dict) -> str:
    """
    创建新用户。

    创建用户并分配唯一的用户ID。

    Args:
        user_data (dict): 用户数据，必须包含以下字段：
            - username (str): 用户名，2-20个字符，只能包含字母和数字
            - email (str): 邮箱地址，必须是有效的邮箱格式
            - password (str): 密码，至少8个字符，包含字母和数字

    Returns:
        str: 新创建用户的唯一ID

    Raises:
        ValueError: 当用户数据不符合要求时
        ConflictError: 当用户名或邮箱已存在时

    Example:
        >>> user_id = create_user({
        ...     "username": "john_doe",
        ...     "email": "john@example.com",
        ...     "password": "securePass123"
        ... })
        >>> print(user_id)
        'abc123def456'
    """
```

## 文档检查清单

- [ ] 模块有文档字符串
- [ ] 所有公开类有文档字符串
- [ ] 所有公开函数有文档字符串
- [ ] 文档字符串包含参数、返回值、异常说明
- [ ] 使用类型提示
- [ ] 复杂逻辑有注释解释
- [ ] 项目有README.md
- [ ] 使用一致的文档风格
- [ ] 文档与代码保持同步
- [ ] 提供使用示例

## 文档工具

### 生成文档

使用工具自动生成文档：

- Sphinx：功能强大的文档生成工具
- MkDocs：简洁的Markdown文档生成器
- pydoc：Python内置文档生成工具

### 检查文档

使用工具检查文档完整性：

- pydocstyle：检查文档字符串风格
- pylint：代码质量检查，包含文档检查
- mypy：静态类型检查

```bash
# 检查文档字符串风格
pydocstyle my_module.py

# 生成文档
sphinx-quickstart
pydoc -w my_package
```
