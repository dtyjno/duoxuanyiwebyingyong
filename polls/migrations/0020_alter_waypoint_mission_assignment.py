# Generated by Django 5.1.7 on 2025-03-12 02:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0019_remove_drone_assignments_drone_assignments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waypoint',
            name='mission_assignment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waypoints', to='polls.missionassignment'),
        ),
    ]
