#!/bin/bash
set -e

echo "Starting NewsOps API..."
echo "Database: $DATABASE_URL"
echo "Host: $APP_HOST:$APP_PORT"

exec uvicorn main:app \
  --host ${APP_HOST:-0.0.0.0} \
  --port ${APP_PORT:-8000} \
  --workers 1 \
  --log-level ${LOG_LEVEL:-info}
