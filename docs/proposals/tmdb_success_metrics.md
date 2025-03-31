# TMDB Success Metrics Proposal

## Overview
Using TMDB's show data to create objective success metrics for series that are 2+ years old. This avoids relying on subjective ratings while providing concrete measures of industry success.

## Success Metrics

### Primary Metrics

1. **Season Achievement Levels**
   - Bronze: 2 seasons
   - Silver: 3 seasons
   - Gold: 4+ seasons
   - Rationale: Each renewal represents network confidence and audience retention

2. **Episode Volume**
   - Standard Season: ≥10 episodes
   - Quick Cancel: <11 episodes
   - Rationale: Episode count indicates network investment

3. **Production Status**
   - Completed: Ended naturally with planned finale
   - Cancelled: Terminated before story completion
   - Current: Still in production
   - Rationale: How show ended provides success context

### Scoring System

1. **Base Success (40 points)**
   - Show renewed for Season 2: 40 points
   - Rationale: Getting renewed once proves initial commercial success

2. **Sustained Success (Up to 60 points)**
   - Season 3: +20 points
   - Season 4: +20 points
   - Season 5+: +20 points
   - Rationale: Each additional renewal represents sustained profitability

3. **Ending Status (Up to 10 points)**
   - Planned Ending: +10 points
   - Still in Production: +5 points
   - Cancelled: 0 points
   - Rationale: How a show ends indicates overall performance

4. **Quick Cancel Penalty**
   - If cancelled with <11 episodes: -20 points
   - Rationale: Early cancellation indicates significant commercial failure

5. **Final Score Calculation**
   ```python
   def calculate_success_score(show):
       score = 0
       
       # Base success - Season 2
       if show.number_of_seasons >= 2:
           score += 40
       
       # Sustained success - Additional seasons
       if show.number_of_seasons >= 3:
           score += 20
       if show.number_of_seasons >= 4:
           score += 20
       if show.number_of_seasons >= 5:
           score += 20
           
       # Ending status
       if show.status == 'Ended' and show.planned_ending:
           score += 10
       elif show.in_production:
           score += 5
           
       # Quick cancel penalty
       if show.status == 'Cancelled' and show.number_of_episodes < 11:
           score = max(0, score - 20)
           
       return min(100, score)
   ```

6. **Success Tiers**
   - Elite (90-100): Long-running hits with planned endings
   - Successful (70-89): Multi-season shows with strong runs
   - Moderate (40-69): Renewed but limited success
   - Unsuccessful (0-39): Early cancellations or limited runs

### Implementation

1. **Data Collection**
   ```python
   show_details = {
       'number_of_seasons': int,
       'number_of_episodes': int,
       'status': str,
       'in_production': bool,
       'last_air_date': date
   }
   ```

2. **Success Calculation**
   ```python
   def calculate_success_score(show):
       score = 0
       
       # Base score for getting renewed
       if show.number_of_seasons >= 2:
           score += 40
           
       # Additional seasons bonus
       score += min(20 * (show.number_of_seasons - 2), 60)
           
       # Planned ending bonus
       if show.status == 'Ended' and not show.was_cancelled:
           score += 10
           
       return min(score, 100)
   ```

## Advantages

1. **Objectivity**
   - Based on concrete industry decisions
   - Not influenced by fan campaigns
   - Clear success thresholds

2. **Data Availability**
   - Already have TMDB integration
   - Data is regularly updated
   - Reliable source

3. **Industry Relevance**
   - Reflects actual network decisions
   - Shows true commercial success
   - Useful for predictions

## Limitations

1. **Time Lag**
   - Only reliable for shows 2+ years old
   - Can't evaluate very recent shows
   - Success metrics delayed

2. **Market Changes**
   - Streaming vs traditional seasons
   - Shorter season trends
   - Platform-specific patterns

3. **Missing Context**
   - Budget considerations
   - Time slot impact
   - International performance

## Next Steps

1. **Implementation**
   - Add metrics to TMDB data pull
   - Create success score column
   - Add to dashboard

2. **Validation**
   - Test against known successes
   - Adjust scoring weights
   - Validate with industry data

3. **Integration**
   - Update analysis tools
   - Add to network comparisons
   - Create success visualizations
