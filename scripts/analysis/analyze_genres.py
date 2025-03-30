#!/usr/bin/env python3
"""Run genre analysis on the TV shows database."""

import logging
from pathlib import Path

from src.data_processing.analyze_shows import shows_analyzer
from src.data_processing.content_strategy.genre_analyzer import analyze_genre_patterns
from src.dashboard.components.genre_view import create_genre_analysis

logger = logging.getLogger(__name__)

def main():
    """Run the genre analysis."""
    # Fetch raw data
    shows_df, _ = shows_analyzer.fetch_data()
    
    # Analyze genre patterns
    logger.info("Analyzing genre patterns...")
    analysis_results = analyze_genre_patterns(shows_df)
    
    # Create visualization
    logger.info("Generating genre analysis visualization...")
    fig = create_genre_analysis(analysis_results)
    
    # Save results
    output_path = Path("output/visualizations/genre_analysis.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output_path)
    
    logger.info(f"Analysis complete. View the results in {output_path}")

if __name__ == '__main__':
    main()