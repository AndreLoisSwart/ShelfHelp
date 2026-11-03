#!/bin/sh
set -e
cd /app/backend
.venv/bin/alembic upgrade head
exec .venv/bin/uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8099
