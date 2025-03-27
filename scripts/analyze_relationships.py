"""Script to analyze network-creative relationships."""

from src.data_processing.analyze_shows import ShowsAnalyzer
from src.data_processing.creative_networks.relationship_analysis import RelationshipAnalyzer

def main():
    """Run the relationship analysis."""
    # Get clean data
    shows_analyzer = ShowsAnalyzer()
    shows_df, team_df = shows_analyzer.fetch_data()
    shows_analyzer.clean_data()
    
    # Create and run relationship analysis
    relationship_analyzer = RelationshipAnalyzer(
        shows_analyzer.shows_df,
        shows_analyzer.team_df
    )
    relationship_analyzer.create_relationship_visualization()

if __name__ == '__main__':
    main()
