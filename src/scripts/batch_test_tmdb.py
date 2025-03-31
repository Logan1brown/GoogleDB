"""Script to test batch processing with TMDB API."""
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from src.data_processing.external.tmdb.tmdb_client import TMDBClient

def load_shows(csv_path: str, limit: int = 5) -> List[Dict]:
    """Load shows from CSV file.
    
    Args:
        csv_path: Path to CSV file
        limit: Maximum number of shows to load
    """
    shows = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            shows.append(row)
    return shows

def search_show(client: TMDBClient, title: str) -> Tuple[bool, Optional[Dict], List[Dict]]:
    """Search for a show and determine if it's a good match.
    
    Returns:
        Tuple of (match_found, best_match, all_results)
    """
    results = client.search_tv_show(title)
    if not results:
        return False, None, []
        
    # For now, consider the first result if title matches exactly
    best_match = results[0]
    exact_match = best_match.name.lower() == title.lower()
    
    return exact_match, best_match, results

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize client
    client = TMDBClient()
    
    # Load shows from CSV
    csv_path = Path(__file__).parent.parent.parent / "docs/sheets/STS Sales Database - shows.csv"
    shows = load_shows(csv_path)
    
    print(f"\nProcessing {len(shows)} shows...")
    print("-" * 50)
    
    for show in shows:
        title = show['shows']  # Column name in CSV
        print(f"\nProcessing: {title}")
        
        # Search TMDB
        found, match, results = search_show(client, title)
        
        if not found:
            print("❌ No exact match found")
            if results:
                print("Possible matches:")
                for r in results[:3]:
                    print(f"- {r.name} ({r.first_air_date.year if r.first_air_date else 'N/A'})")
            continue
            
        # Get full details for matched show
        details = client.get_tv_show_details(match.id)
        
        print("✅ Found exact match:")
        print(f"Title: {details.name}")
        print(f"First Aired: {details.first_air_date}")
        print(f"Status: {details.status}")
        print(f"Seasons: {details.number_of_seasons}")
        print(f"Genres: {', '.join(g.name for g in details.genres)}")
        
        # Compare with our data
        our_date = show.get('date', '')
        if our_date:
            our_year = datetime.strptime(our_date, '%Y-%m-%d').year
            tmdb_year = details.first_air_date.year if details.first_air_date else None
            if tmdb_year and our_year != tmdb_year:
                print(f"⚠️ Year mismatch: Ours={our_year}, TMDB={tmdb_year}")
        
        our_genre = show.get('genre', '')
        if our_genre and not any(g.name.lower() == our_genre.lower() for g in details.genres):
            print(f"⚠️ Genre mismatch: Ours={our_genre}, TMDB={[g.name for g in details.genres]}")

if __name__ == "__main__":
    main()
