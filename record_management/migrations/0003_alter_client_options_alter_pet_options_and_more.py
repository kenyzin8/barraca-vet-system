# Generated by Django 4.2 on 2023-04-04 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0002_pet'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'verbose_name_plural': 'Clients'},
        ),
        migrations.AlterModelOptions(
            name='pet',
            options={'verbose_name_plural': 'Pets'},
        ),
        migrations.RemoveField(
            model_name='client',
            name='middle_name',
        ),
    ]
