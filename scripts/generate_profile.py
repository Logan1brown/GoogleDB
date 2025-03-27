#!/usr/bin/env python3
"""Script to generate a profile report for TV shows data."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data_processing.analyze_shows import shows_analyzer

def main():
    """Generate profile report for TV shows data."""
    shows_analyzer.generate_profile_report()

if __name__ == "__main__":
    main()
