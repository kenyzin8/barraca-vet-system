# Generated by Django 4.2 on 2023-09-14 06:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appointment_management', '0011_alter_appointment_purpose'),
        ('record_management', '0035_pettreatment_total_cycle'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pettreatment',
            old_name='hasAppointmentCycle',
            new_name='hasMultipleCycles',
        ),
        migrations.RemoveField(
            model_name='pettreatment',
            name='cycle_end_date',
        ),
        migrations.RemoveField(
            model_name='pettreatment',
            name='cycle_number',
        ),
        migrations.RemoveField(
            model_name='pettreatment',
            name='total_cycle',
        ),
        migrations.CreateModel(
            name='TreatmentCycle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cycle_number', models.PositiveIntegerField()),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appointment_management.appointment')),
                ('pet_treatment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cycles', to='record_management.pettreatment')),
            ],
            options={
                'unique_together': {('pet_treatment', 'cycle_number')},
            },
        ),
    ]
