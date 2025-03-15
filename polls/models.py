import datetime

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User, Group

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text
# Compare this snippet from polls/urls.py:

class Drone(models.Model):
    

    DOCK_STATUS_CHOICES = [
        (0, '空闲中'),
        (1, '现场调试'),
        (2, '远程调试'),
        (3, '固件升级中'),
        (4, '作业中'),
        (-1, '离线'),
    ]

    # 用户与无人机的一对多关系（使用Django内置User模型）
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drones')
    
    # 任务与无人机的一对多关系
    # assignments = models.ForeignKey(
    #     'MissionAssignment',
    #     on_delete=models.CASCADE,
    #     related_name='drones'
    # )
    assignments = models.ManyToManyField(
        'MissionAssignment',
        related_name='assigned_drones',  # Changed from 'drones' to avoid confusion
        blank=True,
        verbose_name='任务分配'
    )


    # 设备信息
    name = models.CharField(max_length=100, verbose_name='设备名称')
    dock_sn = models.CharField(max_length=100, verbose_name='机场SN')
    drone_sn = models.CharField(max_length=100, verbose_name='无人机SN')
    
    # 定位信息
    longitude = models.FloatField(verbose_name='经度')
    latitude = models.FloatField(verbose_name='纬度')
    height = models.FloatField(verbose_name='高度')
    elevation = models.FloatField(verbose_name='相对起飞点高度')
    
    # 运动状态
    horizontal_speed = models.FloatField(verbose_name='水平速度')
    vertical_speed = models.FloatField(verbose_name='垂直速度')
    
    # 姿态信息
    attitude_pitch = models.FloatField(verbose_name='俯仰轴角度')
    attitude_roll = models.FloatField(verbose_name='横滚轴角度')
    attitude_head = models.FloatField(verbose_name='机头朝向角度')
    
    # 设备状态
    capacity_percent = models.FloatField(verbose_name='电池电量')
    dock_status = models.IntegerField(choices=DOCK_STATUS_CHOICES, verbose_name='设备状态')
    
    # 云台信息
    gimbal_yaw = models.FloatField(verbose_name='云台偏航轴角度')
    zoom_factor = models.IntegerField(verbose_name='云台变焦倍数')
    gimbal_pitch = models.FloatField(verbose_name='云台俯仰轴角度')
    
    # 时间信息
    time_stamp = models.BigIntegerField(verbose_name='时间戳')
    
    # 自动维护字段
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # base_url: "https://all.xinkongan.com"  # 替换为实际的API基础地址
    app_id = models.CharField(verbose_name="appid", 
                                max_length=100, 
                                # default="0019f03b-b23b-427b-a924-6486b14e9f07"
                            )
    app_secret = models.CharField(verbose_name="appsecret",
                                    max_length=100,
                                    # default="7736ae85-60d9-48a1-aa43-48ba23c18a89"
                                )
    
    class Meta:
        verbose_name = '无人机'
        verbose_name_plural = '无人机管理'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['name']),
            models.Index(fields=['dock_status']),
            models.Index(fields=['time_stamp']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_dock_status_display()})-{self.assignments.name}"

class MissionTarget(models.Model):
    STATUS_CHOICES = [
        (0, '待执行'),
        (1, '执行中'),
        (2, '已完成'),
        (3, '已失败')
    ]

    # 基础信息
    name = models.CharField(max_length=100, verbose_name="目标名称")
    description = models.TextField(verbose_name="目标描述", blank=True)
    
    # 地理信息
    longitude = models.FloatField(verbose_name="经度", null=True, blank=True)
    latitude = models.FloatField(verbose_name="纬度", null=True, blank=True)
    altitude = models.FloatField(verbose_name="海拔高度", null=True, blank=True)
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '任务目标'
        verbose_name_plural = '任务目标管理'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['longitude', 'latitude']),
            models.Index(fields=['-created_at'])
        ]
    
    def __str__(self):
        return f"{self.name}-{self.latitude},{self.longitude}(ID: {self.id})"

