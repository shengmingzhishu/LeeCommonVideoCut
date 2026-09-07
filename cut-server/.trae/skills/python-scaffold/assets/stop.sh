#!/bin/bash

APP_NAME="{{ project_name }}"
PID_FILE=".app.pid"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}PID file not found. Is $APP_NAME running?${NC}"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null; then
    echo -e "${RED}Process $PID not found.${NC}"
    rm "$PID_FILE"
    exit 1
fi

echo "Stopping $APP_NAME (PID: $PID)..."
kill "$PID"

# Wait for process to exit
for i in {1..5}; do
    if ! ps -p "$PID" > /dev/null; then
        echo -e "${GREEN}$APP_NAME stopped successfully.${NC}"
        rm "$PID_FILE"
        exit 0
    fi
    sleep 1
done

echo -e "${RED}Process $PID did not stop gracefully. Forcing...${NC}"
kill -9 "$PID"
rm "$PID_FILE"
