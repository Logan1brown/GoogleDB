"""Simple Streamlit app for validating TMDB matches."""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from pathlib import Path

# Add project root to Python path
root_dir = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.append(str(root_dir))

from src.data_processing.external.tmdb.tmdb_client import TMDBClient

def load_matches(csv_path: str) -> pd.DataFrame:
    """Load matches from CSV."""
    df = pd.read_csv(csv_path)
    # Fill NaN values with -1 for TMDB IDs
    df['tmdb_id'] = df['tmdb_id'].fillna(-1).astype(int)
    # Convert validated to bool
    # Read validation status directly from CSV
    df['validated'] = df['validated'].fillna(False)
    return df

def save_matches(df: pd.DataFrame, csv_path: str):
    """Save matches back to CSV."""
    print(f"Saving matches to {csv_path}")
    print(f"DataFrame has {len(df)} rows")
    print(f"Validation status counts:\n{df['validated'].value_counts()}")
    df.to_csv(csv_path, index=False)
    print("Save completed")
    
def search_tmdb(client: TMDBClient, show_name: str):
    """Search TMDB for alternative matches."""
    results = client.search_tv_show(show_name)
    if not results:
        return []
    
    # Get details for each result
    details = []
    for show in results[:5]:  # Limit to top 5 matches
        try:
            detail = client.get_tv_show_details(show.id)
            details.append(detail)
        except Exception as e:
            st.error(f"Error getting details for {show.name}: {e}")
    return details

def main():
    st.title("TMDB Match Validation")
    
    # Get TMDB API key from environment or .env file
    env_path = Path(__file__).parent.parent.parent.parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith('TMDB_API_KEY='):
                    tmdb_api_key = line.split('=')[1].strip()
                    break
    
    # Load matches
    csv_path = Path(__file__).parent.parent.parent.parent.parent.parent / "docs/sheets/tmdb_matches.csv"
    if not csv_path.exists():
        st.error("No matches file found. Please run the matcher first.")
        return
        
    matches_df = load_matches(str(csv_path))
    
    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        confidence_filter = st.selectbox(
            "Filter by confidence:",
            ["All"] + list(matches_df["confidence"].unique())
        )
    with col2:
        validated_filter = st.selectbox(
            "Filter by validation:",
            ["All", "Validated", "Not Validated"]
        )
    
    # Apply filters
    filtered_df = matches_df.copy()
    if confidence_filter != "All":
        filtered_df = filtered_df[filtered_df["confidence"] == confidence_filter]
    if validated_filter != "All":
        is_validated = validated_filter == "Validated"
        filtered_df = filtered_df[filtered_df["validated"] == is_validated]
    
    # Show progress
    total = len(matches_df)
    validated = len(matches_df[matches_df["validated"] == True])
    not_validated = len(matches_df[matches_df["validated"] == False])
    st.progress(validated / total)
    st.write(f"Validated (True): {validated}/{total} shows")
    st.write(f"Not Validated (False): {not_validated}/{total} shows")
    
    # Show matches
    for idx, row in filtered_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2,2,1])
            
            # Show title comparison
            with col1:
                st.subheader("Show Name Comparison (60 pts)")
                st.write("**Our Title:**", row["show_name"])
                st.write("**TMDB Title:**", row["tmdb_name"])
                st.write(f"Score: {row['score']} ({row['confidence']})")
                st.write(f"TMDB ID: {row['tmdb_id']}")
            
            # Show network and EP comparison
            with col2:
                st.subheader("Network (25 pts) & EPs (15 pts)")
                st.write("**Our Network:**", row["our_network"])
                st.write("**TMDB Network:**", row["tmdb_network"])
                st.write("")
                st.write("**Our EPs:**")
                our_eps = row["our_eps"].split(",") if pd.notna(row["our_eps"]) else []
                for ep in our_eps:
                    st.write(f"- {ep.strip()}")
                st.write("")
                st.write("**TMDB EPs:**")
                tmdb_eps = row["tmdb_eps"].split(",") if pd.notna(row["tmdb_eps"]) else []
                for ep in tmdb_eps:
                    st.write(f"- {ep.strip()}")
            
            # Validation and TMDB Search
            with col3:
                # Make key unique by including row index
                key = f"validate_{idx}_{row['tmdb_id']}"
                current = bool(row["validated"])  # Convert to bool explicitly
                st.write(f"Current status: {'Validated' if current else 'Not Validated'}")
                validated = st.checkbox("Validate", value=current, key=key)
                
                # Add TMDB search button
                if st.button("Search TMDB", key=f"search_{idx}"):
                    st.write("Alternative matches from TMDB:")
                    try:
                        client = TMDBClient(api_key=tmdb_api_key)
                        results = search_tmdb(client, row['show_name'])
                        
                        if results:
                            for result in results:
                                air_year = result.first_air_date.year if result.first_air_date else 'N/A'
                                with st.expander(f"{result.name} ({air_year})"):
                                    st.write(f"TMDB ID: {result.id}")
                                    st.write(f"Overview: {result.overview}")
                                    st.write(f"First Air Date: {result.first_air_date}")
                                    st.write(f"Network: {', '.join(n.name for n in result.networks) if result.networks else 'N/A'}")
                                    if result.id != row['tmdb_id']:
                                        if st.button(f"Use this match", key=f"use_{idx}_{result.id}"):
                                            try:
                                                # Get details for the new match
                                                details = client.get_tv_show_details(result.id)
                                                
                                                # Find the row index
                                                show_idx = matches_df.index[matches_df['show_name'] == row['show_name']].item()
                                                
                                                # Update the DataFrame
                                                matches_df.at[show_idx, 'tmdb_id'] = result.id
                                                matches_df.at[show_idx, 'tmdb_name'] = details.name
                                                matches_df.at[show_idx, 'tmdb_network'] = ','.join(n.name for n in details.networks) if details.networks else ''
                                                matches_df.at[show_idx, 'tmdb_genre'] = ','.join(g.name for g in details.genres) if details.genres else ''
                                                matches_df.at[show_idx, 'validated'] = 'False'
                                                
                                                # Save changes
                                                save_matches(matches_df, csv_path)
                                                
                                                # Force Streamlit to rerun
                                                st.experimental_rerun()
                                            except Exception as e:
                                                st.error(f"Error updating match: {e}")
                        else:
                            st.write("No matches found")
                    except Exception as e:
                        st.error(f"Error searching TMDB: {e}")
                
                if validated != current:
                    idx = matches_df.index[matches_df['tmdb_id'] == int(row['tmdb_id'])].tolist()
                    if idx:
                        matches_df.loc[idx[0], 'validated'] = bool(validated)  # Store as bool
                        save_matches(matches_df, csv_path)
                        st.success(f"Saved validation status: {'Validated' if validated else 'Not Validated'}")
            
            st.divider()
    
    # Save button (backup)
    if st.button("Force Save"):
        save_matches(matches_df, csv_path)
        st.success("Saved!")

if __name__ == "__main__":
    main()
