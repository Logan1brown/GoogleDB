"""
Data entry services for interacting with Supabase.
"""

from typing import Dict, List
from datetime import datetime
import streamlit as st
from supabase.client import create_client, Client
import difflib
import time

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(url, key)

@st.cache_data(ttl=3600)
def load_lookup_data() -> Dict[str, List[Dict]]:
    """Load all lookup data needed for the forms"""
    lookups = {}
    
    # Load networks
    response = supabase.table('network_list').select('id, network').execute()
    lookups['networks'] = [{'id': n['id'], 'name': n['network']} for n in response.data]
    
    # Load studios
    response = supabase.table('studio_list').select('id, studio, type').execute()
    lookups['studios'] = [{'id': s['id'], 'name': s['studio'], 'type': s['type']} for s in response.data]
    
    # Load genres
    response = supabase.table('genre_list').select('id, genre').execute()
    lookups['genres'] = [{'id': g['id'], 'name': g['genre']} for g in response.data]
    
    # Load subgenres
    response = supabase.table('subgenre_list').select('id, subgenre').execute()
    lookups['subgenres'] = [{'id': s['id'], 'name': s['subgenre']} for s in response.data]
    
    # Load role types
    response = supabase.table('role_types').select('id, role, active').execute()
    lookups['role_types'] = [{'id': r['id'], 'name': r['role']} for r in response.data]
    
    # Load source types
    response = supabase.table('source_types').select('id, type').execute()
    lookups['source_types'] = [{'id': s['id'], 'name': s['type']} for s in response.data]
    
    # Load order types
    response = supabase.table('order_types').select('id, type').execute()
    lookups['order_types'] = [{'id': o['id'], 'name': o['type']} for o in response.data]
    
    # Load status types
    response = supabase.table('status_types').select('id, status').execute()
    lookups['status_types'] = [{'id': s['id'], 'name': s['status']} for s in response.data]
    
    return lookups

def search_shows(title: str) -> List[str]:
    """Search for shows by title using fuzzy matching"""
    if not title or len(title.strip()) < 3:
        return []

    # Get all existing shows from shows table
    response = supabase.table('shows').select('title').eq('active', True).execute()
    existing_shows = [show['title'] for show in response.data]

    # Find fuzzy matches
    matches = difflib.get_close_matches(title.lower(), [s.lower() for s in existing_shows], n=5, cutoff=0.6)
    
    # Return original case versions of matches
    return [next(s for s in existing_shows if s.lower() == m) for m in matches]

def load_show(title: str, lookups: Dict[str, List[Dict]] = None) -> dict:
    """Load show data for editing"""
    # Get lookups if not provided
    if lookups is None:
        lookups = load_lookup_data()
    """Load show data for editing"""
    # Get show details
    response = supabase.table('shows') \
        .select('*') \
        .eq('title', title) \
        .eq('active', True) \
        .single() \
        .execute()
    
    if not response.data:
        raise ValueError(f"Show not found: {title}")
    
    # Get team members
    print("Loading team members for show ID:", response.data['id'])
    team_response = supabase.table('show_team') \
        .select('*') \
        .eq('show_id', response.data['id']) \
        .execute()
    print("Team member response:", team_response.data)
    
    # Load team members
    team_response = supabase.table('show_team').select('*').eq('show_id', response.data['id']).execute()
    team_members = [{
        'name': member['name'],
        'role_type_id': member['role_type_id']
    } for member in team_response.data]
    print("Loaded team members:", team_members)
    
    show_data = {
        'id': response.data['id'],
        'title': response.data['title'],
        'network_id': response.data['network_id'],
        'genre_id': response.data['genre_id'],
        'subgenres': response.data.get('subgenres', []) if response.data.get('subgenres') else [],
        'source_type_id': response.data.get('source_type_id'),
        'order_type_id': response.data.get('order_type_id'),
        'status_id': response.data.get('status_id'),
        'date': response.data.get('date'),
        'episode_count': response.data.get('episode_count', 0),
        'description': response.data.get('description', ''),
        'studios': response.data.get('studios', []) if response.data.get('studios') else [],
        'new_studios': [],
        'team_members': team_members
    }
    
    return show_data

