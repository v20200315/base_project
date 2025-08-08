from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Tenant, Membership, CustomUser
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    TenantSerializer,
    AddMemberSerializer,
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"message": "需要用户名和密码。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "用户名或密码无效。"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "成功退出。"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TenantViewSet(viewsets.ModelViewSet):
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        print(self.request.user)
        return Tenant.objects.filter(memberships__user=self.request.user).distinct()

    def perform_create(self, serializer):
        tenant = serializer.save()
        Membership.objects.create(user=self.request.user, tenant=tenant, role="OWNER")


class AddMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, tenant_id):
        serializer = AddMemberSerializer(data=request.data)
        if serializer.is_valid():
            try:
                membership = Membership.objects.get(
                    user=request.user, tenant_id=tenant_id
                )
            except Membership.DoesNotExist:
                return Response(
                    {"message": "你现在还不属于这个租户。"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if membership.role not in ["OWNER", "ADMIN"]:
                return Response(
                    {"message": "你现在没有权限添加用户到租户。"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user_to_add = CustomUser.objects.get(
                email=serializer.validated_data["email"]
            )
            role_to_assign = serializer.validated_data["role"]

            exists = Membership.objects.filter(
                user=user_to_add, tenant_id=tenant_id
            ).exists()
            if exists:
                return Response(
                    {"message": "所需添加的用户已经属于租户。"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Membership.objects.create(
                user=user_to_add, tenant_id=tenant_id, role=role_to_assign
            )
            return Response(
                {"message": f"用户 {user_to_add.email} 添加为 {role_to_assign}."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, tenant_id, user_id):
        try:
            # 当前请求用户的 Membership（检查权限）
            requester_membership = Membership.objects.get(
                user=request.user, tenant_id=tenant_id
            )
        except Membership.DoesNotExist:
            return Response(
                {"message": "你现在还不属于这个租户。"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if requester_membership.role != "OWNER":
            return Response(
                {"message": "只有租户的拥有者才能移除成员。"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            # 要被移除的成员（不能移除自己）
            if str(request.user.id) == user_id:
                return Response(
                    {"message": "不能移除自己作为租户拥有者。"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            member_to_remove = Membership.objects.get(
                user_id=user_id, tenant_id=tenant_id
            )
        except Membership.DoesNotExist:
            return Response(
                {"message": "该用户不是此租户的成员。"},
                status=status.HTTP_404_NOT_FOUND,
            )

        member_to_remove.delete()

        return Response(
            {"message": "成员已成功移除。"},
            status=status.HTTP_204_NO_CONTENT,
        )
