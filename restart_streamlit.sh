#!/bin/bash

# Move to script directory
cd "$(dirname "$0")"

# Kill any running Streamlit processes (force kill if needed)
pkill -9 -f streamlit

# Wait a moment for processes to clean up
sleep 2

# Clear Streamlit cache
rm -rf ~/.streamlit/cache
rm -rf ~/.streamlit/runtime
rm -rf ~/.cache/streamlit

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -r {} +

# Source environment setup
source setup_env.sh

# Start Streamlit
streamlit run src/dashboard/app.py
