import json
import time
import threading
import requests
import websockets
import asyncio
from urllib.parse import urljoin
import base64
from typing import Dict, Optional
import logging
import yaml

from asgiref.sync import sync_to_async

import os
import django
import sys

import cv2
import numpy as np
from datetime import datetime
import os
import traceback
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor

# 将项目根目录添加到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)
# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
# 现在可以导入模型
from polls.models import Drone, MissionAssignment ,WayPoint  # 根据实际 models.py 路径调整

logger = logging.getLogger(__name__)

def get_base64_credentials(app_id: str, app_secret: str):
    """生成 Base64 编码的认证信息"""
    credentials = f"{app_id}:{app_secret}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()
    return base64_credentials

class DroneHardwareManager:

    def __init__(self, drone_id, json_data):
        self.base_url = json_data["base_url"]
        self.app_id = json_data["app_id"]
        self.app_secret = json_data["app_secret"]
        self.device_sn = json_data["device_sn"]
        self.mission_id = json_data["mission_id"]

        # 与数据库通信
        self.drone_id = drone_id
        # json_data["drone_id"] # 唯一标识无人机
        self.drone = Drone.objects.get(id=self.drone_id)
        self.drone_data = None

        # Fix mission assignment initialization
        self.mission_assignment = MissionAssignment.objects.get(id=self.mission_id)
        self.mission_assignment_name = self.mission_assignment.name
        # self.mission_assignment_name = "test"
        # Change this line - don't assign the return value of mark_as_started()
        self.mission_assignment.mark_as_started()  # This method already saves the model
        self.update_counts = 0

        self.access_token: Optional[str] = None
        self.ws_connection = None
        self.current_status: Dict = {}
        self.lock = threading.Lock()
        self._loop = None
        self._stop_event = threading.Event()
        self.live_stream_url = None
        self.longitude=None
        self.latitude=None
        self.height=None

        self.cap = None
        self.stream_thread = None
        self.frame = None
        self.frame_lock = threading.Lock()
        
        # Create images directory if it doesn't exist
        self.images_dir = os.path.join(project_root, 'media', str(self.mission_assignment_name), 'drone_images', str(self.drone_id))
        os.makedirs(self.images_dir, exist_ok=True)

        #  Add video recording attributes
        self.video_writer = None
        self.recording = False
        self.video_path = None
        
        # Create videos directory
        self.videos_dir = os.path.join(project_root, 'media', str(self.mission_assignment_name), 'videos', str(self.drone_id))
        os.makedirs(self.videos_dir, exist_ok=True)

        # 初始化认证
        self.authenticate()

        # 获取直播地址
        self.get_live_stream_url()
        self.start_stream_capture()
        self.start_real_time_monitor()

        # 启动实时监控线程
        monitor_thread = threading.Thread(target=self.start_real_time_monitor, daemon=True)
        monitor_thread.start()

    def authenticate(self):
        """获取访问令牌"""
        # 生成 Base64 编码的认证信息
        base64_credentials = get_base64_credentials(self.app_id, self.app_secret)
        headers = {
            "Authorization": f"Basic {base64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_secret"
        }
        auth_url = urljoin(self.base_url, "/prod-api/admin-api/system/oauth2/token")
        logger.debug(f"Authenticating with {auth_url}")
        try:
            response = requests.post(auth_url, headers=headers, data=data) # , timeout=5
            logger.debug(f"Access Token Response Status Code: {response.status_code}")
            # logger.debug(f"Access Token Response Text: {response.text}")
            if response.status_code == 200:
                response_data = response.json().get("data", {})
                self.access_token = response_data.get("access_token")
                self.refresh_token = response_data.get("refresh_token")
                self.tocken_expires = response_data.get("expires_in")
                logger.info(f"认证成功，获取到访问令牌: {self.access_token}, 刷新令牌: {self.refresh_token}, 过期时间: {self.tocken_expires}")
            else:
                raise Exception(f"认证失败: {data.get('msg')}")
        except Exception as e:
            logger.error(f"authenticate(): 认证异常: {str(e)}")
            # raise

    def get_live_stream_url(self) -> Optional[str]:
        """获取RTMP直播流地址"""
        if(self.live_stream_url != None): # 获取过RTMP直播流地址
            return self.live_stream_url
        if not self.access_token: # 未调用authenticate()生成token或生成未成功
            # raise ValueError("未获取有效访问令牌")
            logger.error("get_live_stream_url(): 未获取有效访问令牌")
            return None
        live_url = urljoin(self.base_url, "/prod-api/open-api/base/live/getRtmp")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "sn": self.device_sn
        }
        try:
            response = requests.get(live_url, headers=headers, params=params)
            logger.debug(f"直播地址响应状态码: {response.status_code}")
            logger.debug(f"直播地址响应内容: {response.text}")
            response.raise_for_status()
            data = response.json()
            if data["code"] == 0:
                logger.info(f"获取直播地址成功: {data['data']['url']}")
                self.live_stream_url = data["data"]["url"]
                return self.live_stream_url
        except requests.exceptions.RequestException as e:
            print(f"获取直播地址失败: {str(e)}")

    async def _websocket_handler(self):
        """WebSocket消息处理协程（修复版）"""
        ws_url = f"wss://{self.base_url.split('//')[1]}/socket/connect/5/{self.access_token}"
        headers = {
            "Origin": self.base_url,
            "Sec-WebSocket-Protocol": "chat",  # 添加必要协议头
            "User-Agent": "DroneControl/1.0"
        }

        try:
            # 手动设置请求头
            async with websockets.connect(
                ws_url,
                ping_interval=25,  # 比服务器超时短5秒
                ping_timeout=10,
                close_timeout=10,
                # extra_headers=headers
            ) as ws:
                self.ws_connection = ws
                logger.info("WebSocket连接成功建立")

                # 主消息循环
                while not self._stop_event.is_set():
                    try:
                        message = await ws.recv()
                        parsed_data = json.loads(message)
                        
                        
                        self.drone_data=parsed_data["data"]
                        print(self.drone_data)
                        # 更新数据库
                        await self.update_status()
                        # self.longitude=data["longitude"]
                        # self.latitude=data["latitude"]
                        # self.height=data["height"]
                        # logger.info("WebSocket连接成功建立")

                    except websockets.ConnectionClosed as e:
                        logger.error(f"连接关闭: code={e.code}, reason={e.reason}")
                        await self._reconnect_websocket()
                        break

        except websockets.InvalidStatusCode as e:
            logger.error(f"连接失败: HTTP状态码 {e.status_code}")
            logger.error(f"响应头: {e.headers}")
            if e.body:
                logger.error(f"响应体: {e.body.decode()}")
        except Exception as e:
            logger.error(f"_websocket_handler()消息处理协程：连接异常: {str(e)}")
        finally:
            await self._close_websocket()

    async def _reconnect_websocket(self):
        """智能重连逻辑"""
        retry_delays = [1, 3, 5, 10, 30]  # 指数退避间隔
        for delay in retry_delays:
            print(f"{delay}秒后尝试重连...")
            await asyncio.sleep(delay)
            try:
                await self._websocket_handler()
                return
            except Exception as e:
                print(f"重连失败: {str(e)}")
        print("达到最大重试次数，终止连接")

    def start_real_time_monitor(self):
        """启动实时监控"""
        if not self.access_token:
            # raise ValueError("未获取有效访问令牌")
            logger.error("start_real_time_monitor(): 未获取有效访问令牌")
            return
        
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        # self._loop.run_until_complete(self._websocket_handler())
        try:
            self._websocket_task = self._loop.create_task(self._websocket_handler())
            self._loop.run_forever()  # 持续运行事件循环
        except KeyboardInterrupt:
            pass
        finally:
            if(self._loop.is_running()):
                self._loop.stop()
            self._loop.close()
            logger.info("事件循环已停止")

    
    def start_stream_capture(self):
        """Start capturing frames from RTMP stream"""
        if not self.live_stream_url:
            logger.error("No RTMP URL available")
            return
            
        def capture_frames():
            self.cap = cv2.VideoCapture(self.live_stream_url)
            while not self._stop_event.is_set():
                ret, frame = self.cap.read()
                if ret:
                    with self.frame_lock:
                        self.frame = frame
                else:
                    logger.error("Failed to read frame from stream")
                    break
            
            self.cap.release()
            
        self.stream_thread = threading.Thread(target=capture_frames, daemon=True)
        self.stream_thread.start()

    def save_current_frame(self):
        """Save current frame as image"""
        if self.frame is None:
            return None
            
        with self.frame_lock:
            frame = self.frame.copy()
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'drone_{self.drone_id}_{timestamp}.jpg'
        filepath = os.path.join(self.images_dir, filename)
        
        # Save image
        cv2.imwrite(filepath, frame)
        return f'drone_images/{filename}'


    def shutdown(self):
        """安全关闭（线程安全）"""
        self._stop_event.set()
        
        # Stop recording if active
        if self.recording:
            self.stop_recording()
                
        # Release video capture
        if self.cap:
            self.cap.release()
            
        # Wait for stream thread to finish
        if self.stream_thread and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=5)
        
        if self.executor:
            self.executor.shutdown(wait=False)

        if self._loop:
            
            # 关闭WebSocket连接
            if self._websocket_task and not self._websocket_task.done():
                try:
                    self._websocket_task.cancel()
                    self._loop.run_until_complete(self._websocket_task)
                except Exception as e:
                    logger.error(f"关闭WebSocket任务异常: {str(e)}")
            
            if self._loop.is_running():
                self._loop.call_soon_threadsafe(self._loop.stop)

            start_time = time.time()
            while self._loop.is_running() and time.time() - start_time < 5:
                time.sleep(0.1)
            
            logger.info("已关闭连接")

    # def shutdown(self):
    #     """安全关闭连接（线程安全）"""
    #     self._stop_event.set()
        
    #     # 如果事件循环存在且未关闭
    #     if self._loop and self._loop.is_running():
    #         # 向事件循环提交关闭任务
    #         self._loop.call_soon_threadsafe(
    #             lambda: self._loop.create_task(self._close_websocket())
    #         )
    #         # 等待循环关闭
    #         self._loop.stop()
    #         self._loop.close()
    #     logger.info("已关闭连接")

    async def _close_websocket(self):
        """异步关闭WebSocket"""
        if self.ws_connection:
            await self.ws_connection.close()
            self.ws_connection = None

    @staticmethod
    def get_1():
        logger.info("get_1")
        return 1
    
    def get_current_status(self) -> Dict:
        """获取当前状态"""
        return self.current_status
    
    def get_lat(self):
        return self.latitude
    
    def get_lon(self):
        return self.longitude
    
    def get_height(self):
        return self.height
    
    # async def update_status(self):
    #     """更新硬件状态到数据库"""
    #     self.update_counts += 1
    #     try:
    #         # Convert timestamp to datetime
    #         timestamp_ms = self.drone_data['timeStamp']
    #         timestamp = datetime.fromtimestamp(timestamp_ms / 1000.0)

    #         # Save current frame if available
    #         image_path = None
    #         if self.frame is not None:
    #             image_path = await self._save_frame_async()

    #         # Create waypoint data
    #         waypoint_data = {
    #             'drone': self.drone,
    #             'mission_assignment': self.mission_assignment,
    #             'longitude': self.drone_data['longitude'],
    #             'latitude': self.drone_data['latitude'],
    #             'height': self.drone_data['height'],
    #             'elevation': self.drone_data['elevation'],
    #             'horizontal_speed': self.drone_data['horizontalSpeed'],
    #             'vertical_speed': self.drone_data['verticalSpeed'],
    #             'attitude_pitch': self.drone_data['attitudePitch'],
    #             'attitude_roll': self.drone_data['attitudeRoll'],
    #             'attitude_head': self.drone_data['attitudeHead'],
    #             'sequence': self.update_counts,
    #             'is_reached': False,
    #             'gimbal_yaw': self.drone_data['gimbalYaw'],
    #             'gimbal_pitch': self.drone_data['gimbalPitch'],
    #             'zoom_factor': self.drone_data['zoomFactor'],
    #             'image': image_path,
    #             'reached_at': timestamp
    #         }

    #         # Update drone data
    #         drone_data = {
    #             'longitude': self.drone_data['longitude'],
    #             'latitude': self.drone_data['latitude'],
    #             'height': self.drone_data['height'],
    #             'elevation': self.drone_data['elevation'],
    #             'horizontal_speed': self.drone_data['horizontalSpeed'],
    #             'vertical_speed': self.drone_data['verticalSpeed'],
    #             'attitude_pitch': self.drone_data['attitudePitch'],
    #             'attitude_roll': self.drone_data['attitudeRoll'],
    #             'attitude_head': self.drone_data['attitudeHead'],
    #             'capacity_percent': self.drone_data['capacityPercent'],
    #             'gimbal_yaw': self.drone_data['gimbalYaw'],
    #             'zoom_factor': self.drone_data['zoomFactor'],
    #             'gimbal_pitch': self.drone_data['gimbalPitch'],
    #             'time_stamp': timestamp
    #         }

    #         # Execute database updates in thread pool
    #         await self._update_database(waypoint_data, drone_data)
    #         logger.info(f"状态更新成功: {self.drone.id}")

    #     except Exception as e:
    #         logger.error(f"更新失败: {str(e)} error: {str(traceback.format_exc())}")
    #         raise

    # async def _save_frame_async(self):
    #     """异步保存当前帧"""
    #     if self.frame is None:
    #         return None
        
    #     with self.frame_lock:
    #         frame = self.frame.copy()
            
    #     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    #     filename = f'drone_{self.drone_id}_{timestamp}.jpg'
    #     filepath = os.path.join(self.images_dir, filename)
        
    #     # Execute CV2 operations in thread pool
    #     loop = asyncio.get_event_loop()
    #     await loop.run_in_executor(self.executor, cv2.imwrite, filepath, frame)
    #     return f'drone_images/{filename}'

    # @sync_to_async
    # def _update_database_sync(self, waypoint_data, drone_data):
    #     """同步执行数据库更新"""
    #     with transaction.atomic():
    #         # Create and save waypoint
    #         print("waypoint_data",waypoint_data)
    #         waypoint = WayPoint(**waypoint_data)
    #         waypoint.full_clean()
    #         waypoint.save()

    #         # Update drone
    #         for key, value in drone_data.items():
    #             setattr(self.drone, key, value)
    #         self.drone.full_clean()
    #         self.drone.save()

    # async def _update_database(self, waypoint_data, drone_data):
    #     """异步包装器用于数据库更新"""
    #     loop = asyncio.get_event_loop()
    #     await loop.run_in_executor(
    #         self.executor,
    #         lambda: self._update_database_sync(waypoint_data, drone_data)
    #     )
    async def update_status(self):
        """更新硬件状态到数据库"""
        self.update_counts += 1
        try:
            # Save current frame if available
            image_path = None
            if self.frame is not None:
                image_path = self.save_current_frame()
            
            # Convert timestamp to datetime object
            timestamp = self.drone_data['timeStamp']
            
            waypoint = WayPoint()
            waypoint.drone = self.drone

            waypoint.mission_assignment = self.mission_assignment
            
            waypoint.longitude = self.drone_data['longitude']
            waypoint.latitude = self.drone_data['latitude']
            waypoint.height = self.drone_data['height']
            waypoint.elevation = self.drone_data['elevation']
            waypoint.horizontal_speed = self.drone_data['horizontalSpeed']
            waypoint.vertical_speed = self.drone_data['verticalSpeed']
            waypoint.attitude_pitch = self.drone_data['attitudePitch']
            waypoint.attitude_roll = self.drone_data['attitudeRoll']
            waypoint.attitude_head = self.drone_data['attitudeHead']
            waypoint.sequence = self.update_counts
            waypoint.is_reached = False
            waypoint.gimbal_yaw = self.drone_data['gimbalYaw']
            waypoint.gimbal_pitch = self.drone_data['gimbalPitch']
            waypoint.zoom_factor = self.drone_data['zoomFactor']
            waypoint.image = image_path
             # Convert timestamp to proper format if it's not already a string
            
            waypoint.reached_at = timestamp
            await sync_to_async(waypoint.full_clean, thread_sensitive=False)()
            await sync_to_async(waypoint.save, thread_sensitive=False)()

            add_assignment = sync_to_async(
                lambda: self.drone.assignments.add(self.mission_assignment),
                thread_sensitive=False
            )
            await add_assignment()

            # 设备信息
            # self.drone.dock_sn = models.CharField(max_length=100, verbose_name='机场SN')
            # self.drone.drone_sn = models.CharField(max_length=100, verbose_name='无人机SN')
            # self.drone.id = models.CharField(max_length=100, verbose_name='无人机ID')
            
            # 定位信息
            self.drone.longitude = self.drone_data['longitude']
            self.drone.latitude = self.drone_data['latitude']
            self.drone.height = self.drone_data['height']
            self.drone.elevation = self.drone_data['elevation']
            
            # 运动状态
            self.drone.horizontal_speed = self.drone_data['horizontalSpeed']
            self.drone.vertical_speed = self.drone_data['verticalSpeed']
            
            # 姿态信息
            self.drone.attitude_pitch = self.drone_data['attitudePitch']
            self.drone.attitude_roll = self.drone_data['attitudeRoll']
            self.drone.attitude_head = self.drone_data['attitudeHead']
            
            # 设备状态
            self.drone.capacity_percent = self.drone_data['capacityPercent']
            if 'dockStatus' in self.drone_data:
                self.drone.dock_status = self.drone_data['dockStatus']
            
            # 云台信息
            self.drone.gimbal_yaw = self.drone_data['gimbalYaw']
            self.drone.zoom_factor = self.drone_data['zoomFactor']
            self.drone.gimbal_pitch = self.drone_data['gimbalPitch']

            if 'userLatitude' in self.drone_data:
                self.drone.gimbal_pitch = self.drone_data['userLatitude']
            if 'userLongitude' in self.drone_data:
                self.drone.gimbal_pitch = self.drone_data['userLongitude']

            
            # 时间信息
            self.drone.time_stamp = timestamp
            
            # 触发完整验证
            await sync_to_async(self.drone.full_clean, thread_sensitive=False)()
            await sync_to_async(self.drone.save, thread_sensitive=False)()
            logger.info(f"状态更新成功: {self.drone.id}")
        except Exception as e:
            logger.error(f"更新失败: {str(e)} error: {str(traceback.format_exc())}")
            raise

    def get_historical_data(self, hours=24):
        """获取历史数据"""
        from django.utils import timezone
        from django.db.models import Q
        
        return Drone.objects.filter(
            Q(id=self.drone.id) &
            Q(created_at__gte=timezone.now() - timezone.timedelta(hours=hours))
        ).order_by('-time_stamp')

