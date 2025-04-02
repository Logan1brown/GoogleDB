"""Update Google Sheets with TMDB data from CSVs."""
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from src.dashboard.utils.sheets_client import SheetsClient

def update_tmdb_metrics_sheet(sheets_client: SheetsClient, metrics_df: pd.DataFrame):
    """Update or create TMDB Success Metrics sheet."""
    try:
        # Try to get existing sheet
        metrics_sheet = sheets_client.get_worksheet('tmdb_success_metrics')
        print("Found existing TMDB Success Metrics sheet")
    except:
        # Create new sheet if it doesn't exist
        metrics_sheet = sheets_client.create_worksheet(
            'tmdb_success_metrics',
            rows=1000, cols=20
        )
        print("Created new TMDB Success Metrics sheet")
    
    # Clear existing data
    metrics_sheet.clear()
    
    # Update with new data
    metrics_sheet.update([metrics_df.columns.values.tolist()] + metrics_df.values.tolist())
    print("Updated TMDB Success Metrics sheet")

def update_shows_sheet(sheets_client: SheetsClient, updates_df: pd.DataFrame):
    """Update Shows sheet with TMDB data."""
    shows_sheet = sheets_client.get_worksheet(sheets_client.config.shows_sheet)
    
    # Get all shows data
    shows_data = pd.DataFrame(shows_sheet.get_all_records())
    
    # Update each show that has TMDB data
    rows_updated = 0
    for idx, row in shows_data.iterrows():
        if pd.notna(row.get('TMDB_ID')):
            # Get TMDB updates for this show
            tmdb_updates = updates_df[updates_df['TMDB_ID'] == row['TMDB_ID']].iloc[0]
            
            # Update cells that have changed
            for col in ['notes', 'order_type', 'status', 'episode_count']:
                if tmdb_updates[col] != row[col]:
                    shows_sheet.update_cell(idx + 2, shows_data.columns.get_loc(col) + 1, tmdb_updates[col])
                    rows_updated += 1
    
    print(f"Updated {rows_updated} cells in Shows sheet")

def main():
    """Update sheets with TMDB data from CSVs."""
    # Initialize sheets client
    sheets_client = SheetsClient()
    
    # Read CSVs
    csv_dir = project_root / 'docs' / 'sheets'
    metrics_df = pd.read_csv(csv_dir / 'tmdb_success_metrics.csv')
    updates_df = pd.read_csv(csv_dir / 'shows_tmdb_updates.csv')
    
    # Update sheets
    update_tmdb_metrics_sheet(sheets_client, metrics_df)
    update_shows_sheet(sheets_client, updates_df)
    
    print("Sheet updates complete!")

if __name__ == '__main__':
    main()
