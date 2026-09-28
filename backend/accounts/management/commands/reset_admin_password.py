import os

from django.core.management.base import BaseCommand, CommandError
from accounts.models import User


class Command(BaseCommand):
    help = "Reset the production admin password"

    def handle(self, *args, **options):
        email = "admin@skillnova.ai"
        password = os.getenv("ADMIN_RESET_PASSWORD")

        if not password:
            raise CommandError("ADMIN_RESET_PASSWORD environment variable is required.")

        try:
            admin = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f"Admin account {email} does not exist.")

        admin.set_password(password)
        admin.role = "ADMIN"
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin password reset successfully for {email}"
            )
        )