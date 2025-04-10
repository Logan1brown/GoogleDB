import os
import gspread
from google.oauth2.service_account import Credentials
import psycopg2
from dotenv import load_dotenv
import pandas as pd

def connect_to_db():
    conn = psycopg2.connect(
        host="aws-0-us-west-1.pooler.supabase.com",
        port="5432",
        database="postgres",
        user="postgres.hlwnwcxylueaoemdqiwo",
        password="QTRlgAeCCO1fEumL"
    )
    return conn

def get_sheets_data():
    load_dotenv()
    creds = Credentials.from_service_account_file(
        os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE'),
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.readonly']
    )
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'))
    
    # Get raw data including headers
    shows_ws = spreadsheet.worksheet('shows')
    team_ws = spreadsheet.worksheet('show_team')
    metrics_ws = spreadsheet.worksheet('tmdb_success_metrics')
    
    # Get values and first row as headers
    shows_data = shows_ws.get_all_values()
    team_data = team_ws.get_all_values()
    metrics_data = metrics_ws.get_all_values()
    
    # Convert to DataFrame, using only the first occurrence of each header
    shows_headers = [h if shows_data[0][:i].count(h) == 0 else f'{h}_{shows_data[0][:i].count(h)}' 
                    for i, h in enumerate(shows_data[0])]
    team_headers = [h if team_data[0][:i].count(h) == 0 else f'{h}_{team_data[0][:i].count(h)}' 
                   for i, h in enumerate(team_data[0])]
    metrics_headers = [h if metrics_data[0][:i].count(h) == 0 else f'{h}_{metrics_data[0][:i].count(h)}' 
                      for i, h in enumerate(metrics_data[0])]
    
    shows_sheet = pd.DataFrame(shows_data[1:], columns=shows_headers)
    team_sheet = pd.DataFrame(team_data[1:], columns=team_headers)
    metrics_sheet = pd.DataFrame(metrics_data[1:], columns=metrics_headers)
    
    return shows_sheet, team_sheet, metrics_sheet

def compare_data():
    print("Fetching data from sheets...")
    shows_sheet, team_sheet, metrics_sheet = get_sheets_data()
    
    print("\nFetching data from Supabase...")
    conn = connect_to_db()
    cur = conn.cursor()
    
    # Compare show counts
    cur.execute("SELECT COUNT(*) FROM shows")
    db_show_count = cur.fetchone()[0]
    sheet_show_count = len(shows_sheet[shows_sheet['shows'].notna()])
    print(f"\nShow counts:")
    print(f"Sheets: {sheet_show_count}")
    print(f"Database: {db_show_count}")
    
    # Compare team member counts
    cur.execute("SELECT COUNT(*) FROM show_team")
    db_team_count = cur.fetchone()[0]
    sheet_team_count = len(team_sheet[team_sheet['show_name'].notna()])
    print(f"\nTeam member counts:")
    print(f"Sheets: {sheet_team_count}")
    print(f"Database: {db_team_count}")
    
    # Compare TMDB metrics counts
    cur.execute("SELECT COUNT(*) FROM tmdb_success_metrics")
    db_metrics_count = cur.fetchone()[0]
    sheet_metrics_count = len(metrics_sheet[metrics_sheet['TMDB_ID'].notna()])
    print(f"\nTMDB metrics counts:")
    print(f"Sheets: {sheet_metrics_count}")
    print(f"Database: {db_metrics_count}")
    
    # Check studio counts
    print("\nAnalyzing studios...")
    all_studios = set()
    for studios in shows_sheet['studio'].dropna():
        all_studios.update(s.strip() for s in studios.split(','))
    
    cur.execute("SELECT studio FROM studio_list")
    db_studios = {row[0] for row in cur.fetchall()}
    
    print(f"Unique studios in sheets: {len(all_studios)}")
    print(f"Studios in database: {len(db_studios)}")
    
    missing_studios = all_studios - db_studios
    if missing_studios:
        print("\nStudios in sheets but missing from database:")
        for studio in sorted(missing_studios):
            print(f"- {studio}")
    
    extra_studios = db_studios - all_studios
    if extra_studios:
        print("\nStudios in database but not in sheets:")
        for studio in sorted(extra_studios):
            print(f"- {studio}")
    
    # Sample check of shows with multiple studios
    print("\nSample of shows with multiple studios from sheets:")
    multi_studio_shows = shows_sheet[shows_sheet['studio'].str.contains(',', na=False)].head()
    for _, row in multi_studio_shows.iterrows():
        print(f"\nShow: {row['shows']}")
        print(f"Studios in sheet: {row['studio']}")
        cur.execute("""
            SELECT array_agg(sl.studio) 
            FROM shows s 
            JOIN studio_list sl ON sl.id = ANY(s.studios)
            WHERE s.title = %s
            GROUP BY s.id
        """, (row['shows'],))
        result = cur.fetchone()
        if result:
            print(f"Studios in DB: {', '.join(result[0])}")
        else:
            print("No studios found in DB")
        
    # Analyze team member discrepancy
    print("\nAnalyzing team member discrepancy...")
    print("Sample of team members from sheets:")
    print(team_sheet[['show_name', 'name', 'roles']].head())
    
    # Count unique show/name/role combinations
    sheet_combos = set()
    for _, row in team_sheet.iterrows():
        if pd.isna(row['show_name']) or pd.isna(row['name']) or pd.isna(row['roles']):
            continue
        sheet_combos.add((row['show_name'], row['name'], row['roles']))
    
    print(f"\nUnique show/name/role combinations in sheets: {len(sheet_combos)}")
    
    # Count database entries
    cur.execute("""
        SELECT COUNT(*) FROM show_team st 
        JOIN shows s ON st.show_id = s.id 
        JOIN role_types rt ON st.role_type_id = rt.id
    """)
    db_count = cur.fetchone()[0]
    print(f"Show team entries in database: {db_count}")
    
    # Sample some database entries
    print("\nSample of team members from database:")
    cur.execute("""
        SELECT s.title, st.name, rt.role 
        FROM show_team st 
        JOIN shows s ON st.show_id = s.id 
        JOIN role_types rt ON st.role_type_id = rt.id 
        ORDER BY s.title LIMIT 5
    """)
    for row in cur.fetchall():
        print(f"Show: {row[0]}, Name: {row[1]}, Role: {row[2]}")
    
    # Check TMDB metrics discrepancy
    print("\nAnalyzing TMDB metrics discrepancy...")
    cur.execute("""
        SELECT s.title, m.tmdb_id, m.seasons, m.total_episodes 
        FROM tmdb_success_metrics m 
        JOIN shows s ON m.tmdb_id = s.tmdb_id 
        ORDER BY s.title LIMIT 5
    """)
    print("\nSample of TMDB metrics in database:")
    for row in cur.fetchall():
        print(f"Show: {row[0]}, TMDB ID: {row[1]}, Seasons: {row[2]}, Episodes: {row[3]}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    compare_data()
