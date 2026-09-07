#!/bin/bash

OK_MSG="OK"
ERROR_MSG="ERROR"

w=`whoami`
if [ "${w}" == "root" ]
then
        echo ${ERROR_MSG}
        exit 1
fi
# 获取当前工作目录
WORKDIR=$(dirname "$(realpath "$0")")
cd "$WORKDIR"

cd ..
WORKDIR=$(pwd)
source $WORKDIR/resources/.env.${AIENV}
echo "[INFO] 工作目录: $WORKDIR"
echo "[INFO] AIENV: $AIENV"
# 要测试的 URL
URL="http://127.0.0.1:${PORT:-8088}/init"

# 发送请求，捕获 HTTP 状态码，并将响应内容丢弃
HTTP_CODE=$(curl -s -L -o /dev/null -w "%{http_code}" "$URL")
CURL_EXIT=$?  # curl 自身的退出状态（0=成功, 非0=网络/DNS/协议等错误）

# 判断逻辑
if [ $CURL_EXIT -eq 0 ] && [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 400 ]; then
    echo ${OK_MSG}
    exit 0
else
    echo ${ERROR_MSG}
    exit 1
fi