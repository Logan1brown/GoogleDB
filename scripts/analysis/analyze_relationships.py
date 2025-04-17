"""Script to analyze network-creative relationships."""

import logging
from src.data_processing.analyze_shows import ShowsAnalyzer
from src.data_processing.creative_networks.network_connections import NetworkConnectionAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the network analysis."""
    # Get clean data
    shows_analyzer = ShowsAnalyzer()
    shows_df, team_df, network_df = shows_analyzer.fetch_data()
    
    if shows_df.empty:
        logger.error("No show data available")
        return
    if team_df.empty:
        logger.error("No team data available")
        return
    
    # Create network connection visualization
    network_analyzer = NetworkConnectionAnalyzer(
        shows_analyzer.shows_df,
        shows_analyzer.team_df
    )
    network_analyzer.create_visualization()

if __name__ == '__main__':
    main()
