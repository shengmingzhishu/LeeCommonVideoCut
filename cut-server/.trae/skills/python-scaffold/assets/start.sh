#!/bin/bash

# Configuration
APP_NAME="{{ project_name }}"
VENV_DIR=".venv"
PYTHON_BIN="$VENV_DIR/bin/python"
MAIN_SCRIPT="{{ project_name }}/main.py"
PID_FILE=".app.pid"
LOG_FILE="app.log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Starting $APP_NAME..."

# Check if virtualenv exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Error: Virtual environment not found at $VENV_DIR${NC}"
    echo "Please run 'make install' first."
    exit 1
fi

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
        echo -e "${RED}Error: $APP_NAME is already running (PID: $PID)${NC}"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

# Execute
# Use nohup for background execution or remove it for foreground
nohup "$PYTHON_BIN" "$MAIN_SCRIPT" > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

if ps -p "$NEW_PID" > /dev/null; then
    echo -e "${GREEN}Successfully started $APP_NAME (PID: $NEW_PID)${NC}"
    echo "Logs are being written to $LOG_FILE"
else
    echo -e "${RED}Failed to start $APP_NAME${NC}"
    exit 1
fi
