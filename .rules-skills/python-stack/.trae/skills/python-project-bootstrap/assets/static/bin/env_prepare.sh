#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <venv_name>"
    exit 1
fi

MYARGS=$1

w=`whoami`
if [ "${w}" == "root" ]
then
        echo "Disable root"
        exit 1
fi

if [ ! -d "/data" ]; then
    echo "[ERROR] /data 目录不存在，请先创建 /data 目录并确保当前用户有权限访问。"
    echo "[HINT] 创建方式示例："
    echo "       sudo mkdir -p /data && sudo chown $(whoami) /data"
    exit 1
fi

# 获取当前工作目录
WORKDIR=$(dirname "$(realpath "$0")")
cd "$WORKDIR"

cd ..
WORKDIR=$(pwd)

VENV_NAME=$(basename "$WORKDIR")-venv
VENV_DIR="/data/venv/$VENV_NAME"
echo "[INFO] 工作目录: $WORKDIR"
echo "[INFO] 虚环境目录: $VENV_DIR"
echo "[INFO] AIENV: $AIENV"

if [ "$MYARGS" != "$VENV_NAME" ]; then
    echo "[ERROR] 提供的虚环境名称 '$MYARGS' 与预期的 '$VENV_NAME' 不匹配。"
    echo "[HINT] 请确保传递正确的虚环境名称，示例："
    echo "       $0 $VENV_NAME"
    exit 1
fi

# 定义最低版本要求
MIN_MAJOR=3
MIN_MINOR=13
MIN_PATCH=8

# 检查 Python 是否安装
echo "[INFO] 正在检查 Python 环境..."

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] 未检测到 Python 环境，请先安装 Python 3.13.8 或更高版本。"
    echo "[HINT] 安装方式示例："
    echo "       Ubuntu/Debian: sudo apt update && sudo apt install python3"
    echo "       macOS: brew install python@3.13"
    echo "       或访问 https://www.python.org/downloads/ 下载安装"
    exit 1
fi

# 获取 Python 版本号
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "[INFO] 检测到 Python 版本: $PYTHON_VERSION"

# 解析版本号
IFS='.' read -r MAJOR MINOR PATCH <<< "$PYTHON_VERSION"

# 处理 patch 可能包含额外字符的情况（如 3.13.8+）
PATCH=$(echo "$PATCH" | sed 's/[^0-9].*$//')

# 版本比较函数
version_ge() {
    # 检查 $1 >= $2
    if [ "$1" -gt "$2" ]; then
        return 0
    elif [ "$1" -lt "$2" ]; then
        return 1
    fi
    return 0
}

# 检查主版本
if ! version_ge "$MAJOR" "$MIN_MAJOR"; then
    echo "[ERROR] Python 主版本过低: $MAJOR < $MIN_MAJOR"
    exit 1
fi

# 主版本相同，检查次版本
if [ "$MAJOR" -eq "$MIN_MAJOR" ]; then
    if ! version_ge "$MINOR" "$MIN_MINOR"; then
        echo "[ERROR] Python 次版本过低: $MINOR < $MIN_MINOR"
        exit 1
    fi
fi

# 主版本和次版本都相同，检查补丁版本
if [ "$MAJOR" -eq "$MIN_MAJOR" ] && [ "$MINOR" -eq "$MIN_MINOR" ]; then
    if ! version_ge "$PATCH" "$MIN_PATCH"; then
        echo "[ERROR] Python 补丁版本过低: $PATCH < $MIN_PATCH"
        exit 1
    fi
fi

echo "[SUCCESS] Python 版本检查通过 ($PYTHON_VERSION >= $MIN_MAJOR.$MIN_MINOR.$MIN_PATCH)"

echo "[INFO] 正在检查 Python 虚环境..."

if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "[INFO] 检测到 Python 虚环境，正在激活..."
    source "$VENV_DIR/bin/activate"
else
    echo "[WARNING] 未检测到 Python 虚环境，建议创建虚环境以隔离依赖。"
    echo "[INFO] 是否自动创建虚环境？(y/n)"
    #read -r CREATE_VENV
    CREATE_VENV="y"
    if [[ "$CREATE_VENV" == "y" || "$CREATE_VENV" == "Y" ]]; then
        cd /data/venv
        python3 -m venv "$VENV_NAME"
        echo "[INFO] 虚环境已创建，正在激活..."
        source "$VENV_DIR/bin/activate"
        echo "[INFO] 正在安装依赖..."
        echo "[SUCCESS] 虚环境已设置。"
    else
        echo "[HINT] 创建虚环境示例："
        echo "       cd /data/venv"
        echo "       python3 -m venv $VENV_NAME"
        echo "       source $VENV_DIR/bin/activate"
        exit 1
    fi
fi

echo "[INFO] 正在验证项目依赖的虚环境的依赖是否都已经安装"
cd "$WORKDIR"
pip install --upgrade pip  -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt  -i https://pypi.tuna.tsinghua.edu.cn/simple
echo "[INFO] 虚环境的依赖安装完成"
