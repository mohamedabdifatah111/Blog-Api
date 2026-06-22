"""
Root URL configuration for blog_api.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

api_v1_patterns = [
    path("auth/",     include("apps.accounts.urls", namespace="accounts")),
    path("blog/",     include("apps.blog.urls",     namespace="blog")),
    path("comments/", include("apps.comments.urls", namespace="comments")),
]

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/", include((api_v1_patterns, "api_v1"))),

    # OpenAPI schema & docs
    path("api/schema/",        SpectacularAPIView.as_view(),       name="schema"),
    path("api/docs/swagger/",  SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/",    SpectacularRedocView.as_view(url_name="schema"),   name="redoc"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
