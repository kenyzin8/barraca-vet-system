# Generated by Django 4.2 on 2023-09-14 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0029_labresult_isactive'),
    ]

    operations = [
        migrations.AddField(
            model_name='pettreatment',
            name='hasAppointmentCycle',
            field=models.BooleanField(default=False),
        ),
    ]
