# Generated migration for Photo model

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_key', models.CharField(help_text='Key/path of the file in object storage (S3/Minio).', max_length=512)),
                ('original_filename', models.CharField(blank=True, max_length=255)),
                ('uploaded_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('file_size', models.BigIntegerField(blank=True, null=True)),
                ('content_type', models.CharField(blank=True, max_length=255)),
                ('thumbnail_key', models.CharField(blank=True, help_text='Optional key/path for a thumbnail version of the image.', max_length=512)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='events.event')),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),
    ]

