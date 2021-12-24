# Generated by Django 3.1.6 on 2021-02-21 08:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20210221_0245'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_category',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='customer',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('758f20d3-5e9e-458d-8417-22ce0c1bb86f'), unique=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_uuid',
            field=models.UUIDField(default=uuid.UUID('61173e9b-541c-4f36-b5a7-014da6e2a6a9'), unique=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_id',
            field=models.UUIDField(default=uuid.UUID('516cfb15-d8e0-4676-bc6e-6cc0a443ac12'), unique=True),
        ),
    ]
