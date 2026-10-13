import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the initial Wagtail admin user from environment variables, if configured."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")

        if not (username and email and password):
            self.stdout.write("Skipping initial admin creation; credentials are not all set.")
            return

        user_model = get_user_model()
        if user_model.objects.filter(**{user_model.USERNAME_FIELD: username}).exists():
            self.stdout.write(f"Initial admin '{username}' already exists; leaving it unchanged.")
            return

        user_model.objects.create_superuser(
            **{user_model.USERNAME_FIELD: username},
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Created initial Wagtail admin '{username}'."))
