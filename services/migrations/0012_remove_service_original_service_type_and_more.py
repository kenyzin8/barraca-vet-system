# Generated by Django 4.2 on 2023-07-06 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_alter_service_previous_version_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='original_service_type',
        ),
        migrations.AddField(
            model_name='service',
            name='original_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.service'),
        ),
    ]
