# Generated by Django 4.2 on 2023-10-28 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing_management', '0008_billing_ispaid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billing',
            name='isPaid',
            field=models.BooleanField(default=True),
        ),
    ]
