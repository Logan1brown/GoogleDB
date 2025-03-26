"""Google Sheets configuration and environment variable handling."""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SheetsConfig:
    """Configuration for Google Sheets access."""
    
    # Only request the specific scopes we need
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly'  # Read-only access
        # Add .write scope only if needed: 'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
        self.token_file = os.getenv('GOOGLE_SHEETS_TOKEN_FILE')
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        self.shows_sheet = os.getenv('SHOWS_SHEET_NAME', 'Shows')
        self.team_sheet = os.getenv('TEAM_SHEET_NAME', 'Team Members')
        
        # Validate required variables
        self._validate_config()
        
    def _validate_config(self) -> None:
        """Ensure all required configuration is present."""
        missing = []
        
        if not self.credentials_file:
            missing.append('GOOGLE_SHEETS_CREDENTIALS_FILE')
        if not self.token_file:
            missing.append('GOOGLE_SHEETS_TOKEN_FILE')
        if not self.spreadsheet_id:
            missing.append('GOOGLE_SHEETS_SPREADSHEET_ID')
            
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Please check your .env file and ensure all variables are set."
            )
            
    def get_credentials_path(self) -> Path:
        """Get the full path to credentials file.
        
        Returns path relative to project root, not src directory.
        """
        project_root = Path(__file__).parent.parent.parent
        return (project_root / self.credentials_file).resolve()
        
    def get_token_path(self) -> Path:
        """Get the full path to token file.
        
        Returns path relative to project root, not src directory.
        """
        project_root = Path(__file__).parent.parent.parent
        return (project_root / self.token_file).resolve()

# Create a singleton instance
sheets_config = SheetsConfig()