def save_show(show_data: dict, operation: str = "Add show"):
    """Save show data to database and handle form reset."""
    print("\n" + "="*80)
    print("DEBUG: save_show() called")
    print("="*80)
    print("\nOperation:", operation)
    print("Show data keys:", list(show_data.keys()))
    print("\nTeam data:")
    print(show_data.get('team_members'))

    # Validate required fields
    required_fields = ['title', 'network_id']
    for field in required_fields:
        if not show_data.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    print("\n" + "="*80)
    print("DEBUG: Studio Save")
    print("="*80)
    
    # Handle existing studio IDs
    studio_ids = []
    print("\nExisting studios:", show_data.get('studios'))
    for studio in show_data.get('studios', []):
        if isinstance(studio, tuple):
            print(f"- Converting tuple: {studio} -> {studio[0]}")
            studio_ids.append(studio[0])  # Extract ID from tuple
        else:
            print(f"- Using ID directly: {studio}")
            studio_ids.append(studio)  # Already just an ID
    
    # Add new studios
    new_studios = show_data.get('new_studios', [])
    print("\nNew studios:", new_studios)
    if new_studios:
        for studio_name in new_studios:
            print(f"\nAdding new studio: {studio_name}")
            try:
                # Add new studio as production company
                response = supabase.table('studio_list').insert({
                    'studio': studio_name,
                    'type': 'Production Company'
                }).execute()
                new_id = response.data[0]['id']
                print(f"- Created with ID: {new_id}")
                studio_ids.append(new_id)
            except Exception as e:
                print(f"- Error adding studio: {str(e)}")
    
    print("\nFinal studio_ids:", studio_ids)
    
    # Prepare data for insert/update
    data = {
        'title': show_data['title'],
        'network_id': show_data['network_id'],  # Already an integer
        'genre_id': show_data['genre_id'],  # Already an integer
        'subgenres': show_data.get('subgenres', []),  # List of subgenre IDs
        'source_type_id': show_data.get('source_type_id'),  # Optional
        'order_type_id': show_data.get('order_type_id'),  # Optional
        'status_id': show_data.get('status_id'),  # Optional
        'episode_count': show_data.get('episode_count'),  # Optional
        'date': show_data.get('date'),  # Optional
        'description': show_data.get('description', ''),  # Optional with default
        'studios': studio_ids  # Array of integers
    }

    # Save show
    if operation == "Edit show":
        # Use stored show ID for update
        show_id = show_data['id']
        
        # Make sure we have all required fields
        if not all(show_data.get(field) for field in ['network_id', 'genre_id']):
            raise ValueError("Missing required fields for update")
        
        # Debug data types
        print("\n" + "="*80)
        print("DEBUG: Edit Show Data Types")
        print("="*80)
        for key, value in data.items():
            print(f"{key}: {value} (type: {type(value)})")
        print("="*80)
        
        # Update show using ID
        print("\nUpdating show with ID:", show_id)
        print("Update data:", data)
        try:
            # Start transaction
            response = supabase.table('shows') \
                .update(data) \
                .eq('id', show_id) \
                .execute()
            print("Update response:", response.data)
            if not response.data:
                raise Exception("No data returned from update")
        except Exception as e:
            print("ERROR updating show:", str(e))
            print("Full error:", e)
            raise

        # Delete existing team members
        print(f"\nDeleting team members for show {show_id}")
        try:
            # First get existing team members
            existing = supabase.table('show_team').select('*').eq('show_id', show_id).execute()
            if existing.data:
                # Delete them in a transaction
                delete_response = supabase.table('show_team') \
                    .delete() \
                    .eq('show_id', show_id) \
                    .execute()
                if not delete_response.data:
                    raise Exception(f"Failed to delete {len(existing.data)} existing team members")
                print(f"Deleted {len(delete_response.data)} team members")
            else:
                print("No existing team members found")
        except Exception as e:
            print("Error deleting team members:", str(e))
            raise
    else:
        print("Inserting new show with data:", data)
        response = supabase.table('shows').insert(data).execute()
        print("Insert response:", response.data)
        show_id = response.data[0]['id']
    
    # Add team members - one row per role
    print("\n" + "="*80)
    print("DEBUG: Team Member Save")
    print("="*80)
    
    if show_data.get('team_members'):
        try:
            print(f"\nDeleting team members for show_id: {show_id}")
            delete_response = supabase.table('show_team').delete().eq('show_id', show_id).execute()
            print(f"Delete response: {delete_response.data}")
            
            # Create one row per role
            team_inserts = []
            for member in show_data['team_members']:
                print(f"\nProcessing member: {member}")
                
                name = member['name'].strip()
                if not name:
                    print("- Skipping: empty name")
                    continue
                
                role_type_id = member['role_type_id']
                print(f"- Name: {name}")
                print(f"- Role Type ID: {role_type_id}")
                
                if not isinstance(role_type_id, int):
                    print(f"- Skipping role: {role_type_id} (not an integer)")
                    continue
                    
                print(f"- Adding role: {role_type_id}")
                team_inserts.append({
                    'show_id': show_id,
                    'name': name,
                    'role_type_id': role_type_id
                })
            
            if team_inserts:
                print(f"\nInserting {len(team_inserts)} team members")
                insert_response = supabase.table('show_team').insert(team_inserts).execute()
                print(f"Insert response: {insert_response.data}")
            else:
                print("No team members to insert")
        except Exception as e:
            print("Error saving team members:", str(e))
            raise        
                
    return show_id
