# Quick Optimization Decision Guide

## Immediate Red Flags
If you see these during development, optimize immediately:

1. **Query Response**
   - Query takes > 2 seconds locally
   - Query returns > 10,000 rows
   - Query causes Streamlit to show loading spinner

2. **Memory Usage**
   - DataFrame > 100MB
   - Browser tab > 1GB
   - Streamlit session restart

3. **UI Responsiveness**
   - Chart takes > 1s to update
   - Tab switch takes > 500ms
   - Visible UI lag

## Quick Tests During Development

1. **Query Check**
   ```sql
   EXPLAIN ANALYZE your_query;
   -- Bad if:
   -- - Seq Scan on large tables
   -- - Many rows being filtered
   -- - Large sorts/joins
   ```

2. **Memory Check**
   ```python
   import sys
   df.memory_usage(deep=True).sum() / 1e6  # MB
   # Bad if > 100MB
   ```

3. **Load Test**
   ```python
   # Run this in dev to simulate prod:
   df = df.copy() * 5  # 5x data volume
   # Bad if noticeable slowdown
   ```

## When to Skip Optimization

1. **Acceptable Cases**
   - One-time admin operations
   - Background tasks
   - Development-only features

2. **Already Good Enough**
   - Query < 1s locally
   - Memory stable
   - UI feels smooth

## Quick Fixes vs Major Optimization

### Try Quick Fixes First
1. Add index
2. Add st.cache_data
3. Filter data earlier
4. Use smaller dtypes

### Need Major Optimization If
1. Quick fixes don't help
2. Multiple red flags
3. Core functionality affected

## Development Workflow

1. Write feature
2. Run quick tests above
3. If red flags -> quick fixes
4. If still bad -> plan major optimization

Remember: Local performance will be ~2x better than production!
