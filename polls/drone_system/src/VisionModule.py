import time
import logging
from typing import Dict
import threading

import sys
import os
import django
from src.DroneHardwareManager import DroneHardwareManager

# 将项目根目录添加到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)
# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
# 现在可以导入模型
from polls.models import Drone  # 根据实际 models.py 路径调整


# from src.utils.logger import EnhancedDelayLogger
# logger_v = EnhancedDelayLogger()

logger = logging.getLogger(__name__)

class VisionModule:
    def __init__(
        self, 
        config: Dict,
        drone_id: int,
        hardware: DroneHardwareManager
    ):
        self.config = config
        # 与数据库通信
        self.drone_id = drone_id
        self.hardware = hardware
        self.drone = Drone.objects.get(id=self.drone_id)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread_started = False  # 标志线程是否已经启动

        logger.info("Vision node initialized")

    # def get_single_drone(self):
    #     """获取单个无人机完整信息"""
    #     try:
    #         return Drone.objects.select_related('user').get(
    #             drone_id=self.drone_id
    #         )
    #     except Drone.DoesNotExist:
    #         return None

    def run(self):
        """主处理循环"""
        logger.info("Vision pipeline started")
        
        try:
            while not self.stop_event.is_set():
                # self.drone_data = self.get_single_drone()
                logger.info(f"Vision pipeline running: lon={self.hardware.get_lon()}, lat={self.hardware.get_lat()}, height={self.hardware.get_height()}")
                self.stop_event.wait(1)
        except KeyboardInterrupt:
            logger.info("Vision pipeline stopped by user")
        except Exception as e:
            logger.error(f"Vision pipeline failed: {str(e)}", exc_info=True)

    def start(self):
        """启动线程"""
        self.thread.start()
        self.thread_started = True  # 标志线程已经启动
        logger.info("Vision Module thread started")

    def shutdown(self):
        """关闭线程"""
        if self.thread_started:  # 检查线程是否已经启动
            self.stop_event.set()
            self.thread.join()
            logger.info("Vision Module shutdown")