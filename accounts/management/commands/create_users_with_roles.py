import uuid
from django.core.management.base import BaseCommand
from accounts.models import Tenant, CustomUser
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = "在指定租户下批量创建不同角色的用户"

    def add_arguments(self, parser):
        parser.add_argument("tenant_name", type=str, help="租户名称")
        parser.add_argument("--count", type=int, default=3, help="每种角色创建用户数量")

    def handle(self, *args, **options):
        tenant_name = options["tenant_name"]
        count = options["count"]

        tenant, created = Tenant.objects.get_or_create(name=tenant_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"创建了新租户: {tenant_name}"))

        roles = ["OWNER", "ADMIN", "USER"]

        for role in roles:
            for i in range(1, count + 1):
                username = f"{role.lower()}_{i}_{tenant_name.lower()}"
                email = f"{username}@example.com"
                if CustomUser.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f"用户 {username} 已存在，跳过")
                    )
                    continue
                user = CustomUser.objects.create(
                    username=username,
                    email=email,
                    tenant=tenant,
                    role=role,
                    password=make_password("DefaultPass123"),  # 默认密码
                )
                self.stdout.write(
                    self.style.SUCCESS(f"创建用户 {username} 角色：{role}")
                )

        self.stdout.write(self.style.SUCCESS("所有用户创建完成"))
