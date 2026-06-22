from django.contrib import admin
from .models import Category, Tag, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display   = ("title", "author", "status", "category", "created_at")
    list_filter    = ("status", "category", "tags")
    search_fields  = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields  = ("author",)
    date_hierarchy = "created_at"
    ordering       = ["-created_at"]
    filter_horizontal = ("tags",)
