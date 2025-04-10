#!/usr/bin/env python3
"""
Migration to import show data from Google Sheets
"""
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config.sheets_config import sheets_config

def get_supabase_connection() -> connection:
    """Get connection to Supabase database."""
    load_dotenv()
    required_vars = ['DATABASE_URL']
    for var in required_vars:
        if not os.getenv(var):
            print(f"Missing required environment variable: {var}")
            sys.exit(1)
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    conn.autocommit = False
    return conn

def get_sheets_client() -> gspread.Client:
    """Get authenticated Google Sheets client."""
    load_dotenv()
    required_vars = ['GOOGLE_SHEETS_CREDENTIALS_FILE']
    for var in required_vars:
        if not os.getenv(var):
            print(f"Missing required environment variable: {var}")
            sys.exit(1)

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    credentials = Credentials.from_service_account_file(
        os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE'),
        scopes=scopes
    )
    
    return gspread.authorize(credentials)

def get_sheet_data(gc: gspread.Client, sheet_name: str) -> pd.DataFrame:
    """Get data from a specific Google Sheet."""
    spreadsheet = gc.open_by_key(sheets_config.spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)
    
    # Get all data including headers
    data = worksheet.get_all_values()
    
    # First row is headers
    headers = data[0]
    rows = data[1:]
    
    # Convert to DataFrame
    return pd.DataFrame(rows, columns=headers)

def clean_array_field(value: str) -> List[str]:
    """Clean and split array field values."""
    if pd.isna(value) or not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]

def get_lookup_id(cur, table: str, name_field: str, name: str) -> int:
    """Get ID from a lookup table by name or aliases."""
    if pd.isna(name) or not name:
        return None
    
    name = name.strip()
    
    # Try exact match first
    cur.execute(f"""
        SELECT id FROM {table}
        WHERE {name_field} = %s
    """, (name,))
    
    result = cur.fetchone()
    if result:
        return result[0]
    
    # If no match and this is network_list, try aliases
    if table == 'network_list':
        cur.execute("""
            SELECT id FROM network_list
            WHERE %s = ANY(aliases)
        """, (name,))
        
        result = cur.fetchone()
        if result:
            return result[0]
    
    result = cur.fetchone()
    return result[0] if result else None

def ensure_studio_exists(cur, studio_name: str) -> int:
    """Ensure studio exists in studio_list, creating it if needed."""
    # Clean studio name - remove 'Other:' prefix if present
    clean_name = studio_name.replace('Other:', '').strip()
    
    # First try to find existing studio by name or search_studio
    cur.execute("""
        SELECT id FROM studio_list
        WHERE studio = %s OR search_studio = %s
    """, (clean_name, clean_name.lower()))
    
    result = cur.fetchone()
    if result:
        return result[0]
        
    # If not found, create new studio
    # If original had 'Other:' prefix, create as production company
    is_other = 'Other:' in studio_name
    
    cur.execute("""
        INSERT INTO studio_list (
            studio,
            type,
            active
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (studio) DO UPDATE SET
            type = EXCLUDED.type,
            active = EXCLUDED.active
        RETURNING id
    """, (
        clean_name,
        'production company' if is_other else 'studio',
        True
    ))
    
    return cur.fetchone()[0]

