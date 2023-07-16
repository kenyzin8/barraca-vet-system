# Generated by Django 4.2 on 2023-07-16 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment_management', '0003_doctorschedule'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='doctorschedule',
            options={'verbose_name': 'Doctor Schedule', 'verbose_name_plural': 'Doctor Schedules'},
        ),
        migrations.AddField(
            model_name='appointment',
            name='daily_reminder_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appointment',
            name='weekly_reminder_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('rebook', 'Rebook'), ('cancelled', 'Cancelled'), ('done', 'Done'), ('petdeleted', 'Pet Deleted')], max_length=10),
        ),
        migrations.AlterField(
            model_name='doctorschedule',
            name='timeOfTheDay',
            field=models.CharField(choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('whole_day', 'Whole Day')], max_length=10),
        ),
    ]
