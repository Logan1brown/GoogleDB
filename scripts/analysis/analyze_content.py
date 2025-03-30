#!/usr/bin/env python3
"""Run content and creative analysis on the TV shows database."""

import logging
from pathlib import Path

from src.data_processing.analyze_shows import shows_analyzer
from src.data_processing.content_analysis import ContentAnalyzer

logger = logging.getLogger(__name__)

def main():
    """Run the content analysis."""
    # Fetch and clean data
    shows_analyzer.fetch_data()
    shows_analyzer.clean_data()
    
    # Create content analyzer
    content_analyzer = ContentAnalyzer(
        shows_analyzer.shows_df,
        shows_analyzer.team_df
    )
    
    # Run analyses
    logger.info("Analyzing genre-creative patterns...")
    genre_patterns = content_analyzer.analyze_genre_creative_patterns()
    
    logger.info("Analyzing network preferences...")
    network_prefs = content_analyzer.analyze_network_preferences()
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    content_analyzer.visualize_genre_patterns()
    content_analyzer.visualize_creative_patterns()
    
    # Print some key findings
    print("\nKey Findings:")
    
    print("\nTop Creators by Genre:")
    for genre, creators in genre_patterns['top_creators_by_genre'].items():
        print(f"\n{genre}:")
        for creator, count in list(creators.items())[:3]:
            print(f"  - {creator}: {count} shows")
    
    print("\nRepeat Collaborators by Network:")
    for network, creators in network_prefs['repeat_collaborators'].items():
        print(f"\n{network}:")
        for creator, count in list(creators.items())[:3]:
            print(f"  - {creator}: {count} shows")

if __name__ == '__main__':
    main()
