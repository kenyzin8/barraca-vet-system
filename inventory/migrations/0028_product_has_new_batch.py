# Generated by Django 4.2 on 2023-10-29 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0027_alter_product_form_alter_product_volume_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='has_new_batch',
            field=models.BooleanField(default=False),
        ),
    ]