def import_shows(cur, shows_df: pd.DataFrame):
    """Import shows from shows sheet."""
    print("Importing shows...")
    print("\nColumns in sheet:")
    print(shows_df.columns.tolist())
    print("\nFirst row:")
    print(shows_df.iloc[0].to_dict())
    
    # Get lookup data first
    cur.execute("SELECT id, network FROM network_list")
    networks = dict(cur.fetchall())
    
    cur.execute("SELECT id, genre FROM genre_list")
    genres = dict(cur.fetchall())
    
    cur.execute("SELECT id, status FROM status_types")
    statuses = dict(cur.fetchall())
    
    cur.execute("SELECT id, type FROM source_types")
    sources = dict(cur.fetchall())
    
    cur.execute("SELECT id, type FROM order_types")
    orders = dict(cur.fetchall())
    
    # Process each show
    for _, row in shows_df.iterrows():
        title = row.get('shows')  # Column name in sheet is 'shows'
        if pd.isna(title):
            continue
        print(f"Processing show: {title}")
            
        # Get IDs from lookup tables
        network_id = get_lookup_id(cur, 'network_list', 'network', row.get('network'))
        genre_id = get_lookup_id(cur, 'genre_list', 'genre', row.get('genre'))
        source_type_id = get_lookup_id(cur, 'source_types', 'type', row.get('source_type'))
        
        # Get status from status column
        status = row.get('status')
        if status and not pd.isna(status):
            print(f"Looking for status: {status}")
            cur.execute("""
                SELECT id FROM status_types
                WHERE status = %s OR search_status = %s
            """, (status, status.lower()))
            result = cur.fetchone()
            status_id = result[0] if result else None
            print(f"Found status_id: {status_id}")
        else:
            status_id = None
            
        # Get order type
        order_type = row.get('order_type')
        if order_type and not pd.isna(order_type):
            print(f"Looking for order_type: {order_type}")
            cur.execute("""
                SELECT id FROM order_types
                WHERE type = %s OR search_type = %s
            """, (order_type, order_type.lower()))
            result = cur.fetchone()
            order_type_id = result[0] if result else None
            print(f"Order Type ID: {order_type_id}")
        else:
            order_type_id = None
        
        # Get description from notes
        description = row.get('notes')
        if pd.isna(description):
            description = None
        print(f"Description: {description}")

        # Get TMDB ID
        tmdb_id = row.get('TMDB_ID')
        if pd.isna(tmdb_id):
            tmdb_id = None
        else:
            try:
                tmdb_id = int(tmdb_id)
                print(f"TMDB ID: {tmdb_id}")
            except (ValueError, TypeError):
                print(f"Failed to parse TMDB_ID: {tmdb_id}")
                tmdb_id = None

        # Process studios array - handle both regular studios and Other: production companies
        studios = clean_array_field(row.get('studio', ''))
        studio_ids = []
        for studio in studios:
            studio_id = ensure_studio_exists(cur, studio)
            if studio_id:
                studio_ids.append(studio_id)
                print(f"Found/created studio: {studio} -> ID: {studio_id}")
        print(f"Final studio IDs: {studio_ids}")
        
        # Process subgenres array
        subgenres = []
        if not pd.isna(row.get('subgenre')):
            for sg in clean_array_field(row['subgenre']):
                sg_id = get_lookup_id(cur, 'genre_list', 'genre', sg)
                if sg_id:
                    subgenres.append(sg_id)
                    print(f"Found subgenre: {sg} -> ID: {sg_id}")
        print(f"Final subgenres: {subgenres}")

        # Get date
        date = row.get('date')
        if not pd.isna(date):
            try:
                # Convert to ISO format YYYY-MM-DD
                date = pd.to_datetime(date).strftime('%Y-%m-%d')
                print(f"Date: {date}")
            except Exception as e:
                print(f"Failed to parse date {date}: {e}")
                date = None
        else:
            date = None

        # Get episode count
        episode_count = row.get('episode_count')
        if not pd.isna(episode_count):
            try:
                episode_count = int(episode_count)
                print(f"Episode count: {episode_count}")
            except (ValueError, TypeError):
                print(f"Failed to parse episode count: {episode_count}")
                episode_count = None
        else:
            episode_count = None

        try:
            print(f"Inserting show with values:")
            print(f"- Title: {title}")
            print(f"- Network ID: {network_id}")
            print(f"- Genre ID: {genre_id}")
            print(f"- Source Type ID: {source_type_id}")
            print(f"- Status ID: {status_id}")
            print(f"- Order Type ID: {order_type_id}")
            print(f"- Studio IDs: {studio_ids}")
            print(f"- Description: {description}")
            print(f"- TMDB ID: {tmdb_id}")
            print(f"- Date: {date}")
            print(f"- Episode Count: {episode_count}")
            print(f"- Subgenres: {subgenres}")
            
            # Insert show
            cur.execute("""
                INSERT INTO shows (
                    title,
                    network_id,
                    genre_id,
                    source_type_id,
                    status_id,
                    order_type_id,
                    studios,
                    description,
                    tmdb_id,
                    date,
                    episode_count,
                    subgenres,
                    active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (title) DO UPDATE SET
                    network_id = EXCLUDED.network_id,
                    genre_id = EXCLUDED.genre_id,
                    source_type_id = EXCLUDED.source_type_id,
                    status_id = EXCLUDED.status_id,
                    order_type_id = EXCLUDED.order_type_id,
                    studios = EXCLUDED.studios,
                    description = EXCLUDED.description,
                    tmdb_id = EXCLUDED.tmdb_id,
                    date = EXCLUDED.date,
                    episode_count = EXCLUDED.episode_count,
                    subgenres = EXCLUDED.subgenres,
                    active = EXCLUDED.active
                RETURNING id
        """, (
            title,
            network_id,
            genre_id,
            source_type_id,
            status_id,
            order_type_id,
            studio_ids,
            description,
            tmdb_id,
            date,
            episode_count,
            subgenres,
            True
        ))
            result = cur.fetchone()
            print(f"Successfully inserted/updated show {title} with ID {result[0]}")
        except Exception as e:
            print(f"Error inserting show {title}: {str(e)}")
            raise

