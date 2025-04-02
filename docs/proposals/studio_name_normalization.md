# Studio Name Normalization Proposal

## Current Issues
1. Studio names are inconsistent (e.g. "Netflix" vs "Netflix Studios")
2. Need to track both known studios and allow new ones
3. Multiple studios per show need to be supported
4. Studio list has mixed purposes (validation, relationships, types)

## Proposed Changes

### 1. Modify studio_list.csv
```csv
studio,type,parent_company,division,platform,aliases,category,is_tracked
# 1. Vertically Integrated Media Companies
## Network-First

# Disney Television Studios
20th Television,Studio,Disney,Disney Television Studios,Disney+,"20th Century TV,20th Century Fox TV","Vertically Integrated,Network-First",true
ABC Signature,Studio,Disney,Disney Television Studios,Disney+,"ABC Studios","Vertically Integrated,Network-First",true
Disney Branded Television,Studio,Disney,Disney Television Studios,Disney+,"Disney Channel Productions","Vertically Integrated,Network-First",true
FX Productions,Studio,Disney,Disney Television Studios,Disney+/Hulu,"FX","Vertically Integrated,Network-First",true
Searchlight Television,Studio,Disney,Disney Television Studios,Hulu,,"Vertically Integrated,Network-First",true

# Warner Bros Television Group
Warner Bros Television,Studio,Warner Bros Discovery,WB Television Group,Max,"WBTV","Vertically Integrated,Network-First",true
Warner Horizon,Studio,Warner Bros Discovery,WB Television Group,Max,"Warner Horizon Television","Vertically Integrated,Network-First",true
Warner Bros Animation,Studio,Warner Bros Discovery,WB Television Group,Max,"WBA","Vertically Integrated,Network-First",true
Telepictures,Studio,Warner Bros Discovery,WB Television Group,Max,,"Vertically Integrated,Network-First",true

# NBCU
Universal Television,Studio,NBCU,NBCUniversal Television,Peacock,"UTV","Vertically Integrated,Network-First",true
Universal Content Productions,Studio,NBCU,NBCUniversal Television,Peacock,"UCP","Vertically Integrated,Network-First",true

# Paramount
Paramount Television Studios,Studio,Paramount,Paramount Television Group,Paramount+,"Paramount TV","Vertically Integrated,Network-First",true
MTV Entertainment Studios,Studio,Paramount,Paramount Television Group,Paramount+,"MTV Studios","Vertically Integrated,Network-First",true
Showtime Networks,Studio,Paramount,Paramount Television Group,Paramount+,"Showtime","Vertically Integrated,Network-First",true

## Streaming-First
Netflix Studios,Studio,Netflix,,Netflix,"Netflix","Vertically Integrated,Streaming-First",true
Amazon Studios,Studio,Amazon,Amazon MGM Studios,Prime Video,,"Vertically Integrated,Streaming-First",true
MGM Television,Studio,Amazon,Amazon MGM Studios,Prime Video,"MGM Studios","Vertically Integrated,Streaming-First",true
Apple Studios,Studio,Apple,,Apple TV+,,"Vertically Integrated,Streaming-First",true

# 2. Independent Studios
## Larger Indies (Mini-Majors)
Lionsgate Television,Studio,Lionsgate,,,"Lionsgate TV","Independent,Large",true
AMC Studios,Studio,AMC,,,,"Independent,Large",true

## Mid-Size Indies
A24,Studio,Independent,,,,"Independent,Mid-Size",true
Entertainment One,Studio,Hasbro,,,"eOne","Independent,Mid-Size",true
Gaumont Television,Studio,Independent,,,,"Independent,Mid-Size",true

# 3. Production Companies
3 Arts Entertainment,Production,Independent,,,,Production,false
Anonymous Content,Production,Independent,,,,Production,false
Bad Robot,Production,Independent,,,,Production,false
Berlanti Productions,Production,Independent,,,,Production,false
Chuck Lorre Productions,Production,Independent,,,,Production,false
Scott Free Productions,Production,Independent,,,,Production,false
Temple Hill Entertainment,Production,Independent,,,,Production,false

# Other
Other,Studio,Other,,,,Other,true
```

Changes:
- Reorganize into three main categories:
  1. Vertically Integrated Media Companies (Network-First and Streaming-First)
  2. Independent Studios (Large and Mid-Size)
  3. Production Companies
- Add `platform` column to track streaming/network relationships
- Use hierarchical categories (e.g. "Independent,Large")
- Keep `is_tracked` to distinguish studios from production companies
- Maintain comprehensive alias list (not shown for brevity)
- Keep "Other" as special entry

### 2. Modify Shows Sheet Studio Column

