# Generated by Django 4.2 on 2023-07-18 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0015_serviceremarks_alter_service_remarks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='remarks',
            field=models.CharField(choices=[('without_medicine', 'Without Medicine'), ('with_medicine', 'With Medicine')], max_length=20),
        ),
        migrations.DeleteModel(
            name='ServiceRemarks',
        ),
    ]
