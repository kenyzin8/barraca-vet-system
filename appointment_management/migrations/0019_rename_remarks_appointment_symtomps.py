# Generated by Django 4.2 on 2023-11-27 01:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointment_management', '0018_appointment_remarks'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='remarks',
            new_name='symtomps',
        ),
    ]
