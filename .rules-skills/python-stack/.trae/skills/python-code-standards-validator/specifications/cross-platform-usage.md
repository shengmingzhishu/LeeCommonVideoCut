# 跨平台使用指南

## 概述

本技能支持在 Windows、Linux 和 macOS 系统上运行 Python 代码标准检查。通过使用各操作系统自带的命令行工具（Windows PowerShell、Linux/macOS Shell），实现跨平台的代码检查。

## 支持的操作系统

- ✅ Windows - 使用 PowerShell 或 Git Bash
- ✅ Linux - 使用 Bash/Shell
- ✅ macOS - 使用 Bash/Zsh

## 平台选择策略

### Windows 环境

**推荐：PowerShell** - Windows 原生环境
- 命令更简洁
- 更好的 Windows 文件系统支持
- 不需要额外安装

**备选：Git Bash** - 类 Unix 环境
- 兼容 Linux/macOS 风格命令
- 适合习惯 Unix 命令的用户
- 需要安装 Git for Windows

### Linux / macOS 环境

**使用：Shell (Bash/Zsh)**
- 原生环境，无需额外配置
- 命令丰富，功能强大

## 支持的操作系统

- ✅ Windows (含 Git Bash、PowerShell)
- ✅ Linux (Ubuntu, CentOS, Debian, 等)
- ✅ macOS

## 路径处理差异

### Windows

**路径分隔符：** `\`

**示例：**
```powershell
# PowerShell
C:\Users\username\project\src\module.py
```

**注意事项：**
- 在 PowerShell 中使用 `\` 作为路径分隔符
- 路径不区分大小写
- 可能遇到编码问题（传统的命令行工具使用系统编码）

### Linux / macOS

**路径分隔符：** `/`

**示例：**
```bash
/home/username/project/src/module.py
```

**注意事项：**
- 路径区分大小写
- 禁止在文件名中使用 `\`
- 默认使用 UTF-8 编码

## 平台特定文件查找命令

### Windows (PowerShell)

**查找所有 .py 文件：**
```powershell
Get-ChildItem -Recurse -Filter *.py
```

**排除特定目录：**
```powershell
Get-ChildItem -Recurse -Filter *.py | Where-Object {
    $_.FullName -notmatch '__pycache__|venv|\.venv|node_modules|\.git|dist|build|\.tox'
}
```

**仅筛选文件名：**
```powershell
Get-ChildItem -Recurse -Filter *.py | Select-Object Path, Name
```

**获取文件列表作为数组：**
```powershell
$files = Get-ChildItem -Recurse -Filter *.py | Where-Object {
    $_.FullName -notmatch '__pycache__|venv|\.venv'
}
Write-Output $files.Count
```

### Linux / macOS (Bash)

**查找所有 .py 文件：**
```bash
find . -name "*.py"
```

**排除特定目录：**
```bash
find . -name "*.py" -not -path "*/__pycache__/*" \
  -not -path "*/venv/*" \
  -not -path "*/.venv/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*"
```

**使用 grep 过滤：**
```bash
find . -name "*.py" | grep -v -E '__pycache__|venv|\.venv|node_modules|\.git|dist|build|\.tox'
```

**只查找文件（不含目录）：**
```bash
find . -name "*.py" -type f
```

## 编码处理

### Windows

**默认编码：** GBK/CP936（中文系统）

**问题：** 某些传统命令行工具使用系统编码，处理 UTF-8 内容时可能乱码

**解决方案：**
- 使用 PowerShell 5.1+ 或 PowerShell Core（默认支持 UTF-8）
- 在读取文件时明确指定编码
- 生成中文 Markdown 或报告文件时优先使用 `utf-8-sig` 写入，降低编辑器误判编码的概率
- 避免将大段中文文本通过 PowerShell here-string 管道传递给 `python -`，优先运行磁盘上的 UTF-8 Python 脚本
- 生成完成后回读目标文件确认内容，而不是只看终端输出

### Linux / macOS

**默认编码：** UTF-8

**无需特殊处理**

## 常见问题检查命令

### 行长度检查

**Windows PowerShell：**
```powershell
# 查找超过79字符的行
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    $lineNum = 0
    Get-Content $_.FullName | ForEach-Object {
        $lineNum++
        if ($_.Length -gt 79) {
            Write-Output "$($_.FullName):$lineNum : Length $($_.Length)"
        }
    }
}
```

**Linux/macOS：**
```bash
# 查找超过79字符的行
grep -rn ".\{80,\}" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=venv .
```

### 命名规范检查

**Windows PowerShell：**
```powershell
# 查找函数名使用驼峰法（不符合规范）
Get-ChildItem -Recurse -Filter *.py | Select-String "def [a-z]*[A-Z]"

