# Generated by Django 4.2 on 2023-06-15 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_remove_service_previous_version_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='previous_version',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='updated_version',
            field=models.TextField(blank=True, null=True),
        ),
    ]
