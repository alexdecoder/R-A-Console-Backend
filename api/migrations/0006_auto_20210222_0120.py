# Generated by Django 3.1.6 on 2021-02-22 06:20

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20210221_0342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_id',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
