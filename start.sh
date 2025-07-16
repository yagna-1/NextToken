#!/bin/bash
set -e

echo "Starting NextToken backend..."
echo "Port: $PORT"
echo "Host: 0.0.0.0"

# Start the FastAPI application
exec uvicorn nextoken.main:app --host 0.0.0.0 --port $PORT 