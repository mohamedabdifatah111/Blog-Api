from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet

app_name = "comments"

# Comments are a sub-resource of posts:
# /api/v1/blog/posts/<post_slug>/comments/
router = DefaultRouter()
router.register(r"", CommentViewSet, basename="comment")

urlpatterns = [
    path(
        "blog/posts/<slug:post_slug>/comments/",
        include((router.urls, "comments"), namespace="comments"),
    ),
]
