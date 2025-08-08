from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    TenantViewSet,
    AddMemberView,
    RemoveMemberView,
)

router = DefaultRouter()
router.register(r"tenants", TenantViewSet, basename="tenant")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
    path(
        "tenants/<uuid:tenant_id>/add-member/",
        AddMemberView.as_view(),
        name="add_member",
    ),
    path(
        "tenants/<uuid:tenant_id>/remove-member/<uuid:user_id>/",
        RemoveMemberView.as_view(),
        name="remove_member",
    ),
]
