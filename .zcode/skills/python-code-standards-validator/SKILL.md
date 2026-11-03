---
name: python-code-standards-validator
description: "检查 Python 项目代码是否遵循开发规范（PEP8、命名规范、文档规范等），生成详细的检查报告和改进建议。在 Python 代码检查、规范验证、提交前质量把关时使用。"
summary: "帮助用户检查Python项目代码是否遵循Python开发规范（PEP8、命名规范、文档规范等），生成详细的检查报告和改进建议。"
version: "2.1.0"
author: "WorkBuddy Agent"
agent_created: true
---

# Python代码规范检查技能

帮助用户验证Python代码是否符合Python开发规范，并提供改进建议。

## 何时使用此技能

当用户说以下内容时，使用此技能：
- "检查代码规范"
- "验证Python代码"
- "扫描项目代码规范"
- "代码规范检查"
- "检查代码是否符合PEP8"
- "代码质量检查"
- "审查代码"

## 执行流程

### 第一步：跨平台扫描Python文件

本技能提供跨平台支持，在 Windows、Linux、macOS 上直接使用系统命令执行。

#### Windows (PowerShell)

**查找所有 Python 文件：**
```powershell
Get-ChildItem -Recurse -Filter *.py | Where-Object {
    $_.FullName -notmatch '__pycache__|venv|\.venv|node_modules|\.git|dist|build|\.tox'
} | Select-Object -ExpandProperty FullName
```

**统计文件数量：**
```powershell
(Get-ChildItem -Recurse -Filter *.py | Where-Object {
    $_.FullName -notmatch '__pycache__|venv|\.venv|node_modules|\.git|dist|build|\.tox'
}).Count
```

**快速检查行长度：**
```powershell
Get-ChildItem -Recurse -Filter *.py | Where-Object {
    $_.FullName -notmatch '__pycache__|venv|\.venv|node_modules'
} | ForEach-Object {
    Select-String -Path $_.FullName -Pattern "^.{80,}$"
}
```

#### Linux / macOS / Git Bash

**查找所有 Python 文件：**
```bash
find . -name "*.py" -type f | grep -v -E '__pycache__|venv|\.venv|node_modules|\.git|dist|build|\.tox'
```

**统计文件数量：**
```bash
find . -name "*.py" -type f | grep -v -E '__pycache__|venv|\.venv|node_modules|\.git|dist|build|\.tox' | wc -l
```

**快速检查行长度：**
```bash
grep -rn ".\{80,\}" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=venv --exclude-dir=.venv --exclude-dir=node_modules .
```

**使用系统命令查找常见问题：**
- 查找函数名驼峰化：`grep -rn "def [a-z]*[A-Z]" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=venv .`
- 查找类名小写开头：`grep -rn "class [a-z]" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=venv .`
- 查找 Tab 缩进：`grep -rn $'\t' --include="*.py" --exclude-dir=__pycache__`

#### 使用 Glob 工具（所有平台）

WorkBuddy 的 Glob 工具屏蔽了平台差异，也可使用：
- 模式：`**/*.py` - 递归查找所有 .py 文件
- 然后手动过滤排除目录

### 第二步：阅读规范文档

在执行检查前，先读取 `specifications/` 目录下的规范文档：

1. `pep8-guidelines.md` - PEP8 代码风格指南
2. `naming-conventions.md` - 命名规范
3. `code-organization.md` - 代码组织规范
4. `documentation-standards.md` - 文档规范
5. `best-practices.md` - 最佳实践
6. `cross-platform-usage.md` - **跨平台使用指南**（重要）

使用 Read 工具逐个读取这些文档，理解检查标准。

### 第三步：逐文件详细检查

对于每个Python文件，使用 Read 工具读取文件内容，然后按以下项目进行检查：

#### PEP8规范检查

1. **行长度检查**：
   - 代码行不超过79字符
   - 注释和文档字符串不超过72字符
   - 超过长度的行标记为问题

2. **缩进检查**：
   - 检查是否使用Tab字符（`\\t`）
   - 应该使用4个空格缩进

3. **导入语句检查**：
   - 导入应该在文件开头
   - 导入顺序是否正确：标准库 → 第三方库 → 本地模块
   - 是否有通配符导入（`from module import *`）
   - 多个导入是否在同一行

4. **空格检查**：
   - 运算符周围空格使用
   - 逗号、冒号、分号前不要有空格
   - 括号内不要有多余空格

#### 命名规范检查

