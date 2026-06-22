from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.permissions import IsAuthorOrReadOnly
from apps.blog.models import Post
from .models import Comment
from .serializers import CommentSerializer


@extend_schema(tags=["Comments"])
@extend_schema_view(
    list   = extend_schema(summary="List all comments for a post"),
    create = extend_schema(summary="Add a comment to a post (authenticated)"),
    retrieve       = extend_schema(summary="Retrieve a single comment"),
    update         = extend_schema(summary="Update a comment (author only)"),
    partial_update = extend_schema(summary="Partial update a comment (author only)"),
    destroy        = extend_schema(summary="Delete a comment (author only)"),
)
class CommentViewSet(viewsets.ModelViewSet):
    """
    Nested ViewSet scoped to a specific post:
      GET  /blog/posts/<post_slug>/comments/
      POST /blog/posts/<post_slug>/comments/
      GET  /blog/posts/<post_slug>/comments/<id>/
      PUT  /blog/posts/<post_slug>/comments/<id>/
      DEL  /blog/posts/<post_slug>/comments/<id>/

    - Only top-level comments are returned (replies are nested inside each comment).
    - Authenticated users can create comments.
    - Only the comment's author can update/delete.
    """

    serializer_class   = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def _get_post(self):
        """Resolve and cache the parent post from the URL kwarg."""
        if not hasattr(self, "_post"):
            self._post = Post.objects.get(slug=self.kwargs["post_slug"])
        return self._post

    def get_queryset(self):
        post = self._get_post()
        return (
            Comment.objects
            .filter(post=post, parent=None, is_active=True)
            .select_related("user")
            .prefetch_related("replies__user")
        )

    def perform_create(self, serializer):
        post = self._get_post()
        serializer.save(user=self.request.user, post=post)

    def destroy(self, request, *args, **kwargs):
        """
        Soft-delete: set is_active=False instead of hard delete.
        This preserves the thread structure while hiding the content.
        """
        comment = self.get_object()
        comment.is_active = False
        comment.body = "[deleted]"
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
