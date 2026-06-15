Database indexing & migration plan
================================

Summary
-------
- Tests and profiling show hotspots around comment lookups and aggregate counts.
- Models already include useful indexes, but we should add a few targeted indexes and partial indexes for common queries.

Recommended indexes
--------------------
- Ensure the many-to-many likes table has indexes on `(tweet_id, user_id)` and `(user_id, tweet_id)` (usually created by Django but verify).  
- Add an index on `Comment.parent` (for fast replies lookup) if not present.  
- Add a partial index on `Notification(user_id, is_read)` to speed unread-count queries:  
  - PostgreSQL: `CREATE INDEX idx_notifications_user_unread ON tweet_notification (user_id) WHERE (is_read = false);`
- Consider a GIN index for full-text search on `Tweet.text` if you enable text search:  
  - `CREATE INDEX idx_tweet_text_gin ON tweet_tweet USING gin(to_tsvector('english', text));`
- If you frequently filter/sort feeds by `(user, created_at)` or `(-created_at)` the existing compound indexes are appropriate.

Migration strategy
------------------
1. Add index declarations to models where appropriate (recommended for maintainability) and run `makemigrations` to generate migration files. Example model change (pseudo):

    class Meta:
        indexes = [
            models.Index(fields=["tweet", "-created_at"]),
            models.Index(fields=["parent"]),
        ]

2. For partial or expression-based indexes (GIN/to_tsvector), create a manual migration using `RunSQL` to ensure correct SQL for Postgres.

3. Deploy migrations during a maintenance window if live traffic is high. Creating indexes concurrently on Postgres avoids locks:

    ALTER TABLE ... CREATE INDEX CONCURRENTLY ...;

4. Monitor query performance and pg_stat_activity during index creation.

Verification
------------
- Run explain/analyze on slow queries before and after adding indexes.  
- Add unit/integration tests that assert indexing expectations where feasible (e.g., explain plan contains index usage) or at minimum run representative benchmarks (benchmarks/bench_db.py).

Rollback plan
-------------
- Any new index can be dropped if it doesn't help: `DROP INDEX CONCURRENTLY idx_name;`.

Next steps I'll take now
-----------------------
1. Add this file (`docs/DB_INDEXING_AND_MIGRATIONS.md`).
2. Mark the todo `Database indexing and migration plan` in-progress.
3. Prepare model migration changes for indexes in a follow-up patch (if you want me to apply them automatically).