#### Data Validation Rules
1. Allow comma-separated list of studios
2. Each studio must be either:
   - A canonical name from studio_list.csv
   - An alias from studio_list.csv
   - Start with "Other: " followed by custom text

Examples of valid entries:
```
Netflix Studios
Netflix Studios, Other: New Studio X
Other: Independent Studio Y, Warner Bros Television
```

#### Google Sheets Formula
```
=ARRAYFORMULA(
  IF(
    ISBLANK(D2:D), ,
    JOIN(", ",
      SPLIT(D2:D, ",")
    )
  )
)
```

### 3. Benefits
1. Forces canonical names for known studios
2. Still allows new studios via "Other: "
3. Maintains multiple studios per show
4. Clear distinction between tracked vs untracked studios
5. No additional columns needed
6. Easy to analyze in code

### 4. Implementation Steps

#### Phase 1: Setup
1. Clean up studio_list.csv
   - Remove incorrect entries
   - Add missing aliases
   - Add is_tracked column
   - Verify studio types and parent companies

2. Update shows sheet structure
   - Add data validation to studio column
   - Create custom formula for validation
   - Test with various combinations

#### Phase 2: Data Migration
1. Create migration script to normalize existing studio data:
```python
def normalize_studios():
    # Read both sheets
    studio_df = pd.read_csv('studio_list.csv')
    shows_df = pd.read_csv('shows.csv')
    
    # Build alias mapping
    alias_to_canonical = {}
    for _, row in studio_df.iterrows():
        canonical = row['studio']
        if pd.notna(row['aliases']):
            for alias in row['aliases'].split(','):
                alias_to_canonical[alias.strip()] = canonical

    def normalize_studio_cell(studio_str):
        if pd.isna(studio_str):
            return studio_str
            
        studios = [s.strip() for s in studio_str.split(',')]
        normalized = []
        
        for studio in studios:
            # Use canonical name if known
            if studio in alias_to_canonical:
                normalized.append(alias_to_canonical[studio])
            elif studio in studio_df['studio'].values:
                normalized.append(studio)
            # Mark unknown studios with Other prefix
            else:
                normalized.append(f"Other: {studio}")
                
        return ', '.join(normalized)
        
    # Apply normalization
    shows_df['studio'] = shows_df['studio'].apply(normalize_studio_cell)
    return shows_df
```

2. Iterative Review Process:
   - Run script on test subset first
   - Review normalized output:
     ```
     Before: "Netflix, Warner Bros. Television, Unknown Studio, WBTV"
     After:  "Netflix Studios, Warner Bros Television, Other: Unknown Studio, Warner Bros Television"
     ```
   - Identify patterns in "Other:" entries
   - Update studio_list.csv with missing aliases
   - Rerun normalization
   - Repeat until satisfied with results

3. Final Migration:
   - Run normalized script on full dataset
   - Generate report of all "Other:" studios
   - Manual review of changes
   - Apply to production sheet

#### Phase 3: Analyzer Updates
1. Update analyzer code
   - Add tracking of "Other:" studios
   - Add frequency analysis
   - Add suggestions for frequently used "Other:" studios

### 5. Affected Components

#### Core Data Processing
1. `src/data_processing/analyze_shows.py`:
   - Update studio field handling in clean_data()
   - Modify studio normalization logic
   - Update validation checks
   - Adjust studio-based statistics

2. `src/data_processing/export_shows.py`:
   - Update export format for multi-studio shows
   - Modify any studio-based filtering

3. `src/data_processing/studio_performance/studio_analyzer.py`:
   - Major updates needed for multi-studio analysis
   - Revise market share calculations
   - Update studio relationship tracking

#### Dashboard Components
1. `src/dashboard/components/studio_view.py`:
   - Update studio performance metrics
   - Modify visualization for multi-studio shows
   - Add studio relationship views

2. `src/dashboard/app.py`:
   - Update studio filtering logic
   - Modify data aggregation for multi-studio shows

#### Testing
1. `src/tests/test_sheet_import.py`:
   - Update test cases for multi-studio support
   - Add new test scenarios

#### Impact Assessment
1. Data Model Changes:
   - Shows with multiple studios need new representation
   - Studio relationships need tracking
   - Historical data needs migration

2. Analytics Impact:
   - Market share calculations become more complex
   - Studio performance metrics need revision
   - New relationship-based analytics possible

3. Dashboard Impact:
   - UI/UX changes for multi-studio display
   - Performance impact of relationship queries
   - New visualizations needed

4. Migration Considerations:
   - Data cleanup required
   - Dashboard version compatibility
   - User retraining needed

### 6. Future Considerations
1. Regularly review "Other:" studios for potential promotion to studio_list.csv
2. Consider adding more metadata for studios (e.g. country, founding date)
3. May want to add validation rules for parent company names
4. Could add relationship tracking between studios (e.g. partnerships)
