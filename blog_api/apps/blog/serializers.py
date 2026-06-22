from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from .models import Category, Tag, Post


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    """Full serializer — used for CRUD by admin."""

    post_count = serializers.IntegerField(source="posts.count", read_only=True)

    class Meta:
        model  = Category
        fields = ("id", "name", "slug", "description", "post_count", "created_at")
        read_only_fields = ("id", "slug", "created_at")


class CategoryMinimalSerializer(serializers.ModelSerializer):
    """Nested read-only representation used inside PostSerializer."""

    class Meta:
        model  = Category
        fields = ("id", "name", "slug")


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------

class TagSerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField(source="posts.count", read_only=True)

    class Meta:
        model  = Tag
        fields = ("id", "name", "slug", "post_count")
        read_only_fields = ("id", "slug")


class TagMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tag
        fields = ("id", "name", "slug")


# ---------------------------------------------------------------------------
# Post
# ---------------------------------------------------------------------------

class PostListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list endpoints.
    Avoids returning heavy `content` field.
    """

    author   = UserPublicSerializer(read_only=True)
    category = CategoryMinimalSerializer(read_only=True)
    tags     = TagMinimalSerializer(many=True, read_only=True)

    class Meta:
        model  = Post
        fields = (
            "id", "title", "slug", "banner_image", "status",
            "author", "category", "tags",
            "created_at", "updated_at",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for retrieve / create / update.
    - `author` is auto-set to request.user on create.
    - `category` and `tags` accept PKs on write, return nested objects on read.
    """

    author   = UserPublicSerializer(read_only=True)
    category = CategoryMinimalSerializer(read_only=True)
    tags     = TagMinimalSerializer(many=True, read_only=True)

    # Write-only fields to accept FK/M2M PKs
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source="tags",
        write_only=True,
        many=True,
        required=False,
    )

    class Meta:
        model  = Post
        fields = (
            "id", "title", "slug", "content", "banner_image",
            "status", "author",
            "category", "category_id",
            "tags", "tag_ids",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "slug", "author", "created_at", "updated_at")

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        post = Post.objects.create(**validated_data)
        post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance
