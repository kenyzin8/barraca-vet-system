# Generated by Django 4.2 on 2023-05-12 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0003_alter_pet_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='gender',
            field=models.CharField(default='None', max_length=10),
        ),
    ]
