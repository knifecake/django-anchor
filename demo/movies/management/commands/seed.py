from typing import Any
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Seeds the database with sample data"

    def handle(self, *args: Any, **options: Any) -> str | None:
        User: type = get_user_model()
        admin, _created = User.objects.update_or_create(
            username="admin", defaults={"is_superuser": True, "is_staff": True}
        )

        if not admin.check_password("admin"):
            admin.set_password("admin")
            admin.save()
