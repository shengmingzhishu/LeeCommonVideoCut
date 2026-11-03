import os
import fnmatch
import sys

def print_tree(directory='.', prefix='', show_hidden=False, output_file=None):
    """
    以树形结构将目录内容写入文件或标准输出，自动忽略 Python 缓存文件。

    参数:
        directory: 要遍历的目录路径，默认为当前目录
        prefix: 行前缀（用于递归时的缩进）
        show_hidden: 是否显示以点开头的隐藏文件/目录
        output_file: 输出目标，可以是文件路径（字符串）或文件对象。
                     若为 None，则输出到 sys.stdout。
    """
    # 处理输出目标
    if output_file is None:
        out = sys.stdout
        need_close = False
    elif isinstance(output_file, str):
        out = open(output_file, 'w', encoding='utf-8')
        need_close = True
    else:
        out = output_file
        need_close = False

    # 需要排除的模式
    ignore_patterns = [
        '__pycache__',
        '*.py[cod]',
        '*$py.class',
        'build',
        'dist',
        '*.egg-info',
        '.eggs',
        '.venv',
        'venv',
        'env',
        'ENV',
        '.python-version',
        '.pytest_cache',
        '.mypy_cache',
        '.ruff_cache',
        '.coverage',
        '.coverage.*',
        'htmlcov',
        '.vscode',
        '.idea',
        '*.swp',
        '*.swo',
        '.DS_Store',
        'Thumbs.db',
        '.env',
        '.env.*',
        'logs',
        '*.log',
        'output',
    ]

    def is_ignored(name):
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False

    try:
        entries = []
        for entry in os.listdir(directory):
            if not show_hidden and entry.startswith('.'):
                continue
            if is_ignored(entry):
                continue
            full_path = os.path.join(directory, entry)
            is_dir = os.path.isdir(full_path)
            entries.append((entry, is_dir, full_path))

        entries.sort(key=lambda x: (not x[1], x[0].lower()))

        for i, (name, is_dir, full_path) in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{name}", file=out)

            if is_dir:
                extension = "    " if is_last else "│   "
                # 递归调用时传递同一个输出目标
                print_tree(full_path, prefix + extension, show_hidden, out)

    except PermissionError:
        print(f"{prefix}[权限不足，无法读取]", file=out)
    except FileNotFoundError:
        print(f"{prefix}[目录不存在]", file=out)

    if need_close:
        out.close()

if __name__ == "__main__":
    # 输出到文件 tree.txt
    output_filename = "tree.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(".\n")
        print_tree(output_file=f)
    print(f"树形结构已写入 {output_filename}")