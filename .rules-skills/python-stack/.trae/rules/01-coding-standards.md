---
alwaysApply: true
---
# 编码规范（通用）

> 本规范适用于所有 Python 后端项目，可直接复制到新项目使用。
> 项目特定的命名约定请在 `project/01-project-specific.md` 中补充。

## 1. 命名规范

### 1.1 通用原则

- 使用描述性名称，名称应清楚表达其用途
- 避免使用单字符变量（循环计数器 i, j, k 除外）
- 不使用 Python 关键字
- 名称要简洁而完整，在清晰的前提下尽可能简短

### 1.2 命名约定速查表

| 类型 | 命名规范 | 示例 |
|------|---------|------|
| 模块/文件 | snake_case | `data_parser.py`, `user_service.py` |
| 包名 | snake_case | `myapp`, `controllers` |
| 类 | PascalCase (大驼峰) | `UserService`, `DataProcessor` |
| 函数/方法 | snake_case | `parse_data()`, `get_user_info()` |
| 变量 | snake_case | `user_name`, `total_count` |
| 常量 | UPPER_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| 私有成员 | _snake_case | `_internal_method()`, `_cache_data` |
| 特殊方法 | __dunder__ | `__init__`, `__str__` |
| 异常类 | PascalCase + Error | `ParseError`, `ValidationError` |
| 布尔变量 | is_/has_/can_/should_ 前缀 | `is_valid`, `has_permission` |
| 集合变量 | 复数形式 | `users`, `results`, `items` |

## 2. 代码格式

### 2.1 缩进与行长度

- 使用 4 个空格缩进，不使用 Tab
- 每行最多 120 个字符
- 超过时合理换行，优先在逗号、运算符后换行

### 2.2 空行

- 顶层函数和类定义之间用 2 个空行
- 类内方法之间用 1 个空行
- 逻辑相关的代码块之间用 1 个空行分隔

### 2.3 导入规范

**导入顺序（每组之间用 1 个空行分隔）：**
1. 标准库导入
2. 第三方库导入
3. 本地应用/库导入

**规则：**
- 禁止使用通配符导入（`from module import *`）
- 同一组内按字母顺序排列
- 避免循环导入

**示例：**
```python
# 1. 标准库
import os
import sys
from pathlib import Path
from typing import List, Optional

# 2. 第三方库
from fastapi import FastAPI
from sqlalchemy import create_engine

# 3. 本地导入
from myapp.utils.env import SERVER_PORT
from myapp.utils.logs import LOGGER
```

## 3. 文档字符串

### 3.1 模块文档字符串

每个模块文件开头必须有文档字符串，简要说明模块用途。

```python
"""
数据解析模块。

负责各类格式的数据解析、清洗和结构化转换。
支持 JSON、XML、CSV 等多种输入格式。
"""
```

### 3.2 类文档字符串

```python
class DataProcessor:
    """
    数据处理器。

    封装数据的读取、转换和输出流程。
    支持批量处理和流式处理两种模式。

    Attributes:
        config: 处理器配置字典
        pipeline: 处理管道列表
    """
```

### 3.3 函数/方法文档字符串

所有方法级别和重要函数必须有完整的文档字符串，使用 Google 风格，包含 Args、Returns、Raises。

```python
def process_data(self, data: dict, validate: bool = True) -> dict:
    """
    处理输入数据。

    Args:
        data: 输入数据字典
        validate: 是否进行数据校验，默认 True

    Returns:
        处理后的数据字典

    Raises:
        ValidationError: 数据校验失败时
    """
```

## 4. 类型提示

- 所有公开函数和方法必须有类型提示
- 复杂类型使用 `typing` 模块
- 优先使用具体类型而非 `Any`

```python
from typing import List, Dict, Optional, Tuple

def process_items(items: List[str]) -> Dict[str, int]:
    pass

def find_item(name: str) -> Optional[Item]:
    pass
```

## 5. 注释规范

### 5.1 注释原则

- 注释应该解释"为什么"，而不是"做什么"
- 避免注释与代码重复
- TODO/FIXME 注释必须包含负责人和日期

```python
# TODO: 优化大文件内存占用 - username - 2026-08-07
# FIXME: 边界条件处理不正确 - ticket #123
```

### 5.2 方法级别注释（强制）

- **所有 public 方法必须有文档字符串**，说明其用途、参数、返回值和可能的异常
- **重要的 private 方法也应有注释**，说明其内部逻辑和设计意图
- 方法内复杂逻辑段应有行内注释，解释设计原因

```python
def _build_eval_context(self, suite_id: str, case_ids: list) -> EvalContext:
    """
    构建评测上下文。

    内部方法，从数据库加载评测套件和用例配置，
    合并运行时参数生成不可变的上下文对象。

    Args:
        suite_id: 评测套件 ID
        case_ids: 指定执行的用例 ID 列表，为空则加载全部

    Returns:
        评测上下文对象

    Raises:
        EvalSuiteError: 套件不存在或配置无效时
    """
    # 只加载活跃状态的用例，避免历史废弃用例干扰结果
    active_cases = self._filter_active(case_ids)
    ...
```

