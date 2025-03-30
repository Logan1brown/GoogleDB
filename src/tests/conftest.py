"""
Pytest configuration and shared fixtures
"""
import pytest
import pandas as pd
import os
import json

@pytest.fixture(scope='session')
def test_config():
    """Load test configuration."""
    base_path = os.path.dirname(__file__)
    return {
        'spreadsheet_id': 'test-spreadsheet-id',
        'sheets': {
            'shows': 'test_shows',
            'team': 'test_team'
        },
        'test_data': {
            'sheets_responses': {
                'shows': os.path.join(base_path, 'test_data/sheets_responses/shows_response.json'),
                'team': os.path.join(base_path, 'test_data/sheets_responses/team_response.json')
            },
            'csv_samples': {
                'shows': os.path.join(base_path, 'test_data/csv_samples/shows.csv'),
                'team': os.path.join(base_path, 'test_data/csv_samples/team.csv')
            }
        }
    }

@pytest.fixture(scope='session')
def sample_data_path():
    """Path to test data files."""
    return os.path.join(os.path.dirname(__file__), 'test_data')

@pytest.fixture(autouse=True)
def mock_streamlit():
    """Mock Streamlit for all tests."""
    with pytest.MonkeyPatch.context() as mp:
        # Prevent Streamlit from trying to create a web server
        mp.setenv('STREAMLIT_RUN_TEST', 'true')
        yield
