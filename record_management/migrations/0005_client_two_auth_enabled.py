# Generated by Django 4.2 on 2023-04-18 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0004_alter_client_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='two_auth_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
