from django.contrib import admin
from .models import Tweet, Comment, Notification


# ── Inline: show comments inside Tweet admin ──────────────────────────────

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('user', 'text', 'created_at')
    can_delete = True
    show_change_link = False
    ordering = ('-created_at',)
    max_num = 20


# ── Tweet ModelAdmin ──────────────────────────────────────────────────────

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'short_text', 'like_count',
        'comment_count', 'has_image', 'created_at',
    )
    list_display_links = ('id', 'user', 'short_text')
    list_filter = ('created_at', 'user__is_staff')
    search_fields = ('text', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'photo_url', 'like_count', 'comment_count')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    inlines = [CommentInline]

    fieldsets = (
        ('Content', {
            'fields': ('user', 'text', 'photo_url'),
        }),
        ('Engagement', {
            'fields': ('like_count', 'comment_count'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def short_text(self, obj):
        return obj.text[:60] + ('…' if len(obj.text) > 60 else '')
    short_text.short_description = 'Text'

    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = '❤️ Likes'

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = '💬 Comments'

    def has_image(self, obj):
        return bool(obj.photo_url)
    has_image.boolean = True
    has_image.short_description = '🖼 Image'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('likes', 'comments')


# ── Comment ModelAdmin ────────────────────────────────────────────────────

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tweet_preview', 'short_text', 'created_at')
    list_display_links = ('id', 'user')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username', 'tweet__text')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def short_text(self, obj):
        return obj.text[:60] + ('…' if len(obj.text) > 60 else '')
    short_text.short_description = 'Comment'

    def tweet_preview(self, obj):
        return obj.tweet.text[:40] + ('…' if len(obj.tweet.text) > 40 else '')
    tweet_preview.short_description = 'On Tweet'


# ── Notification ModelAdmin ──────────────────────────────────────────────

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notification_type', 'is_read', 'created_at')
    list_display_links = ('id', 'user')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'comment__text')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Notification Info', {
            'fields': ('user', 'comment', 'notification_type', 'is_read'),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notification(s) marked as read.')
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notification(s) marked as unread.')
    mark_as_unread.short_description = 'Mark selected as unread'
