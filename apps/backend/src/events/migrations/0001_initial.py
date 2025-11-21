# Generated migration for Event model

from django.db import migrations, models
import django.utils.timezone
from secrets import token_urlsafe


def generate_access_token():
    """Generate a random access token."""
    return token_urlsafe(32)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.SlugField(help_text='Short identifier for this event (used in storage paths).', max_length=50, unique=True)),
                ('name', models.CharField(help_text='Display name of the event.', max_length=255)),
                ('access_token', models.CharField(editable=False, help_text='Secret token embedded in the QR code for guest access.', max_length=128, unique=True)),
                ('description', models.TextField(blank=True, help_text='Welcome text shown on the landing page for this event.')),
                ('date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-date', '-created_at'],
            },
        ),
    ]

