# Generated by Django 4.2 on 2023-05-23 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_notification'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