### 5.3 配置文件注释（强制）

- **每个配置项必须有注释**，说明用途、取值范围、默认值含义
- **环境变量配置项**需注明对应的环境变量名和推荐值
- **分组配置**需有分组说明注释

```python
# 评测任务并发控制
MAX_CONCURRENT_TASKS = int(os.getenv('MAX_CONCURRENT_TASKS', '10'))  # 最大并发评测任务数，默认 10
TASK_TIMEOUT = int(os.getenv('TASK_TIMEOUT', '3600'))  # 单任务超时秒数，默认 3600

# 数据库连接池配置
DATABASE_CONFIG = {
    'engine_setting': {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),  # 连接池大小，默认 10
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),  # 连接池溢出上限，默认 20
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '25200')),  # 连接回收周期(秒)，默认 7 小时，避免 MySQL 8 小时断连
    },
}
```

## 6. 禁止事项

- 禁止使用魔数，使用常量替代
- 禁止硬编码配置，使用环境变量或配置文件
- 禁止在业务代码中使用 `print()`，使用日志系统
- 禁止捕获所有异常后静默吞掉（`except: pass`）
- 禁止修改已有公共接口的签名（保持向后兼容）
- 禁止提交无注释的配置项
- 禁止方法缺少文档字符串（private 工具方法除外，但也建议添加）

## 7. 文件编码规范（强制）

> **铁律**：项目内**所有文本文件必须使用 UTF-8 无 BOM（UTF-8 without BOM）** 编码保存。
>
> 历史教训：项目早期 `plan/` 目录用 Windows 记事本编辑，导致 `.md` 文件被存为 GBK 编码 + UTF-8 BOM 混合，
> 后续用 UTF-8 读取时全部变成乱码且无法恢复。本节强制统一编码。

### 7.1 适用范围

| 文件类型 | 编码 | 行尾 | 缩进 |
|----------|------|------|------|
| `.py` `.md` `.txt` `.json` `.yml` `.yaml` `.toml` `.html` `.css` `.js` `.ts` `.sh` | **UTF-8 无 BOM** | LF | 4 空格（Python） / 2 空格（其他） |
| 二进制文件（`.png` `.jpg` `.pdf` `.xlsx` `.pyc` 等） | 不适用 | 不适用 | 不适用 |

### 7.2 防复发基础设施

项目根目录已配置以下文件：

- **`.editorconfig`**：所有主流编辑器（VSCode / PyCharm / IntelliJ / Sublime）自动应用，新文件保存时强制 UTF-8 无 BOM + LF
- **`.gitattributes`**：git 提交/检出时自动规范化编码与行尾（启用 git 后生效）

### 7.3 编码检测脚本

新增/修改文件后必须通过编码检查：

```bash
# 检查项目内所有 .md / .py 文件是否为 UTF-8 无 BOM
python -c "
import os
ok = True
for root, _, files in os.walk('.'):
    if '.git' in root or '.trae' in root or '__pycache__' in root: continue
    for f in files:
        if not f.endswith(('.md', '.py', '.json', '.yml', '.yaml', '.toml', '.txt')): continue
        p = os.path.join(root, f)
        with open(p, 'rb') as fp:
            head = fp.read(3)
        if head.startswith(b'\xef\xbb\xbf'):
            print(f'FAIL: {p} 含 UTF-8 BOM')
            ok = False
print('OK: 所有文件无 BOM' if ok else 'FAIL: 有文件含 BOM')
"
```

### 7.4 禁止事项（编码相关）

- 禁止用 Windows 记事本编辑项目文件（默认 GBK + BOM）
- 禁止用 Sublime Text 旧版（跟随系统编码）保存
- 禁止提交 BOM 文件到 git（即便编码本身是 UTF-8）
- 禁止用 Python `open()` 不指定 encoding（依赖平台默认，Windows 是 GBK）
- 禁止假定"读取不报错 = 编码正确"（GBK 字节被错误 UTF-8 解码后的字符全在 Latin-1 范围内，不会触发 `UnicodeDecodeError`）

### 7.5 Python 读写文件标准模板

```python
# 读取文本文件（强制 UTF-8）
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 写入文本文件（强制 UTF-8 无 BOM）
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

# 读取 JSON（强制 UTF-8）
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
```

### 7.6 编码诊断速查表

| 现象 | 原因 | 修复 |
|------|------|------|
| 文件头 3 字节是 `0xEF 0xBB 0xBF` | UTF-8 BOM | 用编辑器重新保存为 UTF-8 无 BOM |
| PowerShell 显示"锘�# xxx" | UTF-8 BOM 被 GBK 解码 | 同上 |
| 中文显示成"濞寸姾锟"等乱码 | GBK 字节被 UTF-8 错误解码 | 重新获取原始文件并转 UTF-8 |
| UTF-8 严格解码不报错但没中文 | 实际是 GBK 编码 | **必须先用 GBK 严格解码**：GBK 比 UTF-8 严格，遇到非 GBK 字节会报错；UTF-8 严格解码"成功"≠"是 UTF-8" |
