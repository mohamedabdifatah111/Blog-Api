from django.conf import settings
from django.db import models


class Comment(models.Model):
    """
    Self-referencing model for nested (threaded) comments on blog posts.

    Top-level comments have `parent=None`.
    Replies have `parent=<parent_comment>`.
    Nesting is intentionally kept to 1 level of indirection in the API
    (replies to replies are stored but the serializer flattens to 2 levels).
    """

    post    = models.ForeignKey(
        "blog.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent  = models.ForeignKey(
        "self",
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    body       = models.TextField()
    is_active  = models.BooleanField(default=True)  # soft delete / moderation
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user} on '{self.post}'"
