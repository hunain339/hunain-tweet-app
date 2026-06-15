Pagination & Feed Design
------------------------

Goals
- Fast cursor-based feed for timelines
- Predictable pagination links and stable ordering

Plan
- Use keyset (cursor) pagination on `created_at` + `id` for deterministic ordering.
- Expose `?cursor=<ts>_<id>&limit=20` for the feed endpoint. Return `next_cursor` when more results exist.
- Backend: selectors will accept `before_cursor` and `limit` and translate to QuerySet filters.
- Frontend: load initial page, then fetch `next_cursor` for infinite scroll.

Implementation notes
- Add helper `tweet/selectors/pagination.py` with cursor encoding/decoding.
- Use `order_by('-created_at', '-id')` and `filter((created_at, id) < (cursor_ts, cursor_id))`.
