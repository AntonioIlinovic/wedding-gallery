"""
Management command to create a sample wedding event.
"""
import os
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
        parser.add_argument(
            '--generate-qr',
            action='store_true',
            default=True,
            help='Generate QR code after creating event (default: True)'
        )
        parser.add_argument(
            '--no-qr',
            action='store_true',
            help='Skip QR code generation'
        )

    def handle(self, *args, **options):
        code = options['code']
        name = options['name']
        overwrite = options['overwrite']
        generate_qr = options['generate_qr'] and not options['no_qr']

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

        # Generate QR code if requested
        if generate_qr:
            self._generate_qr_code(event, frontend_url)

    def _generate_qr_code(self, event, frontend_url):
        """Generate QR code for the event."""
        try:
            import qrcode
        except ImportError:
            self.stdout.write(
                self.style.WARNING(
                    'qrcode library not available. Skipping QR code generation. '
                    'Install with: pip install qrcode[pil]'
                )
            )
            return

        output_dir = 'qr_codes'
        os.makedirs(output_dir, exist_ok=True)

        # Generate QR code URL
        qr_url = f"{frontend_url}/?token={event.access_token}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save QR code
        output_path = os.path.join(output_dir, f"{event.code}_qr.png")
        img.save(output_path)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated QR code for event "{event.name}"')
        )
        self.stdout.write(f'  QR code saved to: {output_path}')
        self.stdout.write(f'  QR code URL: {qr_url}')

