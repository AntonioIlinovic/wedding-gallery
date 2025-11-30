"""
Management command to seed initial data for the application.

This command calls other management commands to set up sample/test data.
It only creates data if it doesn't already exist.
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand
from src.events.models import Event


class Command(BaseCommand):
    help = 'Seed initial data for the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-events',
            action='store_true',
            help='Skip creating sample events'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force seeding even if data already exists'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        # Create sample wedding event
        if not options['skip_events']:
            event_code = 'andelka-anto'
            event_exists = Event.objects.filter(code=event_code).exists()
            
            if event_exists and not options['force']:
                self.stdout.write(
                    self.style.WARNING(
                        f'Event with code "{event_code}" already exists. '
                        'Skipping event creation. Use --force to overwrite.'
                    )
                )
            else:
                self.stdout.write('Creating wedding event "Anđelka & Anto"...')
                try:
                    cmd_args = [
                        'create_sample_event',
                        '--code', event_code,
                        '--name', 'Anđelka & Anto',
                    ]
                    if options['force']:
                        cmd_args.append('--overwrite')
                    
                    call_command(*cmd_args)
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to create event: {e}')
                    )

        self.stdout.write(self.style.SUCCESS('Data seeding completed!'))

