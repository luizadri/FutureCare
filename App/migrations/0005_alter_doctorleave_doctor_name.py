# Generated by Django 5.0.1 on 2024-02-20 16:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0004_appoinment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorleave',
            name='doctor_name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='App.doctors'),
        ),
    ]