# Generated by Django 4.2 on 2023-07-18 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing_management', '0002_alter_billing_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='billing',
            name='isActive',
            field=models.BooleanField(default=True),
        ),
    ]
