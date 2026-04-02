from django.contrib import admin
from .models import Tweet, Comment

# Register your models here.


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


class TweetAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'created_at', 'likes_count')
    search_fields = ('text', 'user__username')
    list_filter = ('created_at',)
    inlines = [CommentInline]
    readonly_fields = ('created_at', 'updated_at')
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'


admin.site.register(Tweet, TweetAdmin)
admin.site.register(Comment)