# 查找类名使用小写（不符合规范）
Get-ChildItem -Recurse -Filter *.py | Select-String "class [a-z]"
```

**Linux/macOS：**
```bash
# 查找函数名使用驼峰法
grep -rn "def [a-z]*[A-Z]" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=venv .

# 查找类名使用小写
grep -rn "class [a-z]" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=venv .
```

### 缩进检查

**Windows PowerShell：**
```powershell
# 查找使用 Tab 缩进的行（不符合规范）
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    $lineNum = 0
    Get-Content $_.FullName | ForEach-Object {
        $lineNum++
        if ($_ -match "^\t") {
            Write-Output "$($_.FullName):$lineNum : Using tabs instead of spaces"
        }
    }
}
```

**Linux/macOS：**
```bash
# 查找使用 Tab 缩进的行
grep -rn $'\t' --include="*.py" --exclude-dir=__pycache__ --exclude-dir=venv .
```

### 尾随空格检查

**Windows PowerShell：**
```powershell
# 查找包含尾随空格的行
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    $lineNum = 0
    Get-Content $_.FullName | ForEach-Object {
        $lineNum++
        if ($_ -match " +$") {
            Write-Output "$($_.FullName):$lineNum : Trailing whitespace"
        }
    }
}
```

**Linux/macOS：**
```bash
# 查找包含尾随空格的行
grep -rn " \+$" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=venv .
```

### 导入语句检查

**Linux/macOS：**
```bash
# 查找 from module import * 通配符导入
grep -rn "from .* import \*" --include="*.py" .

# 查找单行多个导入
grep -rn "^import .*," --include="*.py" .
```

**Windows PowerShell：**
```powershell
# 查找通配符导入
Get-ChildItem -Recurse -Filter *.py | Select-String "from .* import \*"

# 查找单行多个导入
Get-ChildItem -Recurse -Filter *.py | Select-String "^import .*,"
```

## WorkBuddy 中的跨平台操作

### 自动检测平台

在 WorkBuddy 执行检查时，根据平台选择相应的命令：

**示例：查找 Python 文件数量**

```python
# 在 WorkBuddy 中使用 Bash 工具
# WorkBuddy 会自动根据环境选择合适的Shell

# 以下命令在 Bash/Git Bash 中生效
find . -name "*.py" -type f | grep -v -E '__pycache__|venv|\.venv' | wc -l
```

如果是 Windows PowerShell 环境，使用 PowerShell 命令：

```powershell
(Get-ChildItem -Recurse -Filter *.py | Where-Object {
    $_.FullName -notmatch '__pycache__|venv|\.venv'
}).Count
```

### 路径处理建议

**推荐做法：**
1. 在 WorkBuddy 中使用相对路径
2. 使用 `./` 或 `.` 表示当前目录
3. 避免硬编码绝对路径

**示例：**
```bash
# 不推荐（绝对路径）
Get-ChildItem C:/Users/username/project -Recurse

# 推荐（相对路径）
Get-ChildItem . -Recurse
find . -name "*.py"
```

## 常见跨平台问题与解决

### 问题 1: 路径分隔符不同

**场景：** 不同平台路径分隔符不同

**Windows:** \ (反斜杠)
**Linux/macOS:** / (正斜杠)

**解决方法：**
- 在命令行中使用引号包裹包含空格的路径
- 使用相对路径避免硬编码
- 关注文件内容而非文件路径

### 问题 2: 命令语法差异

**场景：** 不同平台的Shell命令语法不同

**解决方法：**
- 一个平台使用一种命令风格
- 在本技能中明确区分 Windows PowerShell 和 Linux/macOS Shell
- 遵循各自平台的最佳实践

### 问题 3: 大型项目性能

**场景：** 检查包含数千个文件的项目

**解决方法：**
1. 先使用系统命令快速筛选问题文件
2. 只对有问题的文件进行详细检查
3. 使用 `--exclude-dir` 参数排除不必要的目录

**Linux/macOS 优化示例：**
```bash
# 只检查发现长行的文件
for file in $(find . -name "*.py" | grep -v -E '__pycache__|venv'); do
  if grep -q ".\{80,\}" "$file"; then
    echo "Checking: $file"
    # 对该文件进行详细检查
  fi
done
```

## 实用的命令组合

### 组合 1: 快速扫描 + 定位问题

**Linux/macOS:**
```bash
# 1. 查找所有 Python 文件
# 2. 过滤掉常见的长行
# 3. 输出有问题的文件列表
grep -l ".\{80,\}" --include="*.py" --exclude-dir=__pycache__ -r .
```

**Windows PowerShell:**
```powershell
# 1. 查找包含长行的文件
# 2. 输出文件路径
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    if (Select-String -Path $_.FullName -Pattern "^.{80,}$" -Quiet) {
        Write-Output $_.FullName
    }
}
```

### 组合 2: 统计问题类型

**Linux/macOS:**
```bash
echo "=== Line Length Issues ==="
grep -c ".\{80,\}" --include="*.py" -r . | grep -v ":0"

