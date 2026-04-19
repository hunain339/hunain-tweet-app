"""
Custom template tags and filters for the tweet app.
Provides reusable components like admin badges, comment counts, etc.
"""

from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import pluralize

register = template.Library()


@register.simple_tag
def admin_badge(user):
    """
    Display a styled admin/staff badge for superusers and staff members.
    Returns empty string if user is not admin/staff.
    
    Usage: {% admin_badge user %}
    """
    if user.is_superuser:
        return mark_safe(
            '<span class="badge bg-danger ms-2" title="Superuser">'
            '<i class="bi bi-shield-fill"></i> Superuser'
            '</span>'
        )
    elif user.is_staff:
        return mark_safe(
            '<span class="badge bg-warning text-dark ms-2" title="Staff Member">'
            '<i class="bi bi-star-fill"></i> Staff'
            '</span>'
        )
    return ''


@register.filter
def comment_count_text(count):
    """
    Return a properly pluralized comment count text.
    
    Usage: {{ tweet.comments.count|comment_count_text }}
    """
    return f"{count} comment{pluralize(count)}"


@register.filter
def like_count_text(count):
    """
    Return a properly pluralized like count text.
    
    Usage: {{ tweet.likes.count|like_count_text }}
    """
    return f"{count} like{pluralize(count)}"


@register.inclusion_tag('tweet_parts/admin_badge.html', takes_context=False)
def admin_badge_component(user):
    """
    Include-style admin badge component.
    Returns context for a dedicated template.
    """
    return {
        'is_admin': user.is_superuser,
        'is_staff': user.is_staff,
    }


@register.filter
def short_number(value):
    """
    Format numbers for display (e.g., 1500 -> 1.5K).
    
    Usage: {{ tweet.view_count|short_number }}
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value
    
    if value >= 1000000:
        return f"{value / 1000000:.1f}M"
    elif value >= 1000:
        return f"{value / 1000:.1f}K"
    return str(value)

@register.simple_tag
def unread_count(user):
    """
    Return the count of unread notifications for a user.
    Usage: {% unread_count user %}
    """
    if user.is_authenticated:
        return user.notifications.filter(is_read=False).count()
    return 0
