# Generated by Django 3.1.6 on 2021-02-18 00:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='jobs',
            field=models.ManyToManyField(blank=True, to='api.Job'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('5f554fb3-f174-4dbf-b1c8-02092266eabc'), unique=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_uuid',
            field=models.UUIDField(default=uuid.UUID('e646e9d1-127b-4d0d-8e0e-bb77cf8c42df'), unique=True),
        ),
    ]
