from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Creates an admin superuser if none exists'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Creating superuser {username} with password {password}"))
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {username} already exists. Skipping creation.'))
