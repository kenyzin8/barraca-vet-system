# Generated by Django 4.2 on 2023-10-02 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0042_alter_pet_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pet',
            name='original_weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='pet',
            name='weight',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='pettreatment',
            name='temperature',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='pettreatment',
            name='treatment_weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
