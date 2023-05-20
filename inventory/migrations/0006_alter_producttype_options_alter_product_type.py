# Generated by Django 4.2 on 2023-05-20 12:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_producttype_alter_product_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='producttype',
            options={'verbose_name': 'Product Type', 'verbose_name_plural': 'Product Types'},
        ),
        migrations.AlterField(
            model_name='product',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.producttype'),
        ),
    ]
