"""Test the analytics service functions."""
import analytics_service as analytics

def test_materialized_views():
    print("\nTesting materialized views:")
    
    # Test show_details view
    result = analytics.supabase.table('show_details').select('*').limit(5).execute()
    print("\nshow_details sample:")
    print(f"Fields: {', '.join(result.data[0].keys()) if result.data else 'No data'}")
    print(f"Row count: {len(result.data)}")
    
    # Test network_stats view
    result = analytics.supabase.table('network_stats').select('*').execute()
    print("\nnetwork_stats sample:")
    print(f"Fields: {', '.join(result.data[0].keys()) if result.data else 'No data'}")
    print(f"Row count: {len(result.data)}")
    
    # Test team_summary view
    result = analytics.supabase.table('team_summary').select('*').limit(5).execute()
    print("\nteam_summary sample:")
    print(f"Fields: {', '.join(result.data[0].keys()) if result.data else 'No data'}")
    print(f"Row count: {len(result.data)}")

def test_show_stats():
    test_materialized_views()
    df = analytics.get_show_stats()
    print("\nTesting show stats:")
    print("Total shows:", len(df))
    print("\nNetwork distribution:")
    print(df.groupby('network_name').size().head())
    print("\nGenre distribution:")
    print(df.groupby('genre_name').size().head())

def test_team_stats():
    print("\nTesting team stats:")
    df = analytics.get_team_stats()
    print(f"Total team entries: {len(df)}")
    print("\nSample team members and roles:")
    print(df.head())

def test_network_performance():
    print("\nTesting network performance:")
    df = analytics.get_network_performance()
    print("\nNetwork show counts:")
    print(df.sort_values('total_shows', ascending=False).head())

def test_pagination():
    print("\nTesting pagination:")
    
    # Get first page
    page1 = analytics.get_paginated_shows(page=0, page_size=2)
    print("\nFirst page (2 shows):")
    for _, show in page1.iterrows():
        print(f"- {show['title']} ({show['network_name']})")
    
    # Get second page
    page2 = analytics.get_paginated_shows(page=1, page_size=2)
    print("\nSecond page (2 shows):")
    for _, show in page2.iterrows():
        print(f"- {show['title']} ({show['network_name']})")

if __name__ == "__main__":
    print("Testing Analytics Service...")
    test_show_stats()
    test_team_stats()
    test_network_performance()
    test_pagination()
