#!/bin/bash
# AI Service - Status Script

SERVICE_NAME="ai-service"
SERVICE_PORT=8010
PID_FILE="/tmp/${SERVICE_NAME}.pid"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== ${SERVICE_NAME} Status ==="

if [ ! -f "$PID_FILE" ]; then
    echo -e "Status: ${RED}NOT RUNNING${NC}"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "Status: ${GREEN}RUNNING${NC}"
    echo "PID: $PID"
    echo "Port: $SERVICE_PORT"
    echo "API Docs: http://localhost:$SERVICE_PORT/docs"
    
    # Check if service is responding
    if command -v curl &> /dev/null; then
        echo ""
        echo "Health Check:"
        curl -s http://localhost:$SERVICE_PORT/api/v1/health | python3 -m json.tool 2>/dev/null || echo -e "${YELLOW}Service not responding${NC}"
    fi
else
    echo -e "Status: ${RED}NOT RUNNING${NC} (stale PID file)"
    rm -f "$PID_FILE"
    exit 1
fi
