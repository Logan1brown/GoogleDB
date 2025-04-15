"""
Analytics service for read-only data access.
Uses anon key with read-only permissions for better security separation.
"""

from typing import Dict, List
import streamlit as st
from supabase.client import create_client, Client
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize Supabase client with anon key for secure views
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')  # Use anon key for secure views

if not url or not key:
    raise ValueError("Missing Supabase credentials. Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set in .env")

supabase: Client = create_client(url, key)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_show_stats(network: str = None, genre: str = None) -> pd.DataFrame:
    """Get show statistics with optional filtering using secure market analysis view."""
    query = supabase.table('api_market_analysis').select('*')
    
    # Apply filters
    if network:
        query = query.eq('network_name', network)
    if genre:
        query = query.eq('genre', genre)
    
    # Execute query
    result = query.execute()
    
    # Convert to DataFrame
    df = pd.DataFrame(result.data)
    return df

@st.cache_data(ttl=3600)
def get_team_stats() -> pd.DataFrame:
    """Get team member statistics across shows using secure market analysis view."""
    # Get all shows with team data
    result = supabase.table('api_market_analysis').select('*').execute()
    df = pd.DataFrame(result.data)
    
    # Process team data
    team_data = []
    for _, row in df.iterrows():
        for role in ['writers', 'producers', 'directors', 'creators']:
            if pd.notna(row[role]) and row[role]:
                for member in row[role]:
                    team_data.append({'name': member, 'show': row['title']})
    
    # Convert to DataFrame and count shows per team member
    team_df = pd.DataFrame(team_data)
    stats = team_df.groupby('name').size().reset_index(name='show_count')
    return stats

@st.cache_data(ttl=3600)
def get_network_performance() -> pd.DataFrame:
    """Get network performance metrics using secure market analysis view."""
    result = supabase.table('api_market_analysis').select('*').execute()
    df = pd.DataFrame(result.data)
    
    # Aggregate network stats
    network_stats = df.groupby('network').agg({
        'title': 'count',
        'success_score': 'mean'
    }).reset_index()
    
    return network_stats

@st.cache_data(ttl=3600)
def get_paginated_shows(page: int = 0, page_size: int = 50, 
                       network: str = None, genre: str = None) -> Dict:
    """Get paginated show data with optional filters using secure market analysis view."""
    # Calculate offset
    offset = page * page_size
    
    # Build query
    query = supabase.table('api_market_analysis')\
        .select('*')\
        .range(offset, offset + page_size - 1)
    
    # Apply filters
    if network:
        query = query.eq('network_name', network)
    if genre:
        query = query.eq('genre', genre)
    
    # Get total count for pagination
    count_query = supabase.table('api_market_analysis')\
        .select('tmdb_id', count='exact')
    
    if network:
        count_query = count_query.eq('network_name', network)
    if genre:
        count_query = count_query.eq('genre_name', genre)
    
    # Execute queries
    result = query.execute()
    count_result = count_query.execute()
    
    return {
        'data': result.data,
        'total': count_result.count if count_result.count else 0,
        'page': page,
        'page_size': page_size
    }
