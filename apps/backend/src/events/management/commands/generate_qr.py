"""
Management command to generate QR codes for events.
"""
import os
from django.core.management.base import BaseCommand, CommandError
from src.events.models import Event


class Command(BaseCommand):
    help = 'Generate a QR code for an event'

    def add_arguments(self, parser):
        parser.add_argument(
            'event_code',
            type=str,
            help='The event code to generate QR code for'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='qr_codes',
            help='Output directory for QR code images (default: qr_codes)'
        )
        parser.add_argument(
            '--frontend-url',
            type=str,
            default='http://localhost:3000',
            help='Frontend URL to embed in QR code (default: http://localhost:3000)'
        )

    def handle(self, *args, **options):
        event_code = options['event_code']
        output_dir = options['output']
        frontend_url = options['frontend_url']

        try:
            event = Event.objects.get(code=event_code)
        except Event.DoesNotExist:
            raise CommandError(f'Event with code "{event_code}" does not exist')

        # Import qrcode here so it's only required when using this command
        try:
            import qrcode
        except ImportError:
            raise CommandError(
                'qrcode library is required. Install it with: pip install qrcode[pil]'
            )

        # Create output directory if it doesn't exist
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
        output_path = os.path.join(output_dir, f"{event_code}_qr.png")
        img.save(output_path)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated QR code for event "{event.name}"')
        )
        self.stdout.write(f'QR code saved to: {output_path}')
        self.stdout.write(f'QR code URL: {qr_url}')
        self.stdout.write(f'Access token: {event.access_token}')

