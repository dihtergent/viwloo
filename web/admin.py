from django.contrib import admin
from .models import images, UserProfile, Post, Comment


admin.site.register(images)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name')
    search_fields = ('user__username', 'display_name')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'location_name', 'views_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'body', 'location_name')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'author__username')