1. **类名检查**：
   - 类名应该使用CamelCase（首字母大写驼峰）
   - 例如：`class UserAccount:` ✓
   - 例如：`class user_account:` ✗

2. **函数名/方法名检查**：
   - 应该使用snake_case（小写下划线）
   - 例如：`def calculate_total():` ✓
   - 例如：`def calculateTotal():` ✗

3. **变量名检查**：
   - 应该使用snake_case（小写下划线）
   - 例如：`user_name = "John"` ✓
   - 例如：`userName = "John"` ✗

4. **常量检查**：
   - 模块级常量应该使用UPPER_CASE（大写下划线）
   - 例如：`MAX_SIZE = 100` ✓
   - 例如：`max_size = 100` ✗

#### 文档规范检查

对于每个模块、类、函数，检查是否有文档字符串：

1. **模块文档字符串**：文件开头应该有模块描述
2. **类文档字符串**：类定义下应该有类说明
3. **函数文档字符串**：函数/方法应该有参数、返回值说明

#### 代码结构检查

1. **函数长度**：函数是否过长（建议不超过50行）
2. **空行使用**：函数之间、类之间是否有适当的空行
3. **代码重复**：是否有重复的代码块

### 第四步：记录问题

为每个发现的问题创建清晰的记录：

- **文件路径**：问题所在文件的相对路径
- **行号**：问题所在行
- **问题类型**：如"缺少文档字符串"、"命名不规范"等
- **严重程度**：error、warning、info
- **问题说明**：清晰的描述问题
- **代码片段**：问题代码的示例
- **改进建议**：具体的改进步骤

### 第五步：生成报告

创建一个 Markdown 格式的报告文件（默认：`code_standards_report.md`），包含：

**编码约束（Windows 必须遵守）：**
- 报告文件统一使用 UTF-8 编码写入，推荐 `utf-8-sig`，避免编辑器将中文 Markdown 误判为 GBK 导致乱码。
- 不要通过 PowerShell here-string 后再 `python -` 的方式内联传递大量中文模板文本；这类写法在 Windows 终端中容易在标准输入链路上损坏非 ASCII 字符。
- 生成中文报告时，优先执行一个保存在磁盘上的 `.py` 脚本文件，再由脚本写出 Markdown 文件。
- 如果必须在终端读取或写入中文内容，需要显式指定 UTF-8，并避免依赖控制台默认编码。

#### 报告结构

1. **标题**：Python代码规范检查报告

2. **概览**：
   - 项目路径
   - 检查的文件数量
   - 发现的问题总数
   - 严重程度统计（error、warning、info数量）

3. **问题统计**：
   - 错误数量
   - 警告数量
   - 信息数量

4. **详细问题列表**：
   按文件分组列出所有问题，每个问题包含：
   - 行号
   - 简短描述
   - 问题类型
   - 严重程度
   - 代码片段（使用代码块）
   - 改进建议

   示例格式：
   ```markdown
   ### src/module.py

   ⚠️ **行 25**: 函数缺少文档字符串
   - 类型: missing_function_docstring
   - 严重程度: warning
   - 代码片段: ```python
     def process_data():
         pass
     ```
   - 改进建议: 添加函数文档字符串，说明其功能、参数和返回值
   ```

5. **改善建议汇总**：
   按类别提供改进建议：
   - PEP8规范改进
   - 文档字符串改进
   - 命名规范改进
   - 代码结构改进

6. **推荐工具**：
   列出帮助改善代码质量的工具：
   - black（自动格式化）
   - flake8（代码检查）
   - pylint（代码分析）
   - mypy（类型检查）
   - pydocstyle（文档检查）

   包含安装和使用命令示例。

使用 Write 工具创建报告文件。

### 第六步：总结输出

向用户输出检查结果摘要：

```
检查完成 ✓
-----------
扫描文件: X个
发现问题: X个
  - 错误: X个
  - 警告: X个
  - 信息: X个

详细报告已生成: code_standards_report.md
```

使用 Bash 工具运行 `open_result_view` 打开报告文件（如果适用）。

## 编码与输出约束

1. **报告编码**：Markdown 报告默认写为 UTF-8，Windows 下优先使用 `utf-8-sig`。
2. **中文内容生成方式**：不要把大段中文直接嵌入 PowerShell 管道传给 `python -`；应改为执行 UTF-8 编码的脚本文件。
3. **读取文件**：读取源码或报告时显式指定 UTF-8；若存在 BOM，则兼容 `utf-8-sig`。
4. **终端限制**：终端输出可用于摘要统计，但不要把终端回显当成中文内容正确性的唯一验证依据，应回读生成文件确认。

