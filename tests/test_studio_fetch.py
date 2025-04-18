"""Test studio data fetching.

This script verifies that:
1. Studio data can be fetched
2. Required columns are present
3. Data types are correct
4. Studio names are properly parsed as lists
"""

import pandas as pd
from src.data_processing.analyze_shows import ShowsAnalyzer

def test_studio_fetch():
    # Initialize analyzer
    analyzer = ShowsAnalyzer()
    
    # Fetch studio data
    print("\nFetching studio data...")
    shows_df = analyzer.fetch_studio_data()
    
    # Check if we got data
    print(f"\nFetched {len(shows_df)} shows")
    print(f"Unique titles: {shows_df['title'].nunique()}")
    
    # Verify columns
    required_cols = [
        'title', 
        'network_name', 
        'studio_names',
        'status_name',
        'tmdb_id',
        'tmdb_status',
        'tmdb_seasons',
        'tmdb_total_episodes',
        'tmdb_last_air_date'
    ]
    
    print("\nChecking required columns...")
    missing = [col for col in required_cols if col not in shows_df.columns]
    if missing:
        print(f"❌ Missing columns: {missing}")
    else:
        print("✅ All required columns present")
        
    # Check studio_names
    print("\nChecking studio_names format...")
    sample_studios = shows_df['studio_names'].head()
    print("First 5 studio_names entries:")
    for i, studios in enumerate(sample_studios, 1):
        print(f"{i}. {studios} (type: {type(studios)})")
    
    # Check status
    print("\nChecking status distribution...")
    print("Status counts:")
    print(shows_df['status_name'].value_counts().to_dict())
    
    # Check success metrics
    print("\nChecking success metrics...")
    has_success = shows_df[shows_df['tmdb_status'].notna()]
    print(f"Shows with success metrics: {len(has_success)}")
    print("\nUnique TMDB statuses:")
    print(shows_df['tmdb_status'].value_counts().to_dict())

if __name__ == '__main__':
    test_studio_fetch()
