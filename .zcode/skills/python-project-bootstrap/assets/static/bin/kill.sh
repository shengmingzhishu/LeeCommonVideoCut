#!/bin/bash

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

echo "[INFO] 工作目录: $WORKDIR"
echo "[INFO] 虚环境目录: $VENV_DIR"
echo "[INFO] AIENV: $AIENV"

myid=`ps -ef | grep "${WORKDIR}/bin/start.sh"| grep "${VENV_NAME}" | grep -v grep | awk '{print $2}'`

if [ -n "$myid" ]; then
    #kill -9 $myid
    TMP=/tmp/kill_$$.pid
    echo $myid > $TMP
    ps -ef | grep "python" |grep -v grep|awk -v pp=$myid '{if($3==pp)print $2}' >> $TMP
    for pid in `cat $TMP`
    do
        kill -9 $pid
    done
    rm -f $TMP
    echo "Process $myid killed."
else
    echo "No process found."
fi
