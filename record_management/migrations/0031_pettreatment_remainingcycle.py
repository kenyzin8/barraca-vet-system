# Generated by Django 4.2 on 2023-09-14 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0030_pettreatment_hasappointmentcycle'),
    ]

    operations = [
        migrations.AddField(
            model_name='pettreatment',
            name='remainingCycle',
            field=models.IntegerField(default=0),
        ),
    ]
