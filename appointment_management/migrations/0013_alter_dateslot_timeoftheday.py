# Generated by Django 4.2 on 2023-09-16 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment_management', '0012_dateslot_timeoftheday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dateslot',
            name='timeOfTheDay',
            field=models.CharField(choices=[('morning', 'Morning'), ('afternoon', 'Afternoon')], default='morning', max_length=10),
        ),
    ]
