# Generated by Django 4.2 on 2023-09-14 05:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0031_pettreatment_remainingcycle'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pettreatment',
            name='remainingCycle',
        ),
    ]
