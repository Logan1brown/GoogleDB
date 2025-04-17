"""Convert tmdb_matches.csv to shows_with_tmdb.csv format."""
import pandas as pd
from pathlib import Path

def convert_matches():
    """Convert tmdb_matches.csv to shows_with_tmdb.csv format."""
    base_path = Path("/Users/loganbrown/Desktop/GoogleDB/docs/sheets")
    matches_path = base_path / "tmdb_matches.csv"
    output_path = base_path / "shows_with_tmdb.csv"
    
    # Load matches
    matches_df = pd.read_csv(matches_path)
    
    # Get validated shows with TMDB IDs
    validated_df = matches_df[matches_df['validated'] == True].copy()
    
    # Create new dataframe with sheet format
    sheet_df = pd.DataFrame()
    sheet_df['shows'] = validated_df['show_name']
    sheet_df['tmdb_id'] = validated_df['tmdb_id']
    
    # Split TMDB genres into primary and secondary
    def split_genres(genres_str):
        if pd.isna(genres_str):
            return '', ''
        genres = genres_str.split(',')
        primary = genres[0].strip() if genres else ''
        secondary = ','.join(g.strip() for g in genres[1:]) if len(genres) > 1 else ''
        return primary, secondary
    
    # Apply the split to each row
    genres_split = validated_df['tmdb_genres'].apply(split_genres)
    sheet_df['genre'] = genres_split.apply(lambda x: x[0])
    sheet_df['subgenre'] = genres_split.apply(lambda x: x[1])
    
    # Fill other required columns with empty strings
    required_cols = [
        'key_creatives', 'network', 'studio', 'date', 'episode_count',
        'source_type', 'status', 'order_type', 'notes'
    ]
    for col in required_cols:
        sheet_df[col] = ''
    
    # Save to CSV
    sheet_df.to_csv(output_path, index=False)
    print(f"Converted {len(validated_df)} validated matches to {output_path}")

if __name__ == "__main__":
    convert_matches()
