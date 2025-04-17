#!/bin/bash

# Usage: ./scripts/utils/restart_streamlit.sh <path/to/app.py>
# Example: ./scripts/utils/restart_streamlit.sh src/data_entry/v3/data_entry_app_v3.py

# Load environment variables
set -a
source .env
set +a

# Use STREAMLIT_PORT from environment, default to 8501
PORT=${STREAMLIT_PORT:-8501}
MAX_WAIT=10  # Maximum seconds to wait for port to free up

echo "Stopping Streamlit..."
# Kill any existing Streamlit processes
pkill -f streamlit

echo "Waiting for processes to end..."
# Give pkill time to complete
sleep 2

# Force kill any remaining processes
pkill -9 -f streamlit 2>/dev/null || true
sleep 1

echo "Checking port $PORT..."
# Wait for port to be free with timeout
wait_count=0
while lsof -i :$PORT > /dev/null 2>&1; do
    if [ $wait_count -ge $MAX_WAIT ]; then
        echo "ERROR: Port $PORT still in use after ${MAX_WAIT}s"
        exit 1
    fi
    sleep 1
    wait_count=$((wait_count + 1))
done

echo "Starting Streamlit..."
source venv/bin/activate && PYTHONPATH=$PYTHONPATH:$(pwd)/src streamlit run src/dashboard/app.py --server.port $PORT
