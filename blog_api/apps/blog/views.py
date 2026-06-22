from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from core.permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .models import Category, Tag, Post
from .serializers import (
    CategorySerializer,
    TagSerializer,
    PostListSerializer,
    PostDetailSerializer,
)
from .filters import PostFilter


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

@extend_schema(tags=["Categories"])
@extend_schema_view(
    list    = extend_schema(summary="List all categories"),
    retrieve= extend_schema(summary="Retrieve a category by id"),
    create  = extend_schema(summary="Create a category (admin only)"),
    update  = extend_schema(summary="Update a category (admin only)"),
    partial_update = extend_schema(summary="Partial update a category (admin only)"),
    destroy = extend_schema(summary="Delete a category (admin only)"),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category management.
    Read: public.
    Write: admin/staff only.
    """

    queryset           = Category.objects.all()
    serializer_class   = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field       = "slug"


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------

@extend_schema(tags=["Tags"])
@extend_schema_view(
    list    = extend_schema(summary="List all tags"),
    retrieve= extend_schema(summary="Retrieve a tag"),
    create  = extend_schema(summary="Create a tag (admin only)"),
    update  = extend_schema(summary="Update a tag (admin only)"),
    partial_update = extend_schema(summary="Partial update a tag (admin only)"),
    destroy = extend_schema(summary="Delete a tag (admin only)"),
)
class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Tag management.
    Read: public.
    Write: admin/staff only.
    """

    queryset           = Tag.objects.all()
    serializer_class   = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field       = "slug"


# ---------------------------------------------------------------------------
# Post
# ---------------------------------------------------------------------------

@extend_schema(tags=["Posts"])
@extend_schema_view(
    list   = extend_schema(
        summary="List published posts",
        parameters=[
            OpenApiParameter("search",         description="Search in title and content"),
            OpenApiParameter("status",         description="Filter by status (draft|published)"),
            OpenApiParameter("category",       description="Filter by category id"),
            OpenApiParameter("category_slug",  description="Filter by category slug"),
            OpenApiParameter("tags",           description="Filter by tag id"),
            OpenApiParameter("author",         description="Filter by author id"),
            OpenApiParameter("ordering",       description="Order by: created_at, -created_at, updated_at"),
        ],
    ),
    retrieve       = extend_schema(summary="Retrieve a single post by slug"),
    create         = extend_schema(summary="Create a new post (authenticated authors)"),
    update         = extend_schema(summary="Update a post (author only)"),
    partial_update = extend_schema(summary="Partial update a post (author only)"),
    destroy        = extend_schema(summary="Delete a post (author only)"),
)
class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for blog Post CRUD.

    - **List / Retrieve**: public — only `published` posts.
    - **Create**: authenticated users; throttled to 20 creates/hour.
    - **Update / Delete**: author of the post only.
    - Supports full-text **search** on `title` and `content`.
    - Supports **filtering** by status, category, tags, author, and date range.
    - Supports **ordering** by `created_at` and `updated_at`.
    """

    permission_classes = [IsAuthorOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class    = PostFilter
    search_fields      = ["title", "content"]
    ordering_fields    = ["created_at", "updated_at"]
    ordering           = ["-created_at"]
    lookup_field       = "slug"

    def get_queryset(self):
        """
        Public users see only published posts.
        Authenticated users additionally see their own drafts.
        """
        qs = (
            Post.objects
            .select_related("author", "category")
            .prefetch_related("tags")
        )

        user = self.request.user
        if self.action in ("list", "retrieve") and (not user or not user.is_authenticated):
            return qs.filter(status=Post.Status.PUBLISHED)

        if user and user.is_authenticated and not user.is_staff:
            # Authenticated non-staff: see published posts + own drafts
            from django.db.models import Q
            return qs.filter(Q(status=Post.Status.PUBLISHED) | Q(author=user))

        return qs  # staff / superuser see everything

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostDetailSerializer

    def get_throttles(self):
        if self.action == "create":
            return [ScopedRateThrottle()]
        return super().get_throttles()

    @property
    def throttle_scope(self):
        if self.action == "create":
            return "post_create"
        return None

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # ------------------------------------------------------------------
    # Extra action: /posts/<slug>/publish/
    # ------------------------------------------------------------------
    @extend_schema(summary="Publish a draft post (author only)", request=None, responses={200: PostDetailSerializer})
    @action(
        detail=True, methods=["post"], url_path="publish",
        permission_classes=[IsAuthenticated],
    )
    def publish(self, request, slug=None):
        post = self.get_object()
        if post.author != request.user:
            return Response({"detail": "You are not the author."}, status=status.HTTP_403_FORBIDDEN)
        post.status = Post.Status.PUBLISHED
        post.save()
        return Response(PostDetailSerializer(post, context={"request": request}).data)

    # ------------------------------------------------------------------
    # Extra action: /posts/<slug>/unpublish/
    # ------------------------------------------------------------------
    @extend_schema(summary="Revert a post to draft (author only)", request=None, responses={200: PostDetailSerializer})
    @action(
        detail=True, methods=["post"], url_path="unpublish",
        permission_classes=[IsAuthenticated],
    )
    def unpublish(self, request, slug=None):
        post = self.get_object()
        if post.author != request.user:
            return Response({"detail": "You are not the author."}, status=status.HTTP_403_FORBIDDEN)
        post.status = Post.Status.DRAFT
        post.save()
        return Response(PostDetailSerializer(post, context={"request": request}).data)
