"""Robust Google Sheets client with retries and error handling."""
import time
from functools import wraps
from typing import Any, Callable

import gspread
from gspread.exceptions import APIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.config.logging_config import setup_logging
from src.config.sheets_config import SheetsConfig

logger = setup_logging(__name__)

def rate_limit(max_per_minute: int = 60):
    """Decorator to rate limit API calls."""
    min_interval = 60.0 / max_per_minute
    last_call = [0.0]  # List to allow modification in closure
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            now = time.time()
            elapsed = now - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_call[0] = time.time()
            return result
        return wrapper
    return decorator

class SheetsClient:
    """Wrapper around gspread with better error handling."""
    
    def __init__(self):
        """Initialize the client with config."""
        self.config = SheetsConfig()
        self.client = self._get_client()
        self.spreadsheet = None
        
    def _get_client(self) -> gspread.Client:
        """Get authenticated gspread client."""
        try:
            return gspread.service_account(
                filename=self.config.get_credentials_path(),
                scopes=self.config.SCOPES
            )
        except Exception as e:
            logger.error(f"Failed to initialize sheets client: {e}")
            raise
    
    @retry(
        retry=retry_if_exception_type(APIError),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3)
    )
    @rate_limit(max_per_minute=50)  # Stay well under the 60/min limit
    def get_worksheet(self, name: str) -> gspread.Worksheet:
        """Get worksheet by name with retries."""
        try:
            if not self.spreadsheet:
                self.spreadsheet = self.client.open_by_key(
                    self.config.spreadsheet_id
                )
            worksheet = self.spreadsheet.worksheet(name)
            logger.debug(f"Successfully accessed worksheet: {name}")
            return worksheet
        except APIError as e:
            logger.error(f"API error accessing worksheet {name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error accessing worksheet {name}: {e}")
            raise
    
    @retry(
        retry=retry_if_exception_type(APIError),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3)
    )
    @rate_limit(max_per_minute=50)
    def get_all_values(self, worksheet_name: str) -> list[list]:
        """Get all values from a worksheet with retries."""
        try:
            worksheet = self.get_worksheet(worksheet_name)
            data = worksheet.get_all_values()
            logger.debug(f"Retrieved {len(data)} rows from {worksheet_name}")
            return data
        except Exception as e:
            logger.error(f"Failed to get values from {worksheet_name}: {e}")
            raise
    
    def get_shows_data(self) -> list[list]:
        """Get shows data with proper error handling."""
        try:
            return self.get_all_values(self.config.shows_sheet)
        except Exception as e:
            logger.error(f"Failed to get shows data: {e}")
            raise
    
    def get_team_data(self) -> list[list]:
        """Get team data with proper error handling."""
        try:
            return self.get_all_values(self.config.team_sheet)
        except Exception as e:
            logger.error(f"Failed to get team data: {e}")
            raise

# Create singleton instance
sheets_client = SheetsClient()
