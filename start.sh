#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Ensure macOS OpenMP library path
if [ -d "/opt/homebrew/opt/libomp/lib" ]; then
    export DYLD_LIBRARY_PATH="/opt/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH"
fi
export PYTHONPATH="."

echo "================================================================="
echo "  AI PLACEMENT PREDICTOR: INSTITUTIONAL CAREER READINESS ENGINE  "
echo "================================================================="

# Start FastAPI Backend on port 8001
echo "Starting FastAPI Backend on http://127.0.0.1:8001..."
"$DIR/.venv/bin/uvicorn" api.main:app --host 127.0.0.1 --port 8001 &
BACKEND_PID=$!

# Wait for backend health
echo "Waiting for backend service to be ready..."
sleep 2

# Start Vite Frontend on port 5173
echo "Starting React Frontend on http://localhost:5173..."
npm --prefix frontend run dev &
FRONTEND_PID=$!

cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

wait