def normalize_role(role: str) -> list[str]:
    """Normalize role string and handle special abbreviations."""
    # Handle special abbreviations
    role_mapping = {
        'd. ep': ['Director', 'Executive Producer'],
        'ep. sr': ['Executive Producer', 'Showrunner'],
        'w ep': ['Writer', 'Executive Producer'],
    }
    
    if role.lower().strip() in role_mapping:
        return role_mapping[role.lower().strip()]
    
    # Otherwise return the role as is
    return [role.strip()]

def import_show_team(cur, team_df: pd.DataFrame):
    """Import show team data from show_team sheet."""
    print("Importing show team...")
    
    # Process each team member
    for _, row in team_df.iterrows():
        show_name = row['show_name']  # Column name in sheet is 'show_name'
        if pd.isna(show_name):
            continue
            
        # Get show ID - handle Star Wars shows specially
        if show_name.startswith('Star Wars:'):
            # Try without the 'Star Wars:' prefix
            base_title = show_name.replace('Star Wars:', '').strip()
            cur.execute("SELECT id FROM shows WHERE title = %s", (base_title,))
            show = cur.fetchone()
        else:
            cur.execute("SELECT id FROM shows WHERE title = %s", (show_name,))
            show = cur.fetchone()
        
        if not show:
            print(f"Warning: Show not found: {show_name}")
            continue
            
        show_id = show[0]
        name = row['name']
        
        # Split roles by comma and normalize each one
        roles_str = row.get('roles', '')
        if pd.isna(roles_str) or not roles_str.strip():
            print(f"Info: No roles specified for {name} on {show_name}")
            # Get Unknown role type ID
            cur.execute("SELECT id FROM role_types WHERE role = 'Unknown'")
            unknown_role_id = cur.fetchone()[0]
            
            # Insert team member with Unknown role
            try:
                cur.execute("""
                    INSERT INTO show_team (
                        show_id, name, role_type_id,
                        team_order, notes
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (show_id, name, role_type_id) DO UPDATE SET
                        team_order = EXCLUDED.team_order,
                        notes = EXCLUDED.notes
                """, (
                    show_id,
                    name,
                    unknown_role_id,
                    None if pd.isna(row.get('order')) or row.get('order') == '' else row.get('order'),
                    'No role specified in original data'
                ))
                print(f"Added {name} (Unknown role) for {show_name}")
            except Exception as e:
                print(f"Error adding {name} (Unknown role) for {show_name}: {e}")
            continue
            
        # Split by comma and handle each role or abbreviation
        all_roles = []
        for role in clean_array_field(roles_str):
            all_roles.extend(normalize_role(role))
            
        if not all_roles:
            print(f"Warning: No valid roles found for {name} on {show_name}")
            continue
            
        # Process each normalized role
        for role in all_roles:
            role_type_id = get_lookup_id(cur, 'role_types', 'role', role)
            if not role_type_id:
                print(f"Warning: Role type not found: {role} for {name} on {show_name}")
                continue
                
            try:
                cur.execute("""
                    INSERT INTO show_team (
                        show_id, name, role_type_id,
                        team_order, notes
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (show_id, name, role_type_id) DO UPDATE SET
                        team_order = EXCLUDED.team_order,
                        notes = EXCLUDED.notes
                """, (
                    show_id,
                    name,
                    role_type_id,
                    None if pd.isna(row.get('order')) or row.get('order') == '' else row.get('order'),
                    row.get('notes')
                ))
                print(f"Added {name} as {role} for {show_name}")
            except Exception as e:
                print(f"Error adding {name} as {role} for {show_name}: {e}")

