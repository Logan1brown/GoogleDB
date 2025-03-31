"""Update live Google Sheet with TMDB data."""
import pandas as pd
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from src.dashboard.utils.sheets_client import SheetsClient
from src.config.logging_config import setup_logging

logger = setup_logging(__name__)

def update_shows_with_tmdb():
    """Update the live shows sheet with TMDB data."""
    # Load our local CSV with TMDB matches
    base_path = Path("/Users/loganbrown/Desktop/GoogleDB/docs/sheets")
    shows_tmdb_path = base_path / "shows_with_tmdb.csv"
    shows_tmdb_df = pd.read_csv(shows_tmdb_path)
    
    # Get validated shows (ones with TMDB IDs)
    validated_shows = shows_tmdb_df[shows_tmdb_df['tmdb_id'].notna()].copy()
    
    # Initialize sheets client
    client = SheetsClient()
    worksheet = client.get_worksheet(client.config.shows_sheet)
    
    # Get current headers and add TMDB_ID if not present
    headers = worksheet.row_values(1)
    if 'TMDB_ID' not in headers:
        next_col = len(headers) + 1
        worksheet.update_cell(1, next_col, 'TMDB_ID')
        headers.append('TMDB_ID')
    
    # Get all values including headers
    all_values = worksheet.get_all_values()
    headers = all_values[0]
    
    # Convert to list of dicts
    all_data = []
    for row in all_values[1:]:
        row_dict = {}
        for i, value in enumerate(row):
            if i < len(headers):
                row_dict[headers[i]] = value
        all_data.append(row_dict)
    
    # Track what we'll update
    updates = []
    tmdb_col = headers.index('TMDB_ID') + 1  # 1-based index for gspread
    genre_col = headers.index('genre') + 1
    subgenre_col = headers.index('subgenre') + 1
    
    # Update each validated show
    for i, row in enumerate(all_data, start=2):  # start=2 to skip header
        show_name = row['shows']
        tmdb_match = validated_shows[validated_shows['shows'] == show_name]
        
        if not tmdb_match.empty:
            tmdb_data = tmdb_match.iloc[0]
            # Only update if we have valid data
            if pd.notna(tmdb_data['tmdb_id']):
                updates.extend([
                    {'range': f'R{i}C{tmdb_col}', 'values': [[str(int(tmdb_data['tmdb_id']))]]},
                    {'range': f'R{i}C{genre_col}', 'values': [[str(tmdb_data['genre']) if pd.notna(tmdb_data['genre']) else '']]},
                    {'range': f'R{i}C{subgenre_col}', 'values': [[str(tmdb_data['subgenre']) if pd.notna(tmdb_data['subgenre']) else '']]}
                ])
    
    # Batch update all changes
    if updates:
        worksheet.batch_update(updates)
        logger.info(f"Updated {len(validated_shows)} shows with TMDB information")
    else:
        logger.warning("No shows to update")

if __name__ == "__main__":
    update_shows_with_tmdb()
