#!/usr/bin/env bash
# startup script for Render.com deployments
# Render sets the PORT environment variable automatically.  Uvicorn will bind to it.

# Activate a virtual environment if needed (Render handles dependencies from requirements.txt)
# You can uncomment and modify the following lines if you need to source a venv:
# if [ -f venv/bin/activate ]; then
#     source venv/bin/activate
# fi

# default port if not provided
PORT=${PORT:-8000}

echo "Starting FastAPI app on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"