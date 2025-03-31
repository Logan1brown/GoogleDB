"""Script to test TMDB API functionality."""
from dotenv import load_dotenv
from src.data_processing.external.tmdb.tmdb_client import TMDBClient

# Load environment variables
load_dotenv()

def main():
    # Initialize client
    client = TMDBClient()
    
    # Test search
    print("\nSearching for 'The Last of Us'...")
    shows = client.search_tv_show("The Last of Us")
    for show in shows[:3]:  # Show top 3 results
        print(f"- {show.name} ({show.first_air_date.year if show.first_air_date else 'N/A'})")
        print(f"  ID: {show.id}")
        print(f"  Overview: {show.overview[:100]}...")
    
    # Test show details
    print("\nGetting details for The Last of Us...")
    details = client.get_tv_show_details(100088)  # The Last of Us ID
    print(f"Title: {details.name}")
    print(f"First Aired: {details.first_air_date}")
    print(f"Status: {details.status}")
    print(f"Seasons: {details.number_of_seasons}")
    print(f"Genres: {', '.join(g.name for g in details.genres)}")
    
    # Test genre list
    print("\nGetting all TV genres...")
    genres = client.get_genre_list()
    print("Available genres:")
    for genre in genres:
        print(f"- {genre.name} (ID: {genre.id})")
        
    # Test credits
    print("\nGetting credits for The Last of Us...")
    credits = client.get_tv_show_credits(100088)
    
    # Show all unique job titles
    print("\nUnique Job Titles in Crew:")
    job_titles = sorted(set(p['job'] for p in credits.get('crew', [])))
    for job in job_titles:
        count = sum(1 for p in credits['crew'] if p['job'] == job)
        print(f"- {job} ({count} people)")
    
    print("\nSample Crew Members by Role:")
    key_roles = ['Creator', 'Executive Producer', 'Writer', 'Director']
    for role in key_roles:
        crew = [p for p in credits.get('crew', []) if p['job'] == role]
        if crew:
            print(f"\n{role}s:")
            for person in crew[:3]:  # Show up to 3 per role
                print(f"- {person['name']}")    

if __name__ == "__main__":
    main()
