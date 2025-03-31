#!/bin/bash

# Kill any running Streamlit processes
pkill -f streamlit

# Wait a moment for processes to clean up
sleep 2

# Start Streamlit
cd "$(dirname "$0")"  # Move to script directory
streamlit run src/dashboard/app.py
