# Generated by Django 4.2 on 2023-12-06 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0049_rename_lab_test_unit_description_laboratorytests_lab_test_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='laboratorytests',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
