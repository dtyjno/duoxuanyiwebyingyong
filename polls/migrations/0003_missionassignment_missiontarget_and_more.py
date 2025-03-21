# Generated by Django 5.1.6 on 2025-03-03 15:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_drone'),
    ]

    operations = [
        migrations.CreateModel(
            name='MissionAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(verbose_name='开始时间')),
                ('end_time', models.DateTimeField(null=True, verbose_name='结束时间')),
                ('status', models.IntegerField(choices=[(0, '待执行'), (1, '执行中'), (2, '已完成'), (3, '已失败')], default=0)),
                ('video_recording', models.FileField(max_length=255, upload_to='missions/videos/%Y/%m/%d/', verbose_name='任务录像')),
                ('thumbnail', models.ImageField(null=True, upload_to='missions/thumbs/%Y/%m/%d/', verbose_name='视频缩略图')),
                ('drone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='polls.drone')),
            ],
            options={
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='MissionTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='目标名称')),
                ('description', models.TextField(blank=True, verbose_name='目标描述')),
                ('longitude', models.FloatField(verbose_name='经度')),
                ('latitude', models.FloatField(verbose_name='纬度')),
                ('altitude', models.FloatField(verbose_name='海拔高度')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('drones', models.ManyToManyField(related_name='missions', through='polls.MissionAssignment', to='polls.drone')),
            ],
        ),
        migrations.AddField(
            model_name='missionassignment',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='polls.missiontarget'),
        ),
        migrations.AddIndex(
            model_name='missiontarget',
            index=models.Index(fields=['longitude', 'latitude'], name='polls_missi_longitu_30adf9_idx'),
        ),
        migrations.AddIndex(
            model_name='missiontarget',
            index=models.Index(fields=['-created_at'], name='polls_missi_created_a95264_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='missionassignment',
            unique_together={('drone', 'target')},
        ),
    ]