def import_tmdb_metrics(cur, metrics_df: pd.DataFrame):
    """Import TMDB metrics from TMDB_success_metrics sheet."""
    print("Importing TMDB metrics...")
    
    # Keep only first occurrence of each TMDB ID
    seen_tmdb_ids = set()
    
    for _, row in metrics_df.iterrows():
        title = row['Title']  # Column name in sheet is 'Title'
        if pd.isna(title):
            continue
            
        # Skip if we've already seen this TMDB ID
        tmdb_id = row.get('TMDB_ID')
        if tmdb_id in seen_tmdb_ids:
            continue
        seen_tmdb_ids.add(tmdb_id)
            
        # Get show's TMDB ID - try both with and without Star Wars prefix
        cur.execute("SELECT tmdb_id FROM shows WHERE title = %s", (title,))
        result = cur.fetchone()
        
        if not result and title.startswith('Star Wars:'):
            # Try without prefix
            base_title = title.replace('Star Wars:', '').strip()
            cur.execute("SELECT tmdb_id FROM shows WHERE title = %s", (base_title,))
            result = cur.fetchone()
        elif not result and not title.startswith('Star Wars:'):
            # Try with prefix
            prefixed_title = f"Star Wars: {title}"
            cur.execute("SELECT tmdb_id FROM shows WHERE title = %s", (prefixed_title,))
            result = cur.fetchone()
            
        if not result or not result[0]:
            print(f"Warning: No TMDB ID found for show: {title}")
            continue
            
        tmdb_id = result[0]
        
        # Parse episodes per season
        episodes_per_season = []
        if not pd.isna(row.get('tmdb_eps')):
            episodes_per_season = [
                int(eps.strip())
                for eps in row['tmdb_eps'].split(',')
                if eps.strip().isdigit()
            ]
        
        cur.execute("""
            INSERT INTO tmdb_success_metrics (
                tmdb_id, seasons, episodes_per_season,
                total_episodes, average_episodes,
                status, last_air_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT tmdb_success_metrics_tmdb_id_key DO UPDATE SET
                seasons = EXCLUDED.seasons,
                episodes_per_season = EXCLUDED.episodes_per_season,
                total_episodes = EXCLUDED.total_episodes,
                average_episodes = EXCLUDED.average_episodes,
                status = EXCLUDED.status,
                last_air_date = EXCLUDED.last_air_date
        """, (
            tmdb_id,
            int(row.get('tmdb_seasons')) if row.get('tmdb_seasons') and not pd.isna(row.get('tmdb_seasons')) and row.get('tmdb_seasons') != '' else None,
            episodes_per_season,
            int(row.get('tmdb_total_eps')) if row.get('tmdb_total_eps') and not pd.isna(row.get('tmdb_total_eps')) and row.get('tmdb_total_eps') != '' else None,
            float(row.get('tmdb_avg_eps')) if row.get('tmdb_avg_eps') and not pd.isna(row.get('tmdb_avg_eps')) and row.get('tmdb_avg_eps') != '' else None,
            row.get('tmdb_status'),
            row.get('tmdb_last_air') if row.get('tmdb_last_air') and not pd.isna(row.get('tmdb_last_air')) and row.get('tmdb_last_air') != '' else None
        ))

def main():
    """Main migration function."""
    print("Starting show data import...")
    
    # Get database connection
    conn = get_supabase_connection()
    cur = conn.cursor()
    
    try:
        # Get Google Sheets client
        gc = get_sheets_client()
        
        try:
            # Import shows
            shows_df = get_sheet_data(gc, sheets_config.shows_sheet)
            import_shows(cur, shows_df)
            conn.commit()
            print("Successfully imported shows")
        except Exception as e:
            print(f"Error importing shows: {e}")
            conn.rollback()
            raise
        
        try:
            # Import show team data
            team_df = get_sheet_data(gc, sheets_config.team_sheet)
            import_show_team(cur, team_df)
            conn.commit()
            print("Successfully imported show team data")
        except Exception as e:
            print(f"Error importing show team: {e}")
            conn.rollback()
            raise
        
        try:
            # Import TMDB metrics
            metrics_df = get_sheet_data(gc, sheets_config.tmdb_metrics_sheet)
            import_tmdb_metrics(cur, metrics_df)
            conn.commit()
            print("Successfully imported TMDB metrics")
        except Exception as e:
            print(f"Error importing TMDB metrics: {e}")
            conn.rollback()
            raise
        
    except Exception as e:
        print(f"Error during import: {e}")
        conn.rollback()
        raise
    
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
