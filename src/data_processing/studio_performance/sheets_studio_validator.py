"""Studio Data Validator for Sheets Database.

Validates and analyzes shows data against the studio_list_2.csv lookup table.
Identifies missing studios, potential new aliases, and categorization issues.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import csv

def load_studio_lookup() -> pd.DataFrame:
    """Load the studio lookup table from sheets."""
    sheets_dir = Path(__file__).parents[3] / "docs" / "sheets"
    lookup_path = sheets_dir / "STS Sales Database - studio_list_2.csv"
    
    # Read the file line by line to handle comments properly
    studios = []
    with open(lookup_path, 'r', encoding='utf-8') as f:
        # Read header first
        reader = csv.reader(f)
        header = next(reader)
        
        # Process remaining rows
        for row in reader:
            if not row or not row[0] or row[0].startswith('#'):
                continue
            studio = row[0].strip()
            if studio:  # Only add rows with a studio name
                studios.append(row)
    
    # Create DataFrame with the filtered rows
    df = pd.DataFrame(studios, columns=header)
    
    # Only include Studios - everything else will be marked as Other
    df = df[df['type'] == 'Studio']
    
    # Debug output
    print(f"\nLoaded {len(df)} studios from lookup file")
    
    return df

def extract_show_studios(shows_df: pd.DataFrame) -> Set[str]:
    """Extract all unique studios from shows data, handling multiple per show.
    
    This function splits comma-separated studio lists and returns a set of unique
    studios. It's designed to work with the new multi-studio data model where
    shows can have multiple studios listed in a comma-separated format.
    
    Args:
        shows_df: DataFrame containing show data with 'studio' column
        
    Returns:
        Set of unique studio names
    """
    # Split on commas and handle potential whitespace
    all_studios = shows_df['studio'].fillna('').astype(str)
    # Split and explode to separate rows
    all_studios = all_studios.str.split(',').explode()
    # Clean up each studio name
    all_studios = all_studios.str.strip()
    # Remove empty strings and get unique values
    return set(s for s in all_studios if s)

def find_studio_matches(studio_name: str, lookup_df: pd.DataFrame) -> List[Dict]:
    """Find potential matches for a studio name in the lookup table."""
    matches = []
    
    if pd.isna(studio_name):
        return matches
        
    # Create mapping from aliases to standard names
    mapping = {}
    for _, row in lookup_df.iterrows():
        # Get the standard name and category
        standard_name = str(row['studio']).strip()
        category = str(row['category']).strip()
        
        # Add the main name as its own alias (lowercase)
        mapping[standard_name.lower()] = {
            'studio': standard_name,
            'category': category
        }
        
        # Add aliases if they exist
        if not pd.isna(row['aliases']):
            aliases = str(row['aliases']).split(',')
            for alias in aliases:
                alias_clean = alias.strip().lower()  # Convert alias to lowercase
                if alias_clean:  # Skip empty aliases
                    mapping[alias_clean] = {
                        'studio': standard_name,
                        'category': category
                    }
    
    # Try to match the studio name
    studio_lower = studio_name.strip().lower()
    
    # Try to match against known studios
    if studio_lower in mapping:
        match = mapping[studio_lower]
        matches.append({
            'studio': studio_name.strip(),
            'match_type': 'studio',
            'matched_to': match['studio'],
            'category': match['category']
        })
    else:
        matches.append({
            'studio': studio_name.strip(),
            'match_type': 'other',
            'matched_to': 'Other',
            'category': 'Other'
        })
    
    return matches

def analyze_studio_coverage(shows_df: pd.DataFrame) -> Dict:
    """Analyze how well our studio lookup covers the shows data."""
    lookup_df = load_studio_lookup()
    show_studios = extract_show_studios(shows_df)
    
    # Track studio relationships and show counts
    studio_relationships = defaultdict(set)
    studio_show_counts = defaultdict(set)
    multi_studio_shows = []
    studio_match_status = {}
    others = set()
    
    # Analyze shows for relationships and counts
    for _, row in shows_df.iterrows():
        if pd.isna(row['studio']):
            continue
            
        show_studios = [s.strip() for s in str(row['studio']).split(',')]
        if len(show_studios) > 1:
            multi_studio_shows.append({
                'show': row['shows'],
                'studios': show_studios
            })
            # Record relationships between studios
            for i in range(len(show_studios)):
                for j in range(i + 1, len(show_studios)):
                    studio_relationships[show_studios[i]].add(show_studios[j])
                    studio_relationships[show_studios[j]].add(show_studios[i])
                    
        # Record show counts and check matches
        for studio in show_studios:
            if studio:  # Skip empty strings
                studio_show_counts[studio].add(row['shows'])
                if studio not in studio_match_status:
                    matches = find_studio_matches(studio, lookup_df)
                    if len(matches) == 0:
                        studio_match_status[studio] = {'status': 'unmatched'}
                        others.add(studio)
                    elif len(matches) == 1:
                        if matches[0]['match_type'] == 'other':
                            others.add(studio)
                        studio_match_status[studio] = {
                            'status': 'matched',
                            'matched_to': matches[0]['matched_to'],
                            'category': matches[0]['category']
                        }
                    else:
                        studio_match_status[studio] = {
                            'status': 'multiple',
                            'matches': matches
                        }
    
    # Print list of Others with their shows
    print("\nProduction Companies and Other Unmatched Studios:")
    print("----------------------------------------")
    for other in sorted(others):
        shows = sorted(studio_show_counts[other])
        print(f"\n{other} ({len(shows)} shows):")
        for show in shows:
            print(f"  - {show}")
    print(f"\nTotal unmatched entities: {len(others)}")
    
    results = {
        'matched': [],
        'unmatched': [],
        'multiple_matches': [],
        'studio_relationships': {
            studio: list(partners) 
            for studio, partners in studio_relationships.items()
        },
        'studio_show_counts': {
            studio: len(shows) 
            for studio, shows in studio_show_counts.items()
        },
        'multi_studio_shows': multi_studio_shows,
        'studio_match_status': studio_match_status,
        'others': sorted(others)
    }
    
    # Populate match lists
    for studio, status in studio_match_status.items():
        if status['status'] == 'unmatched':
            results['unmatched'].append(studio)
        elif status['status'] == 'matched':
            results['matched'].append({
                'studio': studio,
                'matched_to': status['matched_to'],
                'category': status['category']
            })
        else:
            results['multiple_matches'].append({
                'studio': studio,
                'matches': status['matches']
            })
    
    return results

def analyze_studio_categories(shows_df: pd.DataFrame) -> Dict[str, int]:
    """Analyze distribution of shows across studio categories."""
    lookup_df = load_studio_lookup()
    results = {}
    
    for _, show in shows_df.iterrows():
        if pd.isna(show['studio']):
            continue
            
        studios = [s.strip() for s in show['studio'].split(',')]
        for studio in studios:
            matches = find_studio_matches(studio, lookup_df)
            if matches:
                categories = [c.strip() for c in matches[0]['category'].split(',')]
                for category in categories:
                    results[category] = results.get(category, 0) + 1
    
    return results

def generate_validation_report(shows_df: pd.DataFrame) -> Dict:
    """Generate a comprehensive validation report."""
    coverage = analyze_studio_coverage(shows_df)
    categories = analyze_studio_categories(shows_df)
    
    # Find top collaborating studios
    studio_collab_counts = {
        studio: len(partners) 
        for studio, partners in coverage['studio_relationships'].items()
    }
    top_collaborators = sorted(
        studio_collab_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Find studios with most shows
    top_studios_by_shows = sorted(
        coverage['studio_show_counts'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return {
        'total_shows': len(shows_df),
        'unique_studios_in_shows': len(extract_show_studios(shows_df)),
        'matched_studios': len(coverage['matched']),
        'unmatched_studios': len(coverage['unmatched']),
        'multiple_matches': len(coverage['multiple_matches']),
        'category_distribution': categories,
        'unmatched_studio_names': coverage['unmatched'],
        'multiple_match_details': coverage['multiple_matches'],
        'multi_studio_shows': coverage['multi_studio_shows'],
        'top_collaborating_studios': top_collaborators,
        'top_studios_by_shows': top_studios_by_shows,
        'studio_match_status': coverage['studio_match_status']
    }

if __name__ == '__main__':
    # Load shows data from sheets
    sheets_dir = Path(__file__).parents[3] / "docs" / "sheets"
    shows_df = pd.read_csv(sheets_dir / "STS Sales Database - shows.csv")
    
    report = generate_validation_report(shows_df)
    print("\nStudio Validation Report")
    print("=====================")
    print(f"Total Shows: {report['total_shows']}")
    print(f"Unique Studios: {report['unique_studios_in_shows']}")
    print(f"Matched Studios: {report['matched_studios']}")
    print(f"Unmatched Studios: {report['unmatched_studios']}")
    print(f"Multiple Matches: {report['multiple_matches']}")
    
    print("\nDetailed Studio Match Status:")
    for studio, status in sorted(report['studio_match_status'].items()):
        if status['status'] == 'matched':
            print(f"  ✓ {studio} -> {status['matched_to']} ({status['category']})")
        elif status['status'] == 'unmatched':
            print(f"  ✗ {studio} (no match)")
        else:
            print(f"  ? {studio} (multiple matches):")
            for match in status['matches']:
                print(f"    - {match['matched_to']} ({match['category']})")
    
    print("\nTop Studios by Show Count:")
    for studio, count in report['top_studios_by_shows']:
        print(f"  {studio}: {count} shows")
        
    print("\nTop Collaborating Studios:")
    for studio, collab_count in report['top_collaborating_studios']:
        print(f"  {studio}: {collab_count} collaborations")
    
    print("\nShows with Multiple Studios:")
    for show in report['multi_studio_shows']:
        print(f"  {show['show']}: {', '.join(show['studios'])}")
    
    print("\nCategory Distribution:")
    for category, count in sorted(report['category_distribution'].items()):
        print(f"  {category}: {count}")
    
    if report['multiple_match_details']:
        print("\nMultiple Matches Found:")
        for case in sorted(report['multiple_match_details'], key=lambda x: x['studio']):
            print(f"  {case['studio']}:")
            for match in case['matches']:
                print(f"    - {match['matched_to']} ({match['match_type']})")
