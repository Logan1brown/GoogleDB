"""Update Google Sheets with TMDB data from CSVs."""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Optional
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from src.dashboard.utils.sheets_client import SheetsClient

def update_tmdb_metrics_sheet(sheets_client: SheetsClient, metrics_df: pd.DataFrame, test_mode: bool = False):
    """Update or create TMDB Success Metrics sheet."""
    # Expected headers for tmdb_success_metrics sheet
    expected_headers = ['TMDB_ID', 'Title', 'tmdb_seasons', 'tmdb_eps', 'tmdb_total_eps',
                       'tmdb_avg_eps', 'tmdb_status', 'tmdb_last_air', 'success_score']
    
    try:
        # Try to get existing sheet
        metrics_sheet = sheets_client.get_worksheet('tmdb_success_metrics')
        print("Found existing TMDB Success Metrics sheet")
    except:
        # Create new sheet if it doesn't exist
        metrics_sheet = sheets_client.create_worksheet(
            'tmdb_success_metrics',
            rows=1000, cols=len(expected_headers)
        )
        print("Created new TMDB Success Metrics sheet")
        
    # Ensure metrics_df has all expected columns in correct order
    metrics_df = metrics_df[expected_headers]
    
    if test_mode:
        print("\nTest Mode - Would update TMDB Metrics sheet with:")
        print(metrics_df)
        return
    
    # Convert numpy types to Python types and handle invalid floats
    def clean_value(val):
        if pd.isna(val) or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
            return ''  # Replace NaN/inf with empty string for better sheet handling
        if isinstance(val, (np.int64, np.int32)):
            return int(val)
        if isinstance(val, (np.float64, np.float32)):
            return float(val)
        return val
    
    # Get current data range
    current_data = metrics_sheet.get_all_values()
    if len(current_data) > 1:  # If there's data beyond headers
        # Clear all rows except headers
        metrics_sheet.batch_clear([f'A2:Z{len(current_data)}'])
    
    # Get existing headers to preserve any formatting
    existing_headers = metrics_sheet.row_values(1)
    if existing_headers != expected_headers:
        # Only update headers if they don't match expected
        metrics_sheet.update('A1', [metrics_df.columns.tolist()])
        time.sleep(1)  # Rate limit
    
    # Clean all values
    cleaned_data = [
        [clean_value(val) for val in row] 
        for row in metrics_df.values.tolist()
    ]
    
    # Update values starting from row 2
    metrics_sheet.update('A2', cleaned_data)
    print("Updated TMDB Success Metrics sheet")

def update_shows_sheet(sheets_client: SheetsClient, updates_df: pd.DataFrame, test_mode: bool = False):
    """Update Shows sheet with TMDB data."""
    shows_sheet = sheets_client.get_worksheet(sheets_client.config.shows_sheet)
    
    # Get all shows data with expected headers
    expected_headers = ['shows', 'key_creatives', 'network', 'studio', 'date', 'genre', 
                      'subgenre', 'episode_count', 'source_type', 'status', 'order_type', 
                      'notes', 'TMDB_ID', 'success_score']
    shows_data = pd.DataFrame(shows_sheet.get_all_records(expected_headers=expected_headers))
    
    if test_mode:
        print("\nTest Mode - Would update Shows sheet for:")
        print(updates_df[['Title', 'TMDB_ID', 'status', 'order_type', 'episode_count', 'success_score', 'notes']])
        return
    
    # Prepare batch updates for shows that have changed
    batch_updates = []
    update_ranges = []
    
    for idx, row in shows_data.iterrows():
        if pd.notna(row.get('TMDB_ID')):
            # Get TMDB updates for this show
            show_updates = updates_df[updates_df['TMDB_ID'] == row['TMDB_ID']]
            if len(show_updates) == 0:
                continue
                
            show_updates = show_updates.iloc[0]
            
            # Check which cells need updating
            for col in ['notes', 'order_type', 'status', 'episode_count']:
                if col in show_updates and show_updates[col] != row.get(col, ''):
                    # Convert numpy types to Python types
                    value = show_updates[col]
                    if pd.isna(value) or (isinstance(value, float) and (np.isnan(value) or np.isinf(value))):
                        value = ''
                    elif isinstance(value, (np.int64, np.int32)):
                        value = int(value)
                    elif isinstance(value, (np.float64, np.float32)):
                        value = float(value)
                    
                    # Get A1 notation for cell
                    col_letter = chr(ord('A') + shows_data.columns.get_loc(col))
                    cell_range = f'{col_letter}{idx + 2}'
                    
                    update_ranges.append(cell_range)
                    batch_updates.append([[value]])
    
    if batch_updates:
        # Do all updates in one batch request
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': [{
                'range': f'{shows_sheet.title}!{cell_range}',
                'values': values
            } for cell_range, values in zip(update_ranges, batch_updates)]
        }
        shows_sheet.spreadsheet.values_batch_update(body)
        print(f"Updated {len(batch_updates)} cells in Shows sheet")
    else:
        print("No cells needed updating in Shows sheet")

def main(test_mode: bool = False, show_id: Optional[int] = None):
    """Update sheets with TMDB data from CSVs."""
    # Initialize sheets client
    sheets_client = SheetsClient()
    
    # Read CSVs from the correct directory
    csv_dir = Path('/Users/loganbrown/Desktop/GoogleDB/docs/sheets/TMDB csv')
    updates_df = pd.read_csv(csv_dir / 'shows_updates.csv')
    
    if show_id is not None:
        # Filter to just one show for testing
        updates_df = updates_df[updates_df['TMDB_ID'] == show_id]
        if len(updates_df) == 0:
            print(f"Error: Show ID {show_id} not found in updates data")
            return
        print(f"\nTesting with show: {updates_df.iloc[0]['Title']} (ID: {show_id})")
    
    # Only update shows sheet since metrics is already done
    # update_tmdb_metrics_sheet(sheets_client, metrics_df, test_mode)
    update_shows_sheet(sheets_client, updates_df, test_mode)
    
    if test_mode:
        print("\nTest complete - no actual updates made")
    else:
        print("\nSheet updates complete!")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Run in test mode (no actual updates)')
    parser.add_argument('--show-id', type=int, help='Test with a specific show ID')
    args = parser.parse_args()
    main(test_mode=args.test, show_id=args.show_id)
