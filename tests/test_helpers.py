import pytest
import time
from helpers import TestUser, generate_test_show, TemporaryTestData, supabase

def test_user_impersonation():
    """Test creating and using a test user"""
    # Create test admin
    admin = TestUser(role='admin')
    admin_id = admin.create()
    
    try:
        assert admin_id is not None, "Admin user should be created"
        
        # Test user creation worked
        response = supabase.auth.admin.list_users()
        assert any(user.id == admin_id for user in response)
        
    finally:
        admin.delete()

def test_show_generation():
    """Test generating and inserting test shows"""
    timestamp = int(time.time())
    test_shows = [
        generate_test_show(title=f'Test Show 1 {timestamp}', network_id=15),  # HBO
        generate_test_show(title=f'Test Show 2 {timestamp}', network_id=1)   # Netflix
    ]
    
    titles = [f'Test Show 1 {timestamp}', f'Test Show 2 {timestamp}']
    with TemporaryTestData('shows', test_shows, {'titles': titles}) as shows:
        assert len(shows) == 2
        
        # Verify shows were inserted
        response = supabase.table('shows')\
            .select('title, network_id')\
            .in_('title', [f'Test Show 1 {timestamp}', f'Test Show 2 {timestamp}'])\
            .execute()
            
        assert len(response.data) == 2, f"Expected 2 test shows, got {len(response.data)}: {response.data}"
        assert any(show['title'] == f'Test Show 1 {timestamp}' for show in response.data)
        assert any(show['title'] == f'Test Show 2 {timestamp}' for show in response.data)
    
    # Verify cleanup worked
    response = supabase.table('shows')\
        .select('*')\
        .in_('title', [f'Test Show 1 {timestamp}', f'Test Show 2 {timestamp}'])\
        .execute()

    assert len(response.data) == 0, "Test data should be cleaned up"
