from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ("__str__", "user", "post", "parent", "is_active", "created_at")
    list_filter   = ("is_active",)
    search_fields = ("body", "user__email", "post__title")
    raw_id_fields = ("user", "post", "parent")
    date_hierarchy = "created_at"
    actions       = ["activate_comments", "deactivate_comments"]

    @admin.action(description="Activate selected comments")
    def activate_comments(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected comments")
    def deactivate_comments(self, request, queryset):
        queryset.update(is_active=False)
