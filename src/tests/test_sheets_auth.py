"""Test Google Sheets authentication with minimal permissions."""
import os
from pathlib import Path
import gspread
from config.sheets_config import SheetsConfig

def test_sheets_connection():
    """Test we can connect with read-only access."""
    config = SheetsConfig()
    
    try:
        # Initialize the client
        client = gspread.service_account(
            filename=config.get_credentials_path(),
            scopes=config.SCOPES
        )
        
        # Try to open spreadsheet (will fail if permissions wrong)
        sheet = client.open_by_key(config.spreadsheet_id)
        
        # Just get the sheet titles (minimal data access)
        sheet_titles = [ws.title for ws in sheet.worksheets()]
        
        print(f"\nSuccessfully connected! Available sheets: {sheet_titles}")
        return True
        
    except gspread.exceptions.APIError as e:
        if "insufficient permission" in str(e).lower():
            print("\nPermission error - check that:")
            print("1. You shared the sheet with the service account email")
            print("2. The credentials.json is for the correct project")
        else:
            print(f"\nAPI Error: {e}")
        return False
        
    except FileNotFoundError:
        print("\nCredentials file not found - check that:")
        print("1. You downloaded credentials.json")
        print("2. You moved it to the config directory")
        return False

if __name__ == "__main__":
    # Simple command line test
    success = test_sheets_connection()
    exit(0 if success else 1)
