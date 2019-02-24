# Generated by Django 2.2a1 on 2019-02-16 12:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analyses', '0002_auto_20190215_1910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analyses',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='analyses_for_patient', to='patients.Patient'),
        ),
    ]