echo -e "\n=== CamelCase Function Names ==="
grep -c "def [a-z]*[A-Z]" --include="*.py" -r . | grep -v ":0"

echo -e "\n=== Lowercase Class Names ==="
grep -c "class [a-z]" --include="*.py" -r . | grep -v ":0"
```

**Windows PowerShell:**
```powershell
Write-Output "=== Line Length Issues ==="
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    $count = (Select-String -Path $_.FullName -Pattern "^.{80,}$").Count
    if ($count -gt 0) {
        Write-Output "$($_.Name): $count"
    }
}
```

### 组合 3: 按模块分组统计

**Linux/macOS:**
```bash
# 按顶层目录分组统计
find . -maxdepth 2 -name "*.py" -type f | grep -v __pycache__ | while read file; do
    module=$(echo "$file" | cut -d'/' -f2)
    echo "$module"
done | sort | uniq -c
```

## Windows PowerShell 最佳实践

### 基本操作

```powershell
# 查看当前位置
Get-Location
# 或
pwd

# 切换目录
Set-Location "C:\path\to\project"
# 或
cd "C:\path\to\project"

# 列出文件
Get-ChildItem
# 或
ls

# 创建数组
$pyFiles = Get-ChildItem -Recurse -Filter *.py

# 遍历数组
foreach ($file in $pyFiles) {
    Write-Output $file.FullName
}

# 管道操作
Get-ChildItem -Recurse -Filter *.py | Where-Object { $_.Length -gt 1000 }

# 输出到文件
Get-ChildItem -Recurse -Filter *.py | Out-File filelist.txt
```

### 常用代码检查命令

```powershell
# 统计代码行数
$lines = (Get-ChildItem -Recurse -Filter *.py | Get-Content | Measure-Object -Line).Lines

# 查找所有导入语句
Select-String -Path *.py -Pattern "^import |^from "

# 查找文档字符串
Select-String -Path *.py -Pattern "^[\t ]*\"\"\"\""

# 查找空函数
Select-String -Path *.py -Pattern "def [a-z_]+\([^)]*\):\s*$"
```

## Linux/macOS Shell 最佳实践

### 基本操作

```bash
# 查看当前位置
pwd

# 切换目录
cd /path/to/project

# 列出文件
ls -la

# 找到文件后处理
find . -name "*.py" | while read file; do
    echo "Processing: $file"
done

# 管道操作
find . -name "*.py" | grep -v __pycache__ | xargs wc -l

# 输出到文件
find . -name "*.py" > filelist.txt
```

### 常用代码检查命令

```bash
# 统计代码行数
find . -name "*.py" -not -path "*/__pycache__/*" | xargs cat | wc -l

# 查找所有导入语句
grep -rh "^import \|^from " --include="*.py" .

# 查找文档字符串
grep -rh '^[[:space:]]*"""' --include="*.py" .

# 查找空函数
grep -rh "def [a-z_]*():\s*$" --include="*.py" .
```

## Git Bash 特殊说明

### 在 Windows 上使用 Git Bash

Git Bash 是 Windows 上获得类 Unix 环境的最佳方式：

**优势：**
- 完整的 Unix 命令支持（ls, grep, find 等）
- 与 Linux/macOS 命令兼容
- 路径处理更简单
- 脚本可移植性强

**配置建议：**
1. 安装 Git for Windows 时选择使用 Git Bash
2. 在 WorkBuddy 中优先使用 Git Bash 而非 CMD
3. 使用 Unix 风格的路径和命令

### Git Bash vs CMD vs PowerShell

| 特性 | Git Bash | CMD | PowerShell |
|-----|---------|-----|------------|
| Unix 命令 | ✅ | ❌ | 部分 |
| 路径风格 | `/` | `\` | `\` |
| 管道操作 | ✅ | 有限 | ✅ |
| 跨平台兼容 | ✅ | ❌ | 部分 |

## 参考资源

### Windows PowerShell
- [PowerShell 文档](https://docs.microsoft.com/zh-cn/powershell/)
- [Get-ChildItem 命令](https://docs.microsoft.com/zh-cn/powershell/module/microsoft.powershell.management/get-childitem)
- [Select-String 命令](https://docs.microsoft.com/zh-cn/powershell/module/microsoft.powershell.utility/select-string)

### Linux/macOS Shell
- [Bash 参考](https://www.gnu.org/software/bash/manual/)
- [find 命令手册](https://man7.org/linux/man-pages/man1/find.1.html)
- [grep 命令手册](https://man7.org/linux/man-pages/man1/grep.1.html)

### Git Bash
- [Git for Windows](https://gitforwindows.org/)
- [Git Bash 基础](https://git-scm.com/book/zh/v2/Git-%E5%9F%BA%E7%A1%80--%E5%91%BD%E4%BB%A4%E8%A1%8C)
