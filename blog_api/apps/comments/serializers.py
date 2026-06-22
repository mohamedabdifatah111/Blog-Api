from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from .models import Comment


class ReplySerializer(serializers.ModelSerializer):
    """Serializer for one-level deep replies (children of top-level comments)."""

    user = UserPublicSerializer(read_only=True)

    class Meta:
        model  = Comment
        fields = ("id", "user", "body", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "user", "is_active", "created_at", "updated_at")


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for top-level comments.
    Includes nested `replies` (read-only).
    """

    user    = UserPublicSerializer(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(read_only=True, source="post")

    class Meta:
        model  = Comment
        fields = (
            "id", "post_id", "user", "parent",
            "body", "is_active", "replies",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "user", "is_active", "replies", "created_at", "updated_at")

    def validate_parent(self, value):
        """
        Restrict replies to one level of nesting:
        a reply's parent must be a top-level comment (no grandchildren).
        """
        if value and value.parent is not None:
            raise serializers.ValidationError(
                "Replies to replies are not allowed. Reply to the top-level comment instead."
            )
        return value

    def validate(self, attrs):
        """Ensure parent comment belongs to the same post."""
        parent = attrs.get("parent")
        # post is injected by the view via perform_create, not from request body
        # Validation happens at object level; we just check parent post consistency here
        # when parent is given and post is already in context
        request = self.context.get("request")
        if parent and request:
            view = self.context.get("view")
            post_slug = view.kwargs.get("post_slug") if view else None
            if post_slug and str(parent.post.slug) != str(post_slug):
                raise serializers.ValidationError(
                    {"parent": "Parent comment does not belong to this post."}
                )
        return attrs
