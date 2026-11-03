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

if [ ! -f "$WORKDIR/bin/main.ss" ]; then
    echo "[ERROR] 未找到 $WORKDIR/bin/main.ss 文件，请确保项目结构正确。"
    exit 1
fi

if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "[INFO] 检测到 Python 虚环境，正在激活..."
    source "$VENV_DIR/bin/activate"
else
    echo "[WARNING] 未检测到 Python 虚环境，建议创建虚环境以隔离依赖。"
    exit 1
fi

cd "$WORKDIR"

export PYTHONPATH=$WORKDIR/src

source $WORKDIR/resources/.env.${AIENV:-test}
source $WORKDIR/bin/main.ss

while [ 1 ]
do  
    for main in "${MAIN[@]}"
    do
        sleep 1
        app=`echo $main|awk -F":" '{print $1}'`
        port=`echo $main|awk -F":" '{print $2}'`
        if [ -z "$app" ]; then
            echo "[ERROR] 无效的 MAIN 配置: $main，正确格式应为 app:port"
            continue
        fi
        strport=$port
        if [ -z "$strport" ]; then
            strport=$app
        fi
        yes=`ps -ef|grep "$app"|grep "$strport"|grep -v grep|wc -l`
        if [ $yes -eq 0 ]
        then
            echo "Starting $main ......"
            if [ -z "$port" ]; then
                nohup python3 "$app" &
            else
                nohup python3 "$app" --port "$port" &
            fi
            sleep 30
        fi
    done
done

