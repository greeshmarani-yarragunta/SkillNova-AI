import os

from django.core.management.base import BaseCommand, CommandError
from accounts.models import User


class Command(BaseCommand):
    help = "Create or reset the production admin account"

    def handle(self, *args, **options):
        email = "admin@skillnova.ai"
        password = os.getenv("ADMIN_RESET_PASSWORD")

        if not password:
            raise CommandError(
                "ADMIN_RESET_PASSWORD environment variable is required."
            )

        admin = User.objects.filter(email=email).first()

        if admin is None:
            admin = User(
                username="admin",
                email=email,
                role="ADMIN",
                is_staff=True,
                is_superuser=True,
                is_active=True,
            )
            admin.set_password(password)
            admin.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin account {email} created successfully."
                )
            )
        else:
            admin.set_password(password)
            admin.role = "ADMIN"
            admin.is_staff = True
            admin.is_superuser = True
            admin.is_active = True
            admin.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin password reset successfully for {email}."
                )
            )