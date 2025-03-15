import sys
import os
import time
import signal
import logging
import yaml
# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.DroneControl import DroneControl
from src.ThreadManager import ThreadManager

# 初始化日志系统
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d-%(name)s-%(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler('drone_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_config(config_path):
    """安全加载配置文件"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            logger.info(f"Loaded config from {config_path}")
            return config
    except Exception as e:
        logger.critical(f"Config load failed: {str(e)}")
        sys.exit(1)

class DroneSystem:
    def __init__(self):        
        logger.info("Drone system initialized")
        self.drone_id_list = [] # 无人机ID列表
        self.threads_manager = ThreadManager() # 创建线程管理器
        # self.register_signals()

    # def register_signals(self):
    #     """注册信号处理函数"""
    #     signal.signal(signal.SIGINT, self.handle_signal)
    #     signal.signal(signal.SIGTERM, self.handle_signal)

    # def handle_signal(self, signum, frame):
    #     """信号处理逻辑"""
    #     logging.warning(f"Received signal {signum}, initiating shutdown")
    #     self.shutdown()
    #     # self.threads_manager.register_signals() # 捕获退出信号

    def run_drone(self, config, drone_id:int):
        """主运行循环"""
        logger.info(f"Starting {"Drone" + str(drone_id)}")
        if drone_id in self.drone_id_list:
            raise Exception(f"{"Drone" + str(drone_id)}已存在")
        self.drone_id_list.append(drone_id)
        try:
            # 启动线程
            self.threads_manager.start_thread(
                target=DroneControl(config),
                name="Drone" + str(drone_id),
            )
        except Exception as e:
            self.threads_manager.safe_shutdown()
            raise e 
            # logger.critical(f"System failure: {str(e)}", exc_info=True)

    def stop_drone(self, drone_id:int):
        """停止无人机"""
        try:
            self.drone_id_list.remove(drone_id)
            self.threads_manager.stop_thread("Drone" + str(drone_id))
        except Exception as e:
            raise e
    def run(self):
        """主运行循环"""
        # 主监控循环
        while True:
            time.sleep(1)
            if not any(t.is_alive() for t in self.threads_manager.threads):
                logger.error("Critical thread died, shutting down")
                break
    def shutdown(self):
        """关闭线程"""
        logger.info("Drone system shutdown")
        self.threads_manager.safe_shutdown()
        logger.info("Drone system shutdown")
        exit(0)

if __name__ == "__main__":
    ds = DroneSystem()
    config = load_config("drone_system/config/default.yaml")
    ds.run_drone(config, 1)
    time.sleep(3)
    # logger.info("Stop drone")
    # ds.stop_drone(1)
    # time.sleep(5)
    while True:
        time.sleep(1)
        # if not any(t.is_alive() for t in ds.threads_manager.threads):
        #     logger.error("Critical thread died, shutting down")
        #     break
    
    
