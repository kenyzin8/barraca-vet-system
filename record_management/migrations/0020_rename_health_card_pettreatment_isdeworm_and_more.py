# Generated by Django 4.2 on 2023-09-03 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0019_pettreatment_health_card'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pettreatment',
            old_name='health_card',
            new_name='isDeworm',
        ),
        migrations.AddField(
            model_name='pettreatment',
            name='isVaccine',
            field=models.BooleanField(default=False),
        ),
    ]