# if __name__ == "__main__":
#     # 测试用例
#     manager = DroneHardwareManager("UAV-001")
    
#     test_data = {
#         'longitude': 116.397428,
#         'latitude': 39.90923,
#         'status_code': 4,
#         'battery': 78.5
#     }
    
#     manager.update_status(test_data)
#     history = manager.get_historical_data()
#     print(f"最近24小时记录数: {history.count()}")
        
    

# 使用示例
if __name__ == "__main__":
    # 配置参数
    # 配置基础信息
    # BASE_URL = "https://all.xinkongan.com"  # 替换为实际的API基础地址
    # APP_ID = "6bac0bdd-62bc-4442-ba90-a85df625e067"  # 替换为实际的appId
    # APP_SECRET = "c6930005-7514-40f7-9f0d-f9268640adba"  # 替换为实际的appSecret
    # 初始化日志系统
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler('drone_system.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    with open('/home/linhao/code/tutorial_copy/drone_system/config/default.yaml', 'r') as f:
        conf = yaml.safe_load(f).get('drone_hardware', 'default_value')

    # 初始化硬件管理器
    drone_mgr = DroneHardwareManager(
        conf
    )
    
    try:
        # 获取直播地址
        rtmp_url = drone_mgr.get_live_stream_url()
        print(f"RTMP直播地址: {rtmp_url}")
        
        # 启动实时监控线程
        monitor_thread = threading.Thread(target=drone_mgr.start_real_time_monitor, daemon=True)
        monitor_thread.start()
        
        # 主循环获取状态
        while True:
            status = drone_mgr.get_current_status()
            print(f"longitude:{drone_mgr.longitude},latitude:{drone_mgr.latitude},height:{drone_mgr.height}")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("正在关闭...")
    finally:
        drone_mgr.shutdown()
        print("已关闭连接")