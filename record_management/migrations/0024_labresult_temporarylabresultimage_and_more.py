# Generated by Django 4.2 on 2023-09-08 10:11

from django.db import migrations, models
import django.db.models.deletion
import record_management.models


class Migration(migrations.Migration):

    dependencies = [
        ('record_management', '0023_remove_prescriptionmedicines_form'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_name', models.CharField(blank=True, max_length=100, null=True)),
                ('result_image', models.ImageField(blank=True, default='None', null=True, upload_to='public/images/', validators=[record_management.models.validate_image_extension])),
            ],
            options={
                'verbose_name_plural': 'Lab Results',
            },
        ),
        migrations.CreateModel(
            name='TemporaryLabResultImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='public/temp_images/', validators=[record_management.models.validate_image_extension])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='pettreatment',
            name='medical_images',
        ),
        migrations.AddField(
            model_name='pettreatment',
            name='symptoms',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.RemoveField(
            model_name='pettreatment',
            name='lab_results',
        ),
        migrations.CreateModel(
            name='LabResultsTreatment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lab_result', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='record_management.labresult')),
                ('pet_treatment', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='record_management.pettreatment')),
            ],
        ),
        migrations.AddField(
            model_name='pettreatment',
            name='lab_results',
            field=models.ManyToManyField(blank=True, to='record_management.labresult'),
        ),
    ]
