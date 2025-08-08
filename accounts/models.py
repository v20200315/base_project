import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_owner(self):
        """获取租户的 OWNER 用户"""
        membership = self.memberships.filter(role="OWNER").first()
        return membership.user if membership else None


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)  # 每个用户邮箱唯一
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)

    def __str__(self):
        return self.email

    def get_role(self, tenant):
        """获取用户在指定租户下的角色"""
        membership = self.memberships.filter(tenant=tenant).first()
        return membership.role if membership else None

    def is_admin(self, tenant):
        """是否在某租户下为 ADMIN 或 OWNER"""
        role = self.get_role(tenant)
        return role in ["OWNER", "ADMIN"]


class Membership(models.Model):
    ROLE_CHOICES = [
        ("OWNER", "Owner"),
        ("ADMIN", "Admin"),
        ("MEMBER", "Member"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="MEMBER")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "user")

    def __str__(self):
        return f"{self.user.username} in {self.tenant.name} as {self.role}"
