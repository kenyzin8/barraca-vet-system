# Generated by Django 4.2 on 2023-11-29 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0046_laboratorytests'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='laboratorytests',
            options={'verbose_name_plural': 'Laboratory Tests'},
        ),
        migrations.AddField(
            model_name='client',
            name='isWalkIn',
            field=models.BooleanField(default=False),
        ),
    ]
