"""
Management command to create a sample wedding event.
"""
from datetime import date
from django.core.management.base import BaseCommand
from django.conf import settings
from src.events.models import Event


class Command(BaseCommand):
    help = 'Create a sample wedding event for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--code',
            type=str,
            default='andelka-anto',
            help='Event code (default: andelka-anto)'
        )
        parser.add_argument(
            '--name',
            type=str,
            default="Anđelka & Anto",
            help='Event name (default: Anđelka & Anto)'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing event with the same code'
        )

    def handle(self, *args, **options):
        code = options['code']
        name = options['name']
        overwrite = options['overwrite']

        # Check if event already exists
        existing_event = Event.objects.filter(code=code).first()
        
        if existing_event:
            if overwrite:
                self.stdout.write(
                    self.style.WARNING(f'Overwriting existing event: {existing_event.name}')
                )
                existing_event.name = name
                existing_event.description = (
                    "Dobrodošli na naše vjenčanje! Jako smo uzbuđeni što slavimo s vama. "
                    "Molimo vas podijelite svoje omiljene trenutke učitavanjem fotografija ispod."
                )
                existing_event.date = date(2026, 1, 3)
                existing_event.is_active = True
                existing_event.save()
                event = existing_event
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated event: {name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Event with code "{code}" already exists. '
                        f'Use --overwrite to update it.'
                    )
                )
                return
        else:
            # Create new event
            event = Event.objects.create(
                code=code,
                name=name,
                description=(
                    "Dobrodošli na naše vjenčanje! Jako smo uzbuđeni što slavimo s vama. "
                    "Molimo vas podijelite svoje omiljene trenutke učitavanjem fotografija ispod."
                ),
                date=date(2026, 1, 3),
                is_active=True
            )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created event: {name}')
            )

        self.stdout.write(f'  Code: {event.code}')
        self.stdout.write(f'  Access Token: {event.access_token}')
        
        # Get frontend URL from settings
        frontend_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        access_url = f"{frontend_url}/?token={event.access_token}"
        self.stdout.write(f'  Access URL: {access_url}')
