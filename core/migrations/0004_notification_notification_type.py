# Generated by Django 4.2 on 2023-09-07 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_smslogs_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('critical', 'Critical Level'), ('out_of_stock', 'Out of Stock'), ('expired', 'Expired')], default='none', max_length=50),
        ),
    ]
