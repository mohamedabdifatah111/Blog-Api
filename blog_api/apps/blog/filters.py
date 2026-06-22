import django_filters
from .models import Post


class PostFilter(django_filters.FilterSet):
    """
    Declarative filter set for the Post list endpoint.

    Supported query params:
      ?status=published
      ?category=<id>
      ?tags=<id>          (exact match on any tag)
      ?author=<id>
      ?created_after=YYYY-MM-DD
      ?created_before=YYYY-MM-DD
    """

    status         = django_filters.ChoiceFilter(choices=Post.Status.choices)
    category       = django_filters.NumberFilter(field_name="category__id")
    category_slug  = django_filters.CharFilter(field_name="category__slug", lookup_expr="iexact")
    tags           = django_filters.NumberFilter(field_name="tags__id")
    author         = django_filters.NumberFilter(field_name="author__id")
    created_after  = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model  = Post
        fields = ["status", "category", "category_slug", "tags", "author"]
