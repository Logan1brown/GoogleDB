# Performance Benchmarks

## Key Metrics & Targets

### 1. Page Load Times
- Initial load: < 3 seconds
- Subsequent loads (cached): < 1 second
- Tab switching: < 500ms

### 2. Query Performance
- Dashboard queries: < 1 second
- Materialized view refresh: < 30 seconds
- Cache hit rate: > 80%

### 3. Resource Usage
- Memory per session: < 500MB
- CPU usage: < 20% sustained
- Connection pool: < 80% utilization

## Measurement Strategy

### Production Monitoring
1. **Streamlit Cloud Metrics**
   ```python
   import time
   
   @st.cache_data
   def log_performance():
       start = time.time()
       # ... operation ...
       duration = time.time() - start
       st.session_state.perf_logs.append({
           'operation': 'query_name',
           'duration': duration,
           'timestamp': time.time(),
           'cache_hit': st.session_state.get('cache_hit', False)
       })
   ```

2. **Supabase Query Stats**
   - Enable `pg_stat_statements`
   - Monitor through Supabase dashboard
   - Focus on:
     - Execution time
     - Rows processed
     - Cache hits

### User-Centric Metrics
1. **Time to Interactive**
   - When can users start interacting?
   - When do charts become visible?
   - Track in session state:
   ```python
   if 'page_ready' not in st.session_state:
       start = time.time()
       # ... load components ...
       st.session_state.load_time = time.time() - start
   ```

2. **Error Rates**
   - Track failed queries
   - Monitor timeout frequency
   - Log user-facing errors

## Performance Budget

### Response Times
| Operation | Target | Max Acceptable |
|-----------|---------|----------------|
| Page Load | 3s | 5s |
| Query | 1s | 2s |
| Chart Update | 500ms | 1s |

### Resource Limits
| Resource | Target | Max Acceptable |
|----------|--------|----------------|
| Memory | 500MB | 750MB |
| CPU | 20% | 40% |
| DB Connections | 20 | 30 |

## Gradual Rollout Plan

1. **Staging Environment**
   - Deploy to separate Streamlit app
   - Use production database
   - Run synthetic load tests

2. **Limited Release**
   - Release to 10% of users
   - Monitor performance metrics
   - Compare with local benchmarks

3. **Full Release Criteria**
   - All metrics within targets
   - No timeout errors
   - Cache hit rate > 80%

## Monitoring Setup

```python
# Add to main app.py
if 'perf_metrics' not in st.session_state:
    st.session_state.perf_metrics = {
        'page_loads': [],
        'query_times': {},
        'error_counts': 0,
        'cache_hits': 0,
        'cache_misses': 0
    }

def track_operation(name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                st.session_state.perf_metrics['query_times'][name] = duration
                return result
            except Exception as e:
                st.session_state.perf_metrics['error_counts'] += 1
                raise e
        return wrapper
    return decorator

# Usage:
@track_operation("load_market_data")
def load_market_data():
    # ... existing code ...
```

## Action Thresholds

1. **Immediate Action Required**
   - Page load > 5s
   - Query timeout rate > 1%
   - Memory usage > 750MB

2. **Investigation Needed**
   - Cache hit rate < 70%
   - CPU sustained > 30%
   - Error rate > 0.1%

3. **Optimization Opportunity**
   - Any metric consistently above 80% of target

## Review Process

1. Daily:
   - Check error rates
   - Monitor resource usage
   - Review slowest queries

2. Weekly:
   - Analyze performance trends
   - Review cache effectiveness
   - Update optimization priorities

3. Monthly:
   - Full performance review
   - Update benchmarks if needed
   - Plan major optimizations
