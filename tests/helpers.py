from supabase import create_client
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
import uuid

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')  # Using service key for admin access
)

class TestUser:
    """Helper class to manage test users and impersonation"""
    def __init__(self, email: str = None, role: str = 'authenticated', password: str = None):
        self.email = email or f'test_{uuid.uuid4()}@example.com'
        self.password = password or 'test123'
        self.role = role
        self._user_id = None
    
    def create(self) -> str:
        """Create a test user and return their ID"""
        # Create user in auth.users with role in metadata
        response = supabase.auth.admin.create_user({
            'email': self.email,
            'password': self.password,
            'email_confirm': True,
            'user_metadata': {
                'role': self.role
            }
        })
        self._user_id = response.user.id
        return self._user_id
    
    def delete(self):
        """Clean up the test user"""
        if self._user_id:
            supabase.auth.admin.delete_user(self._user_id)

def generate_test_show(
    title: str = None,
    network_id: int = None,
    overrides: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate test show data"""
    show_data = {
        'title': title or f'Test Show {uuid.uuid4()}',
        'network_id': network_id or 1,  # Default to first network
        'status_id': 1,  # Default to first status
        'studio_id': 1,  # Default to first studio
        'source_type_id': 1,
        'order_type_id': 1,
        'active': True,
        'date': '2025-01-01'
    }
    
    if overrides:
        show_data.update(overrides)
    
    return show_data

def insert_test_shows(shows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Insert multiple test shows and return their IDs"""
    response = supabase.table('shows').insert(shows).execute()
    return response.data

def cleanup_test_data(table: str, condition: Dict[str, Any]):
    """Clean up test data from a table based on a condition"""
    # First clean up any dependent tables
    if table == 'shows':
        # Get shows to delete
        titles = condition.get('titles', [condition.get('title')] if condition.get('title') else [])
        shows = supabase.table('shows')\
            .select('title, tmdb_id')\
            .in_('title', titles)\
            .execute()
        if shows.data:
            titles = [show['title'] for show in shows.data]
            tmdb_ids = [show['tmdb_id'] for show in shows.data if show['tmdb_id']]
            
            # Delete from show_team first
            if titles:
                supabase.table('show_team')\
                    .delete()\
                    .in_('title', titles)\
                    .execute()
            
            # Delete from tmdb_success_metrics
            if tmdb_ids:
                supabase.table('tmdb_success_metrics')\
                    .delete()\
                    .in_('tmdb_id', tmdb_ids)\
                    .execute()
    
    # Now delete from main table
    if table == 'shows' and 'titles' in condition:
        # For shows table, use in_ for titles
        supabase.table(table).delete().in_('title', condition['titles']).execute()
    elif table == 'shows' and 'title' in condition:
        # Single title
        supabase.table(table).delete().in_('title', [condition['title']]).execute()
    else:
        # For other tables, use match
        supabase.table(table).delete().match(condition).execute()

# Context manager for temporary test data
class TemporaryTestData:
    def __init__(self, table: str, data: List[Dict[str, Any]], condition: Dict[str, Any]):
        self.table = table
        self.data = data
        self.condition = condition
        self.inserted_data = None
    
    def __enter__(self):
        self.inserted_data = insert_test_shows(self.data)
        return self.inserted_data
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        cleanup_test_data(self.table, self.condition)

# Example usage:
'''
async def test_show_creation():
    # Create a test admin user
    admin = TestUser(role='admin')
    admin_id = await admin.create()
    
    try:
        # Generate and insert test data
        test_shows = [
            generate_test_show(title='Test Show 1'),
            generate_test_show(title='Test Show 2')
        ]
        
        async with TemporaryTestData('shows', test_shows, {'created_by': 'test_user'}) as shows:
            # Run your tests here
            assert len(shows) == 2
            
    finally:
        # Clean up
        await admin.delete()
'''
