# signals.py 实时更新触发机制
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Drone

@receiver(post_save, sender=Drone)
def drone_change_handler(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "drones_updates",
        {
            "type": "drone.update",
            "id": instance.id
        }
    )

# signals.py 添加阈值检测
# POSITION_CHANGE_THRESHOLD = 0.0001 # 约10米

@receiver(post_delete, sender=Drone)
def drone_delete_handler(sender, instance, **kwargs):
    # if (abs(instance.longitude - instance.prev_longitude) > POSITION_CHANGE_THRESHOLD or 
    #     abs(instance.latitude - instance.prev_latitude) > POSITION_CHANGE_THRESHOLD):
        # 触发位置更新通知
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "drones_updates",
        {
            "type": "drone.delete",
            "id": instance.id
        }
    )
