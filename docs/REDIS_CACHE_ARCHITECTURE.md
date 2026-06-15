Redis Cache Architecture
------------------------

Purpose
- Cache aggregated values and read-heavy selectors: popular feeds, tweet stats, unread counts.

Key patterns
- `tweet_stats:{tweet_id}` -> JSON stats (TTL: 60s)
- `popular_tweets:{limit}` -> list of Tweet IDs or serialized objects (TTL: 30s)
- `user_unread_count:{user_id}` -> integer (TTL: 30s or event-driven invalidation)

Invalidation
- On create/delete comment or like events, invalidate `tweet_stats:{tweet_id}` and related feed keys.
- Use pub/sub or event queue (Redis stream) if multiple app instances need to invalidate caches quickly.

Operational
- Use Redis with at least 1GB for metadata; enable eviction policy `volatile-ttl` or `allkeys-lru` depending on usage.
- Use a namespaced prefix and set a reasonable max TTL.
