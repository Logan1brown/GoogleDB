import json
import pandas as pd
from datetime import datetime

def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def map_show_to_sheet_format(show):
    """Map a single show to the sheets format"""
    # Fix network mapping
    network = show['network'][0] if show['network'] else ''
    if network == 'Apple':
        network = 'Apple TV+'
    
    # Merge creators and talent for key_creatives
    creatives = []
    if show.get('creators'):
        creatives.extend(show['creators'])
    if show.get('talent'):
        creatives.extend(show['talent'])
    key_creatives = ', '.join(creatives) if creatives else ''
    
    # Handle genres
    genres = show.get('genres', [])
    main_genre = genres[0] if genres else ''
    subgenres = ', '.join(genres[1:]) if len(genres) > 1 else ''
    
    # Get source type from source_material
    source_material = show.get('source_material', ['Original'])[0]
    
    return {
        'show_name': show['show_name'],
        'key_creatives': key_creatives,
        'network': network,
        'studio': show.get('studio_seller', [''])[0] if show.get('studio_seller') else '',
        'date': show.get('date', ''),
        'genre': main_genre,
        'subgenre': subgenres,
        'episode_count': show.get('episode_count', ''),
        'source_type': source_material,
        'status': '',  # Empty by default
        'order_type': '',  # Empty by default
        'notes': ''
    }

def main():
    # Load data
    data = load_json_data('/Users/loganbrown/Desktop/tv_market_analysis/CascadeProjects/windsurf-project/sample_data/processed/structured_deals.json')
    
    # Take first 5 shows as a test
    test_shows = data['shows'][:5]
    
    # Map shows to sheet format
    sheet_data = [map_show_to_sheet_format(show) for show in test_shows]
    
    # Convert to DataFrame for nice display
    df = pd.DataFrame(sheet_data)
    
    # Print in a format easy to copy to sheets
    print("\nSample data for Google Sheets (tab-separated):")
    print("\t".join(df.columns))
    for _, row in df.iterrows():
        print("\t".join(str(val) for val in row))

if __name__ == "__main__":
    main()
