from django.contrib import admin
from .models import images, UserProfile, Post


admin.site.register(images)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name')
    search_fields = ('user__username', 'display_name')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'views_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'body')