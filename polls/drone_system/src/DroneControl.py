import time
import logging
from typing import Dict
from src.DroneHardwareManager import DroneHardwareManager
from src.VisionModule import VisionModule
import threading
import asyncio

logger = logging.getLogger(__name__)

class DroneControl:
    def __init__(self, config: Dict):
        
        self.vision_id = []
        self.config = config
        self.hardware = DroneHardwareManager(self.config.get('drone_id'), self.config.get('drone_hardware')) # 创建硬件管理器
        self.vision_module = VisionModule(self.config.get('vision_module'), self.config.get('drone_id'), self.hardware) # 创建视觉处理模块

        logging.info("Control node initialized")

    def shutdown(self):
        """关闭线程"""
        logger.info("Control subsystem shutdown")
        # asyncio.run(self.hardware.shutdown())
        self.hardware.shutdown()
        self.vision_module.shutdown()
        logger.info("Control node shutdown")

    def run(self, stop_event: threading.Event):
        """主控制循环"""
        logger.info("Starting drone control loop")
        
        try:
            self.vision_module.start()  # 启动视觉处理模块线程
            while not stop_event.is_set():
                logger.info(f"drone_control running")
                # logger.info(f"lat: {self.hardware.get_lat()}, lon: {self.hardware.get_lon()}, height: {self.hardware.get_height()}")
                # time.sleep(1)
                stop_event.wait(1)
            self.shutdown()
        except KeyboardInterrupt:
            logger.info("Control loop stopped by user")
        except Exception as e:
            logger.error(f"Control loop failed: {str(e)}", exc_info=True)
        finally:
            self.shutdown()