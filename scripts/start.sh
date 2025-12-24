#!/bin/bash
# AI Service - Start Script

SERVICE_NAME="ai-service"
SERVICE_PORT=8010
PID_FILE="/tmp/${SERVICE_NAME}.pid"
LOG_FILE="logs/${SERVICE_NAME}.log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Starting ${SERVICE_NAME}..."

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${RED}Service is already running (PID: $PID)${NC}"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# Create logs directory
mkdir -p logs

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the service
nohup uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $SERVICE_PORT \
    --reload \
    > "$LOG_FILE" 2>&1 &

PID=$!
echo $PID > "$PID_FILE"

echo -e "${GREEN}${SERVICE_NAME} started successfully (PID: $PID)${NC}"
echo "Logs: $LOG_FILE"
echo "API Docs: http://localhost:$SERVICE_PORT/docs"
