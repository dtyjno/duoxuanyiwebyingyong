# Generated by Django 5.1.7 on 2025-03-12 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0022_remove_missionassignment_targets_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='missiontarget',
            name='missions',
        ),
        migrations.AddField(
            model_name='missionassignment',
            name='targets',
            field=models.ManyToManyField(blank=True, related_name='assigned_missions', to='polls.missiontarget'),
        ),
        migrations.RemoveField(
            model_name='drone',
            name='assignments',
        ),
        migrations.AddField(
            model_name='drone',
            name='assignments',
            field=models.ManyToManyField(blank=True, related_name='assigned_drones', to='polls.missionassignment', verbose_name='任务分配'),
        ),
    ]
