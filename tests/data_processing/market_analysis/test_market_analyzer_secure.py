"""Test module for secure MarketAnalyzer class."""

import os
import logging
from pathlib import Path
import pandas as pd
import pytest
from dotenv import load_dotenv
from supabase import create_client, Client

from src.data_processing.market_analysis.market_analyzer_secure import MarketAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Get authenticated Supabase client."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
    return create_client(url, key)

def test_market_analyzer_with_supabase():
    """Test MarketAnalyzer with real Supabase data."""
    print("\nTesting Secure MarketAnalyzer with Supabase...")
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    # Fetch data from api_market_analysis view
    response = supabase.table('api_market_analysis').select('*').execute()
    market_data = pd.DataFrame(response.data)
    
    print("\nMarket Analysis DataFrame Info:")
    print("=====================")
    print(f"Number of shows: {len(market_data)}")
    print(f"Columns: {market_data.columns.tolist()}")
    
    print("\nSample of first 5 shows:")
    sample_cols = ['shows', 'network', 'studio', 'status_name']
    print(market_data[sample_cols].head().to_string())
    
    # Initialize analyzer
    analyzer = MarketAnalyzer(market_data)
    
    # Test network distribution
    network_dist = analyzer.get_network_distribution()
    print("\nTop 5 Networks by Show Count:")
    print(network_dist.head().to_string())
    assert len(network_dist) > 0, "Should have network distribution"
    
    # Test success by network
    network_success = analyzer.get_success_by_network()
    print("\nTop 5 Networks by Success Score:")
    print(network_success.head().to_string())
    assert len(network_success) > 0, "Should have success scores"
    
    # Test market insights
    insights = analyzer.generate_market_insights()
    print("\nMarket Insights:")
    print("===============")
    print(f"Total Shows: {insights['total_shows']}")
    print(f"Total Networks: {insights['total_networks']}")
    print(f"Network Concentration: {insights['network_concentration']:.1f}%")
    print(f"Vertical Integration: {insights['vertical_integration']:.1f}%")
    print(f"\nTop 3 Networks:")
    for network in insights['top_networks']:
        print(f"- {network}")
    
    # Test team data
    if all(col in market_data.columns for col in ['writers', 'producers', 'directors', 'creators']):
        print("\nTeam Data Example:")
        print("=================")
        sample_show = market_data.iloc[0]
        print(f"Show: {sample_show['shows']}")
        print(f"Writers: {sample_show['writers']}")
        print(f"Producers: {sample_show['producers']}")
        print(f"Directors: {sample_show['directors']}")
        print(f"Creators: {sample_show['creators']}")
    
    print("\nTest succeeded")

if __name__ == '__main__':
    test_market_analyzer_with_supabase()
