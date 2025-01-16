# Generated by Django 5.1.4 on 2025-01-16 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EnergyData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_timestamp', models.BigIntegerField()),
                ('end_timestamp', models.BigIntegerField()),
                ('marketprice', models.FloatField()),
                ('unit', models.CharField(max_length=50)),
            ],
        ),
    ]
