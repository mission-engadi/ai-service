#!/bin/bash
# AI Service - Stop Script

SERVICE_NAME="ai-service"
PID_FILE="/tmp/${SERVICE_NAME}.pid"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Stopping ${SERVICE_NAME}..."

if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}Service is not running (no PID file found)${NC}"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${RED}Service is not running (stale PID file)${NC}"
    rm -f "$PID_FILE"
    exit 1
fi

kill "$PID"
sleep 2

# Force kill if still running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Force stopping..."
    kill -9 "$PID"
fi

rm -f "$PID_FILE"
echo -e "${GREEN}${SERVICE_NAME} stopped successfully${NC}"
