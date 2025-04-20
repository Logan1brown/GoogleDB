import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import and run the main dashboard app
from src.dashboard.app import main

if __name__ == "__main__":
    main()
