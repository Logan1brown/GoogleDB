# Genre Standardization Proposal

## Overview
Proposal to standardize TV show genres using TMDB (The Movie Database) as the source of truth. This will align our genre categorization with industry standards while maintaining data quality through an automated matching system.

## Current State
- Genres stored in `genre_list.csv`
- Shows reference genres in `shows.csv`
- Custom genre categories with aliases
- Potential inconsistencies with industry standards

## Proposed Solution

### 1. TMDB Integration

#### A. API Details
- Rate limit: 40 API calls per 10 seconds
- Each show requires ~4 API calls:
  1. Search show by name (1 call)
  2. Get details for top matches (2-3 calls)
- Processing capacity: ~10 shows per 10-second window
- Example: 100 shows = ~100 seconds total processing time

#### B. Genre System
Use TMDB's standardized genre system:
- Action & Adventure (10759)
- Animation (16)
- Comedy (35)
- Crime (80)
- Documentary (99)
- Drama (18)
- Family (10751)
- Kids (10762)
- Mystery (9648)
- News (10763)
- Reality (10764)
- Sci-Fi & Fantasy (10765)
- Soap (10766)
- Talk (10767)
- War & Politics (10768)
- Western (37)

### 2. Genre Mapping Strategy

#### A. TMDB to Local Mapping
Convert TMDB's multi-genre system to our genre/subgenre structure:
- Primary genre → `genre` column (first TMDB genre)
- Additional genres → `subgenre` column (remaining TMDB genres, comma-separated)

Examples:
```
TMDB: ["Drama", "Crime", "Thriller"]
Local: genre="Drama", subgenre="Crime, Thriller"

TMDB: ["Comedy"]
Local: genre="Comedy", subgenre=""
```

This approach:
- Maintains existing data structure
- Preserves all TMDB genre information
- Requires no schema changes
- Minimizes code modifications

#### B. Confidence Scoring
Total score (0-100) based on:

1. **Show Name Match** (50 points)
   - Uses fuzzy string matching ratio
   - Exact match = 50 points
   - Close match (e.g. "The Office US" vs "The Office") = ~45 points
   - Poor match = <30 points

2. **Network Match** (20 points)
   - Full points if network matches any TMDB network
   - Example: "ABC" matches ["ABC", "ABC Studios"]

3. **Creative Team Match** (15 points)
   - Uses show_team table for accurate name matching
   - Focuses on writers (w) and executive producers (ep)
   - First match = 5 points
   - Each additional match = 2 points (up to max 15)
   - Uses fuzzy matching for name variations

4. **Episode Count Match** (15 points)
   - Full points if counts match exactly
   - No partial points

Confidence Levels:
- High: 80-100 points (auto-approve)
- Medium: 50-79 points (manual review)
- Low: <50 points (flag for research)

#### B. Processing Categories
1. **High Confidence** (>80 points)
   - Automatic approval
   - Batch processing
   - Quality check sample

2. **Medium Confidence** (50-80 points)
   - Interactive review
   - Quick approve/reject UI
   - Batch review capability

3. **Low Confidence** (<50 points)
   - Manual review required
   - Research needed
   - Potential data updates

4. **No Match**
   - Manual research
   - Alternative data sources
   - Update show metadata

### 3. Output and Storage

#### A. Match Results CSV
```csv
show_name,tmdb_id,tmdb_url,confidence,match_details,current_genre,proposed_genre,proposed_subgenre,status
"Stranger Things",66732,"https://www.themoviedb.org/tv/66732",95,"name:50,network:20,team:15","Sci-Fi","Science Fiction","Drama, Mystery","high_confidence"
```

#### B. TMDB ID Storage
Store TMDB IDs in a new reference table for future use:

1. **Primary Use**
   - Genre standardization and updates

2. **Secondary Uses**
   - Episode count validation
   - Order type validation (comparing our order_type against TMDB's type field):
     - Limited/Miniseries vs Ongoing
     - Documentary vs Scripted
     - Reality shows

Note: We prioritize our own data for most fields (dates, status, team) as it's more accurate for our use case.

```sql
CREATE TABLE show_external_ids (
    show_name TEXT PRIMARY KEY,
    tmdb_id INTEGER,
    tmdb_url TEXT,
    match_confidence INTEGER,
    last_updated TIMESTAMP
);
```

### 3. Implementation Plan

#### Phase 1: Setup (Week 1)
- [ ] TMDB API integration
- [ ] Create confidence scoring system
- [ ] Build batch processing system:
  - Process shows in 10-show batches
  - Respect API rate limits (40 calls/10s)
  - Cache results to avoid duplicate calls
  - Handle API errors gracefully
- [ ] Test on sample dataset (50 shows)
- [ ] Generate initial accuracy metrics

#### Phase 2: Batch Processing (Week 2)
- [ ] Process high confidence matches
- [ ] Develop interactive review system
- [ ] Generate initial reports
- [ ] Review results

#### Phase 3: Data Migration (Week 3)
- [ ] Update genre_list.csv
- [ ] Migrate approved matches
- [ ] Document manual review cases
- [ ] Update analysis code

#### Phase 4: Cleanup (Week 4)
- [ ] Handle edge cases
- [ ] Update documentation
- [ ] Add genre validation
- [ ] Final QA

### 4. Technical Implementation

```python
# Key Components:

1. Match Confidence Scorer
def score_match_confidence(show_data, tmdb_result):
    """Score how confident we are in a TMDB match."""
    # Name matching
    # Network verification
    # Creator validation
    # Episode count check
    return confidence_score

2. Batch Processor
def process_shows_batch(shows_df):
    """Process shows in batches by confidence level."""
    # Search TMDB
    # Score matches
    # Categorize results
    return results_by_category

3. Interactive Review
def review_matches(results):
    """Interactive system for reviewing medium confidence matches."""
    # Display match details
    # Collect user input
    # Track decisions
    return approved_matches, manual_review

4. Report Generator
def generate_reports(approved_matches, manual_review):
    """Generate CSVs for tracking and review."""
    # Create matches report
    # Create review needed report
    # Generate statistics
```

### 5. Benefits
1. Industry standard categorization
2. Improved data consistency
3. Automated maintenance
4. Better cross-platform compatibility
5. Enhanced analysis capabilities

### 6. Risks and Mitigations
1. **Risk**: Incorrect matches
   - *Mitigation*: Multi-level confidence scoring
   - *Mitigation*: Interactive review system
   - *Mitigation*: Quality check samples

2. **Risk**: Missing shows in TMDB
   - *Mitigation*: Manual review process
   - *Mitigation*: Alternative data sources
   - *Mitigation*: Keep original genres as backup

3. **Risk**: API rate limits
   - *Mitigation*: Batch processing
   - *Mitigation*: Result caching
   - *Mitigation*: Throttled requests

### 7. Success Metrics
1. Match rate (target: >90% high/medium confidence)
2. Manual review rate (target: <10% of shows)
3. Genre accuracy (target: >95% for approved matches)
4. Processing time (target: <1 week for initial migration)

### 8. Next Steps
1. Review and approve proposal
2. Set up TMDB API access
3. Run pilot on 100 show sample
4. Review results and adjust confidence scoring
5. Proceed with full implementation

## Questions?
- TMDB API key requirements?
- Preferred manual review process?
- Timeline constraints?
- Success metric priorities?
