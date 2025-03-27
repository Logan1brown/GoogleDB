"""Script to analyze source type patterns."""

from src.data_processing.analyze_shows import ShowsAnalyzer
from src.data_processing.source_analysis import SourceAnalyzer

def main():
    """Run the source type analysis."""
    # Get clean data
    shows_analyzer = ShowsAnalyzer()
    shows_df, _ = shows_analyzer.fetch_data()
    shows_analyzer.clean_data()
    
    # Create and run source analysis
    source_analyzer = SourceAnalyzer(shows_analyzer.shows_df)
    source_analyzer.create_source_visualization()

if __name__ == '__main__':
    main()
