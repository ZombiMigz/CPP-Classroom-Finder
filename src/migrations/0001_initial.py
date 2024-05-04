# Generated by Django 5.0.4 on 2024-05-03 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('building', models.CharField(max_length=30)),
                ('room', models.CharField(max_length=30)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('day_of_the_week', models.CharField(max_length=2)),
            ],
        ),
    ]