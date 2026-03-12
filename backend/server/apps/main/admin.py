from django.contrib import admin

from server.apps.main.models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin[BlogPost]):
    """Admin panel example for ``BlogPost`` model."""

    list_display = ("id", "title", "created_at", "updated_at")
    search_fields = ("title", "body")
    readonly_fields = ("created_at", "updated_at")
