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
echo "[INFO] RUN PREPARE" >${WORKDIR}/run.log 2>&1
chmod +x ${WORKDIR}/bin/env_prepare.sh
${WORKDIR}/bin/env_prepare.sh ${VENV_NAME} >>${WORKDIR}/run.log 2>&1
if [ $? -ne 0 ]; then
    echo "[ERROR] 环境准备失败。"
    exit 1
fi
chmod +x ${WORKDIR}/bin/start.sh
echo "[INFO] RUN START" >>${WORKDIR}/run.log 2>&1
nohup ${WORKDIR}/bin/start.sh ${VENV_NAME}  >>${WORKDIR}/run.log 2>&1 &

