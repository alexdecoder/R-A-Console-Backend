# Generated by Django 3.1.6 on 2021-03-26 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_contactrequest_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactrequest',
            name='email',
            field=models.CharField(max_length=75),
        ),
    ]
