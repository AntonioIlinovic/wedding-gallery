"""
Management command to create a sample wedding event.
"""
from django.core.management.base import BaseCommand
from src.events.models import Event


class Command(BaseCommand):
    help = 'Create a sample wedding event for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--code',
            type=str,
            default='sample-wedding',
            help='Event code (default: sample-wedding)'
        )
        parser.add_argument(
            '--name',
            type=str,
            default="Sample Wedding",
            help='Event name (default: Sample Wedding)'
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
                    "Welcome to our wedding! We're so excited to celebrate with you. "
                    "Please share your favorite moments by uploading photos below."
                )
                existing_event.is_active = True
                existing_event.save()
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
        
        # Create new event
        event = Event.objects.create(
            code=code,
            name=name,
            description=(
                "Welcome to our wedding! We're so excited to celebrate with you. "
                "Please share your favorite moments by uploading photos below."
            ),
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created event: {name}')
        )
        self.stdout.write(f'  Code: {event.code}')
        self.stdout.write(f'  Access Token: {event.access_token}')
        self.stdout.write(
            f'  Access URL: http://localhost:3000/?token={event.access_token}'
        )

