#!/bin/bash
# AI Service - Restart Script

SERVICE_NAME="ai-service"

echo "Restarting ${SERVICE_NAME}..."

# Stop the service
./scripts/stop.sh

# Wait a moment
sleep 1

# Start the service
./scripts/start.sh
