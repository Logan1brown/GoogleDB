"""Test studio analyzer functionality.

This script verifies that:
1. Studio relationships are correctly analyzed
2. Active shows are properly filtered when column is present
3. Success metrics are calculated correctly
4. Studio insights are accurate
"""

import pandas as pd
import pytest
from src.data_processing.studio_performance.studio_analyzer import (
    analyze_studio_relationships,
    get_studio_insights,
    get_all_studios,
    get_shows_for_studio
)

def create_test_data(with_active: bool = False) -> pd.DataFrame:
    """Create test data for studio analysis."""
    data = {
        'title': ['Show1', 'Show2', 'Show3', 'Show4', 'Show5'],
        'network_name': ['Net1', 'Net1', 'Net2', 'Net2', 'Net3'],
        'studio_names': [
            ['Studio1'], 
            ['Studio1', 'Studio2'],
            ['Studio2'],
            ['Studio3'],
            ['Studio1', 'Studio3']
        ],
        'status_name': ['Ended', 'Running', 'Running', 'Ended', 'Running'],
        'tmdb_seasons': [2, 3, 1, 4, 2],
        'tmdb_total_episodes': [20, 30, 10, 40, 20]
    }
    
    if with_active:
        data['active'] = [False, True, True, False, True]
        
    return pd.DataFrame(data)

def test_analyze_studio_relationships_without_active():
    """Test studio analysis without active column."""
    df = create_test_data(with_active=False)
    result = analyze_studio_relationships(df)
    
    # Check studio sizes
    assert len(result['studio_sizes']) == 3  # Studio1, Studio2, Studio3
    assert result['studio_sizes']['Studio1'] == 3  # Show1, Show2, Show5
    
    # Check network relationships
    assert 'Net1' in result['network_relationships']['Studio1']
    assert 'Net3' in result['network_relationships']['Studio3']
    
    # Check success metrics
    studio1_success = result['studio_success']['Studio1']
    assert studio1_success['total_shows'] == 3
    assert 'active_shows' not in studio1_success  # No active column
    assert studio1_success['avg_seasons'] == (2 + 3 + 2) / 3

def test_analyze_studio_relationships_with_active():
    """Test studio analysis with active column."""
    df = create_test_data(with_active=True)
    result = analyze_studio_relationships(df)
    
    # Should only count active shows, each studio gets credit for co-produced shows
    assert result['studio_sizes']['Studio1'] == 2  # Show2, Show5 (Show1 inactive)
    assert result['studio_sizes']['Studio2'] == 2  # Show2, Show3 (each studio gets credit)
    assert result['studio_sizes']['Studio3'] == 1  # Show5
    
    # Check success metrics with active shows
    studio1_success = result['studio_success']['Studio1']
    assert studio1_success['total_shows'] == 2  # Only active shows
    assert studio1_success['active_shows'] == 2
    assert studio1_success['active_percentage'] == 100.0

def test_get_studio_insights_without_active():
    """Test studio insights without active column."""
    df = create_test_data(with_active=False)
    result = get_studio_insights(df, 'Studio1')
    
    assert len(result['network_partners']) == 2  # Net1, Net3
    assert len(result['show_details']) == 3  # Show1, Show2, Show5
    assert result['success_metrics']['total_shows'] == 3
    assert 'active_shows' not in result['success_metrics']

def test_get_studio_insights_with_active():
    """Test studio insights with active column."""
    df = create_test_data(with_active=True)
    result = get_studio_insights(df, 'Studio1')
    
    assert len(result['network_partners']) == 2  # Net1, Net3
    assert len(result['show_details']) == 2  # Only Show2, Show5 (active)
    assert result['success_metrics']['total_shows'] == 2
    assert result['success_metrics']['active_shows'] == 2
    assert result['success_metrics']['active_percentage'] == 100.0

def test_get_shows_for_studio():
    """Test getting shows for a specific studio."""
    df = create_test_data()
    shows = get_shows_for_studio(df, 'Studio2')
    
    assert len(shows) == 2  # Show2, Show3
    assert all(shows['title'].isin(['Show2', 'Show3']))

def test_get_all_studios():
    """Test getting all studios and their show counts."""
    df = create_test_data()
    studio_sizes = get_all_studios(df)
    
    assert len(studio_sizes) == 3  # Studio1, Studio2, Studio3
    assert studio_sizes['Studio1'] == 3  # Show1, Show2, Show5
    assert studio_sizes['Studio2'] == 2  # Show2, Show3
    assert studio_sizes['Studio3'] == 2  # Show4, Show5
