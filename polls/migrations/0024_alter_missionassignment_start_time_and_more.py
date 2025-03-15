# Generated by Django 5.1.7 on 2025-03-12 07:00

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0023_remove_missiontarget_missions_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='missionassignment',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='开始时间'),
        ),
        migrations.AlterField(
            model_name='waypoint',
            name='reached_at',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='到达时间'),
        ),
    ]
