Final Report (Draft)
====================

Summary of changes
- Split requirements into `requirements-prod.txt`, `requirements-dev.txt`, `requirements-ci.txt`.
- Added smoke-test script and GitHub Action for verifying `requirements-prod.txt`.
- Implemented selectors/services refactor pattern and fixed N+1 issues in `get_tweets_for_list`.
- Added query-count tests and a profiling script under `scripts/`.
- Added caching for `get_tweet_stats` and `get_popular_tweets`.
- Created migrations for additional indexes and a GIN trigram search index.

Performance impact
- Iteration over tweets touching comments: reduced queries from ~17 to 2 via prefetch.
- Aggregates cached for short periods to reduce repeated heavy counts.

Risks & next steps
- Need to implement cache invalidation in services (on likes/comments).
- Deployment plan for concurrent index creation.
- Plan Redis provisioning and monitoring.