class MissionAssignment(models.Model):
    targets = models.ManyToManyField(
        'MissionTarget',
        related_name='assigned_missions',
        blank=True
    )
    
    # 任务执行详情
    name = models.CharField(max_length=100, verbose_name="任务名称", blank=True, null=True)
    start_time = models.DateTimeField(verbose_name="开始时间", default=timezone.now,)
    end_time = models.DateTimeField(verbose_name="结束时间", null=True)
    status = models.IntegerField(choices=MissionTarget.STATUS_CHOICES, default=0, verbose_name="任务状态")
    
    # 媒体记录
    video_recording = models.FileField(
        upload_to='missions/videos/%Y/%m/%d/',
        verbose_name="任务录像",
        max_length=255,
        null=True,
        blank=True
    )
    thumbnail = models.ImageField(
        upload_to='missions/thumbs/%Y/%m/%d/',
        verbose_name="视频缩略图",
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = '任务分配'
        verbose_name_plural = '任务分配管理'
        ordering = ['-start_time']

    def save(self, *args, **kwargs):
        # 如果没有提供名称，自动生成一个
        if not self.name:
            timestamp = timezone.now().strftime('%Y%m%d_%H%M')
            self.name = f"任务_{timestamp}"

        # 如果是新创建的任务，设置开始时间
        if not self.pk:  # 新对象的主键为None
            self.start_time = timezone.now()

        # 如果状态变更为已完成或已失败，且结束时间未设置
        if self.status in [2, 3] and not self.end_time:
            self.end_time = timezone.now()

        super().save(*args, **kwargs)

    def mark_as_started(self):
        """将任务标记为执行中"""
        self.status = 1
        self.save()
        return self.status

    def mark_as_completed(self):
        """将任务标记为已完成"""
        self.status = 2
        self.end_time = timezone.now()
        self.save()

    def mark_as_failed(self):
        """将任务标记为失败"""
        self.status = 3
        self.end_time = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.name}{self.id}({self.get_status_display()})"

# ...existing code...

class WayPoint(models.Model):
    WAYPOINT_TYPE_CHOICES = [
        (0, '起飞点'),
        (1, '途经点'),
        (2, '任务点'),
        (3, '返航点')
    ]
    
    drone = models.ForeignKey(
        'Drone',
        on_delete=models.CASCADE,
        related_name='waypoints'
    )
    
    mission_assignment = models.ForeignKey(
        'MissionAssignment',
        on_delete=models.CASCADE,
        related_name='waypoints',
        null=True,
        blank=True
    )

    # 位置信息
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="经度")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="纬度")
    height = models.FloatField(verbose_name='高度')
    elevation = models.FloatField(verbose_name='相对起飞点高度')
    
    # 运动状态
    horizontal_speed = models.FloatField(verbose_name='水平速度')
    vertical_speed = models.FloatField(verbose_name='垂直速度')
    
    # 姿态信息
    attitude_pitch = models.FloatField(verbose_name='俯仰轴角度')
    attitude_roll = models.FloatField(verbose_name='横滚轴角度')
    attitude_head = models.FloatField(verbose_name='机头朝向角度')
    
    
    # 航点类型和执行动作
    # waypoint_type = models.IntegerField(
    #     choices=WAYPOINT_TYPE_CHOICES,
    #     default=1,
    #     verbose_name="航点类型"
    # )
    # heading = models.FloatField(
    #     verbose_name="航向角",
    #     default=0,
    #     help_text="机头朝向，0-360度"
    # )
    # stay_time = models.FloatField(
    #     verbose_name="停留时间",
    #     default=0,
    #     help_text="单位：秒"
    # )

    # 航点序号和状态
    sequence = models.PositiveIntegerField(verbose_name="航点序号")
    is_reached = models.BooleanField(default=False, verbose_name="是否已到达")
    reached_at = models.BigIntegerField(null=True, blank=True, verbose_name="到达时间")

    # 航点动作配置
    gimbal_yaw = models.FloatField(
        null=True,
        blank=True,
        verbose_name='云台偏航轴角度'
    )
    gimbal_pitch = models.FloatField(
        null=True,
        blank=True,
        verbose_name="云台俯仰轴角度",
        help_text="-90到0度"
    )
    zoom_factor = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="云台变焦倍数"
    )
    # take_photo = models.BooleanField(
    #     default=False,
    #     verbose_name="拍照"
    # )
    
    image = models.ImageField(
        upload_to='missions/thumbs/%Y/%m/%d/',
        verbose_name="航点图片",
        null=True, 
        blank=True
    )
    # record_video = models.BooleanField(
    #     default=False,
    #     verbose_name="录像"
    # )

    class Meta:
        verbose_name = '航点'
        verbose_name_plural = '航点管理'
        ordering = ['mission_assignment', 'sequence']
        indexes = [
            models.Index(fields=['mission_assignment', 'sequence']),
            models.Index(fields=['longitude', 'latitude'])
            # models.Index(fields=['is_reached'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['mission_assignment', 'sequence'],
                name='unique_waypoint_sequence'
            )
        ]

    def __str__(self):
        return f"{self.drone.name} - 航点{self.sequence} ({self.longitude}, {self.latitude})"

    def save(self, *args, **kwargs):
        if self.is_reached and not self.reached_at:
            self.reached_at = timezone.now()
        super().save(*args, **kwargs)


# 如果使用自定义用户模型（在settings.py中需要设置AUTH_USER_MODEL）
# class CustomUser(AbstractUser):
#     # 添加自定义用户字段
#     company = models.CharField(max_length=100, blank=True)
#     phone = models.CharField(max_length=20, blank=True)
# 
#     class Meta:
#         verbose_name = '用户'
#         verbose_name_plural = '用户管理'
