"""
Django Filter configurations for scalable API queries.

This module provides FilterSets for various models to enable
efficient and flexible filtering through DRF's DjangoFilterBackend.
"""

import django_filters
from .models import Tweet
from django.contrib.auth.models import User


class TweetFilterSet(django_filters.FilterSet):
    """
    FilterSet for Tweet model supporting efficient filtering.
    
    Filters:
    - user: Filter tweets by user (single user ID or multiple)
    - created_after: Filter tweets created after a specific date
    - created_before: Filter tweets created before a specific date
    - has_photo: Filter tweets with or without photos
    
    Example queries:
    - /api/tweets/?user=1
    - /api/tweets/?user=1&user=2  (multiple users)
    - /api/tweets/?created_after=2024-01-01
    - /api/tweets/?has_photo=true
    - /api/tweets/?user=1&search=keyword&page=1  (combined)
    """
    
    # Filter by user - allows multiple selections
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        help_text="Filter tweets by specific user(s)"
    )
    
    # Date range filters
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter tweets created after this date"
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter tweets created before this date"
    )
    
    # Filter for media-containing tweets
    has_photo = django_filters.BooleanFilter(
        field_name='photo_url',
        lookup_expr='isnull',
        exclude=True,
        help_text="Filter tweets with photos (true) or without (false)"
    )
    
    # Ordering - allows sorting by multiple fields
    ordering = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('-created_at', 'newest'),
            ('likes_count', 'least_liked'),
            ('-likes_count', 'most_liked'),
        ),
        label='Sort by'
    )

    class Meta:
        model = Tweet
        fields = ['user', 'created_after', 'created_before', 'has_photo']
