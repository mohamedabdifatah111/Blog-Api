from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering         = ["-date_joined"]
    list_display     = ("email", "first_name", "last_name", "is_staff", "is_active", "date_joined")
    list_filter      = ("is_staff", "is_active")
    search_fields    = ("email", "first_name", "last_name")
    readonly_fields  = ("date_joined", "last_login")

    fieldsets = (
        (None,             {"fields": ("email", "password")}),
        (_("Personal"),    {"fields": ("first_name", "last_name", "bio", "avatar")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Dates"),       {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "password1", "password2", "first_name", "last_name"),
        }),
    )
