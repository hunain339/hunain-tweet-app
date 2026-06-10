"""Compatibility shim: re-export selectors implementation.

This module preserves the original import path used across the codebase
(`tweet.query_optimizations`) while the real implementations live in
`tweet.selectors.tweet_selector`.
"""

from .selectors.tweet_selector import (
    OptimizedTweetQueries,
    OptimizedCommentQueries,
    AggregateStatistics,
)

__all__ = [
    "OptimizedTweetQueries",
    "OptimizedCommentQueries",
    "AggregateStatistics",
]