## 检查技巧

1. **优先级**：先标记error级别的问题，然后是warning，最后是info
2. **代码片段**：只显示问题相关的代码行，不要截取过多
3. **建议具体**：改进建议应该具体可执行，如"将函数名重命名为 snake_case 格式"
4. **示例代码**：对于命名规范等问题，展示正确的命名示例
5. **分组统计**：在报告中按文件分组，方便用户逐个修复
6. **利用系统命令**：对于大型项目，先使用系统命令快速扫描，再逐个检查问题文件

## 规范文档使用

规范文档是此技能的知识库，执行检查前应该：

1. 使用 Read 工具读取 `specifications/` 下的所有规范文档
2. 理解每项规范的具体要求
3. 按照规范文档中的示例进行检查

### 规范文档列表：

**核心规范：**
- `specifications/pep8-guidelines.md` - PEP8 代码风格指南
- `specifications/naming-conventions.md` - 命名规范
- `specifications/code-organization.md` - 代码组织规范
- `specifications/documentation-standards.md` - 文档规范
- `specifications/best-practices.md` - 最佳实践

**跨平台指南：**
- `specifications/cross-platform-usage.md` - **跨平台使用指南**
  - Windows PowerShell 命令参考
  - Linux/macOS Shell 命令参考
  - 平台特定的文件处理方法
  - 路径和编码处理差异
  - 常见跨平台问题和解决方案

**重要：** 在不同操作系统上使用此技能前，请务必阅读 `cross-platform-usage.md` 文档。

## 快速检查方法

### 方法 1：使用系统命令快速扫描

**Windows PowerShell：**
```powershell
# 快速发现长行
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    $result = Select-String -Path $_.FullName -Pattern "^.{80,}$"
    if ($result) { $result }
}

# 快速发现函数命名不规范
Get-ChildItem -Recurse -Filter *.py | Select-String "def [a-z]*[A-Z]"
```

**Linux/macOS：**
```bash
# 快速发现长行
grep -rn ".\{80,\}" --include="*.py" --exclude-dir=__pycache__ .

# 快速发现函数命名不规范
grep -rn "def [a-z]*[A-Z]" --include="*.py" --exclude-dir=__pycache__ .

# 快速发现类命名不规范
grep -rn "class [a-z]" --include="*.py" --exclude-dir=__pycache__ .
```

### 方法 2：使用 WorkBuddy Bash 工具

在 Bash 工具中根据平台选择对应命令，快速扫描项目。

## 输出文件

- **code_standards_report.md**：详细的检查报告，保存在项目根目录

## 技能文件结构

```
python-code-standards-validator/
├── SKILL.md                                    # 技能主文档
└── specifications/
    ├── pep8-guidelines.md                      # PEP8 规范
    ├── naming-conventions.md                   # 命名规范
    ├── code-organization.md                    # 代码组织
    ├── documentation-standards.md              # 文档规范
    ├── best-practices.md                       # 最佳实践
    └── cross-platform-usage.md                 # 跨平台使用指南
```

## 注意事项

1. **安全性**：检查是只读操作，不会修改任何源代码
2. **性能**：对于大型项目（1000+ 文件），检查可能需要较长时间
3. **文件覆盖**：报告文件会覆盖同名文件
4. **扫描范围**：只扫描当前工作目录，不包括子项目或依赖包
5. **跨平台兼容性**：
   - Windows 使用 PowerShell 命令
   - Linux/macOS 使用 Shell 命令
   - Git Bash 在 Windows 上可使用 Linux 风格命令
6. **排除目录**：默认排除 `__pycache__`、`venv`、`.venv`、`node_modules` 等目录
7. **编码处理**：使用 UTF-8 编码读取文件，避免 Windows GBK 编码问题

## 工作流程总结

1. 扫描 → 使用系统命令查找所有Python文件
2. 阅读规范 → 理解检查标准
3. 快速扫描 → 使用系统命令快速发现常见问题
4. 检查代码 → 逐文件、逐项详细检查
5. 记录问题 → 详细记录每个问题
6. 生成报告 → 创建Markdown报告文件
7. 输出摘要 → 向用户展示检查结果

执行此技能时，严格遵循以上流程，确保检查的完整性和报告的准确性。
