from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Tenant, Membership


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = (
        "id",
        "username",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important Dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    model = Tenant
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    model = Membership
    list_display = ("id", "tenant", "user", "role", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("tenant__name", "user__username", "user__email")
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)
