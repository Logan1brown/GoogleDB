"""Test environment and configuration setup."""
import os
import pytest
from config.sheets_config import SheetsConfig

def test_env_loaded():
    """Test that environment variables are loaded."""
    assert 'PYTHON' in os.environ, "PYTHON not in environment"
    assert 'PYTHONPATH' in os.environ, "PYTHONPATH not in environment"
    assert os.environ.get('VENV_PATH') == './venv', "VENV_PATH incorrect"

def test_sheets_config_validation():
    """Test that SheetsConfig validates required variables."""
    # Should raise error if required vars missing
    with pytest.raises(ValueError) as exc_info:
        # Temporarily unset a required var
        original = os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID')
        os.environ['GOOGLE_SHEETS_SPREADSHEET_ID'] = ''
        SheetsConfig()
        # Restore the variable
        if original:
            os.environ['GOOGLE_SHEETS_SPREADSHEET_ID'] = original
    
    assert "Missing required environment variables" in str(exc_info.value)

def test_sheets_config_paths():
    """Test that config paths are resolved correctly."""
    # Set test values directly
    os.environ['GOOGLE_SHEETS_CREDENTIALS_FILE'] = 'config/credentials.json'
    os.environ['GOOGLE_SHEETS_TOKEN_FILE'] = 'config/token.json'
    os.environ['GOOGLE_SHEETS_SPREADSHEET_ID'] = '1234567890abcdef'
    
    config = SheetsConfig()
    assert config.get_credentials_path().name == 'credentials.json'
    assert config.get_token_path().name == 'token.json'
