# Generated by Django 4.2 on 2023-05-12 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0004_client_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='None', max_length=10),
        ),
    ]
