from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction


User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the DB'

    def _get_or_create_admin(self):
        try:
            admin = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin = User(**{
                "username": "admin",
                "password": make_password("admin"),
                "is_staff": True,
                "is_superuser": True
            })
            admin.save()
        return admin

    @transaction.atomic
    def handle(self, *a, **kwa):
        self._get_or_create_admin()
