"""
Smart Caching Utilities for API Performance

This module provides intelligent caching strategies that:
- Cache public/anonymous requests aggressively
- Exclude authenticated user-specific data from cache
- Handle cache invalidation on data mutations
- Provide cache utilities for high-performance reads
"""

from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from functools import wraps
from django.core.cache import cache
import hashlib


class CacheConfig:
    """Cache timeout constants for different endpoints."""
    
    # Public list endpoints - safe to cache for longer
    PUBLIC_LIST_CACHE_TIME = 300  # 5 minutes
    
    # Detail endpoints - cache for moderate duration
    PUBLIC_DETAIL_CACHE_TIME = 600  # 10 minutes
    
    # Search and filtered endpoints - shorter cache (dynamic)
    SEARCH_CACHE_TIME = 120  # 2 minutes
    
    # Popular/trending endpoints - moderate cache
    TRENDING_CACHE_TIME = 300  # 5 minutes


def smart_cache_page(cache_timeout, must_vary_user=True):
    """
    Smart caching decorator that:
    - Skips cache for authenticated users (differentiated responses)
    - Applies aggressive caching for public/anonymous users
    - Varies cache by query parameters for filtered results
    
    Args:
        cache_timeout: Time in seconds to cache the response
        must_vary_user: If True, varies cache by User header (default: True)
    
    Example:
        @smart_cache_page(CacheConfig.PUBLIC_LIST_CACHE_TIME)
        def get_tweets_list(request):
            ...
    """
    def decorator(view_func):
        # First apply cache_page if user is anonymous
        cached_view = cache_page(cache_timeout)(view_func)
        
        # Then apply vary_on_headers for consistent cache keys
        if must_vary_user:
            cached_view = vary_on_headers('Authorization', 'Cookie')(cached_view)
        
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Skip caching for authenticated users (they get dynamic responses)
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # Apply caching for anonymous users
            return cached_view(request, *args, **kwargs)
        
        return wrapper
    return decorator


def get_cache_key(prefix, *args, **kwargs):
    """
    Generate consistent cache keys from function args/kwargs.
    
    Args:
        prefix: Cache key prefix (e.g., 'tweet_list')
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
    
    Returns:
        String cache key
    
    Example:
        key = get_cache_key('tweet_list', user_id=1, page=2)
    """
    # Build a string from all args/kwargs
    key_data = f"{prefix}:" + ":".join(
        str(arg) for arg in args
    )
    
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        key_data += ":" + ":".join(
            f"{k}={v}" for k, v in sorted_kwargs
        )
    
    # Hash to keep key length reasonable
    hash_obj = hashlib.md5(key_data.encode())
    return f"{prefix}:{hash_obj.hexdigest()}"


def invalidate_tweet_cache(tweet_id):
    """
    Invalidate related cache entries when a tweet is modified.
    
    Args:
        tweet_id: Primary key of the modified tweet
    
    Invalidates:
    - Tweet detail cache
    - User tweet list cache
    - Popular tweets cache
    """
    try:
        # Invalidate tweet detail cache
        detail_key = get_cache_key('tweet_detail', tweet_id)
        cache.delete(detail_key)
        
        # Invalidate popular/trending cache (since engagement changed)
        cache.delete('trending_tweets')
        cache.delete('popular_tweets')
        
        # Could also invalidate user-specific tweet list, but we don't
        # cache user lists by default due to rapid changes
    except Exception:
        # Fail gracefully - cache is not critical
        pass


def invalidate_user_cache(user_id):
    """
    Invalidate related cache entries when a user's data changes.
    
    Args:
        user_id: Primary key of the user
    """
    try:
        # Invalidate user tweet list cache
        user_list_key = get_cache_key('user_tweets', user_id)
        cache.delete(user_list_key)
    except Exception:
        pass


class CacheAwarePaginator:
    """
    Paginator that can cache results for public/anonymous requests.
    
    Usage:
        paginator = CacheAwarePaginator(queryset, page_size=10)
        page = paginator.get_page(request, cache_key='tweets_page_{page}')
    """
    
    def __init__(self, queryset, page_size=10):
        self.queryset = queryset
        self.page_size = page_size
    
    def get_page_from_cache_or_query(self, page_num, cache_key, cache_timeout=300):
        """
        Get paginated results from cache or database.
        
        Args:
            page_num: Page number to retrieve
            cache_key: Cache key prefix
            cache_timeout: Time to cache in seconds
        
        Returns:
            Paginated data
        """
        full_cache_key = f"{cache_key}:{page_num}"
        
        # Try to get from cache
        cached_data = cache.get(full_cache_key)
        if cached_data is not None:
            return cached_data
        
        # Fetch from database
        start_idx = (page_num - 1) * self.page_size
        end_idx = start_idx + self.page_size
        data = list(self.queryset[start_idx:end_idx])
        
        # Store in cache
        cache.set(full_cache_key, data, cache_timeout)
        
        return data
