#!/usr/bin/env python3
"""Run genre analysis on the TV shows database."""

import logging
from pathlib import Path

from src.data_processing.analyze_shows import shows_analyzer
from src.data_processing.content_strategy.genre_analysis_2 import GenreAnalyzer

logger = logging.getLogger(__name__)

def main():
    """Run the genre analysis."""
    # Fetch and clean data
    shows_analyzer.fetch_data()
    shows_analyzer.clean_data()
    
    # Create genre analyzer
    genre_analyzer = GenreAnalyzer(shows_analyzer.shows_df)
    
    # Generate insights and visualization
    logger.info("Generating genre insights and visualization...")
    genre_analyzer.create_genre_heatmap()
    
    logger.info("Analysis complete. View the results in output/visualizations/genre_analysis.html")

if __name__ == '__main__':
    main()
