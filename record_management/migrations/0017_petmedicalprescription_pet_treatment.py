# Generated by Django 4.2 on 2023-09-01 04:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0016_alter_pettreatment_medical_images_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='petmedicalprescription',
            name='pet_treatment',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='record_management.pettreatment'),
        ),
    ]
