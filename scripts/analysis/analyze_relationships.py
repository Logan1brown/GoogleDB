"""Script to analyze network-creative relationships."""

from src.data_processing.analyze_shows import ShowsAnalyzer
from src.data_processing.creative_networks.network_connections import NetworkConnectionAnalyzer
from src.data_processing.creative_networks.role_analysis import RoleAnalyzer

def main():
    """Run the network and role analysis."""
    # Get clean data
    shows_analyzer = ShowsAnalyzer()
    shows_df, team_df = shows_analyzer.fetch_data()
    shows_analyzer.clean_data()
    
    # Create network connection visualization
    network_analyzer = NetworkConnectionAnalyzer(
        shows_analyzer.shows_df,
        shows_analyzer.team_df
    )
    network_analyzer.create_visualization()
    
    # Create role analysis visualization
    role_analyzer = RoleAnalyzer(
        shows_analyzer.shows_df,
        shows_analyzer.team_df
    )
    role_analyzer.create_visualization()

if __name__ == '__main__':
    main()
