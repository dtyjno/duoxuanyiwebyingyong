import asyncio
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Drone, MissionAssignment, WayPoint
from channels.db import database_sync_to_async
from django.db.models import Prefetch

class DroneTrackerConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # 验证用户身份
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            print("未认证用户连接尝试")
            await self.close(code=4001)
            return

        # 调试输出当前用户
        print(f"连接用户: {self.user.username}")

        # 接受WebSocket连接
        await self.accept()

        # 启动定时器任务
        self.send_task = asyncio.create_task(self.send_periodic_updates())

    async def disconnect(self, close_code):
        # 取消定时器任务
        if hasattr(self, 'send_task'):
            self.send_task.cancel()

        # 自定义关闭代码处理
        if close_code == 4001:
            print("未认证用户连接尝试")
        elif close_code == 4002:
            print("数据获取失败")

    async def send_periodic_updates(self):
        while True:
            try:
                # 获取并发送数据
                geojson_data = await self.get_geojson_data()
                await self.send_json(geojson_data)
            except Exception as e:
                print(f"数据获取失败: {e}")
                await self.send_json({"error": str(e)})

            # 等待一段时间后再次发送数据
            await asyncio.sleep(10)  # 每10秒发送一次数据
# def get_geojson_data(self):
#     try:
#         # 获取当前用户的所有无人机，并预取相关数据
#         drones = Drone.objects.filter(user=self.user).prefetch_related(
#             Prefetch('assignments',  # 使用Drone模型中定义的related_name
#                     queryset=MissionAssignment.objects.prefetch_related(
#                         'targets',  # 预取多对多目标
#                         Prefetch('waypoints', queryset=WayPoint.objects.order_by('sequence'))
#                     ))
#         )

#         features = []
        
#         for drone in drones:
#             # 无人机基础信息
#             drone_properties = {
#                 "id": drone.id,
#                 "type": "drone",
#                 "sn": drone.drone_sn,
#                 "status": {
#                     "code": drone.dock_status,
#                     "text": drone.get_dock_status_display()
#                 },
#                 "battery": drone.capacity_percent,
#                 "altitude": drone.height,
#                 "coordinates": [drone.longitude, drone.latitude],
#                 "details_url": f"/drones/{drone.id}/"
#             }

#             # 无人机实时位置特征
#             features.append({
#                 "type": "Feature",
#                 "geometry": {
#                     "type": "Point",
#                     "coordinates": [float(drone.longitude), float(drone.latitude)]
#                 },
#                 "properties": drone_properties
#             })

#             # 处理每个任务分配
#             for assignment in drone.assignments.all():
#                 # 任务基本信息
#                 mission_properties = {
#                     "mission_id": assignment.id,
#                     "name": assignment.name,
#                     "status": assignment.get_status_display(),
#                     "start_time": assignment.start_time.isoformat()
#                 }

#                 # 关联任务目标
#                 for target in assignment.targets.all():  # 使用多对多字段的all()
#                     if target.latitude and target.longitude:
#                         target_feature = {
#                             "type": "Feature",
#                             "geometry": {
#                                 "type": "Point",
#                                 "coordinates": [float(target.longitude), float(target.latitude)]
#                             },
#                             "properties": {
#                                 **mission_properties,
#                                 "target_id": target.id,
#                                 "type": "mission_target"
#                             }
#                         }
#                         features.append(target_feature)

#                 # 关联航路点
#                 for waypoint in assignment.waypoints.all():
#                     waypoint_feature = {
#                         "type": "Feature",
#                         "geometry": {
#                             "type": "Point",
#                             "coordinates": [float(waypoint.longitude), float(waypoint.latitude)]
#                         },
#                         "properties": {
#                             **mission_properties,
#                             "waypoint_id": waypoint.id,
#                             "sequence": waypoint.sequence,
#                             "type": "waypoint"
#                         }
#                     }
#                     features.append(waypoint_feature)

#         return {
#             "type": "FeatureCollection",
#             "features": features
#         }

#     except Exception as e:
#         logger.error(f"GeoJSON生成失败: {str(e)}")
#         return {
#             "type": "FeatureCollection",
#             "features": [],
#             "error": "数据加载失败"
#         }

    @database_sync_to_async
    def get_geojson_data(self):
        try:
           # Update the query to use correct relationship names
            # 获取当前用户的所有无人机，并预取相关数据
            drones = Drone.objects.filter(user=self.user).prefetch_related(
                'assignments',
                'assignments__targets',  # Use plural form since it's M2M
                'assignments__waypoints'
            )

            features = []
            
            # 遍历每个无人机及其任务
            for drone in drones:
                # 构建无人机基础信息
                drone_properties = {
                    "id": drone.id,
                    "type": "drone",
                    "sn": drone.drone_sn,
                    "status": {
                        "code": drone.dock_status,
                        "text": drone.get_dock_status_display()
                    },
                    "battery": drone.capacity_percent,
                    "altitude": drone.height,
                    "last_update": drone.time_stamp,
                    # "details_url": reverse('drone-detail', args=[drone.id])
                    
                    # "details_url": f"/drones/{drone.id}/"
                }

                # 添加无人机实时位置为独立特征
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(drone.longitude), float(drone.latitude)]
                    },
                    "properties": drone_properties
                })

                # 处理任务相关数据
                # Get all targets for this assignment
                for assignment in drone.assignments.all():
                    for target in assignment.targets.all():  # Change here - iterate through targets
                        mission_properties = {
                            "id": assignment.id,
                            "type": "mission",
                            "name": assignment.name or f"任务-{assignment.id}",
                            "status": {
                                "code": assignment.status,
                                "text": assignment.get_status_display()
                            },
                            "start_time": assignment.start_time.isoformat(),
                            "end_time": assignment.end_time.isoformat() if assignment.end_time else None,
                            "drones": [{
                                "id": drone.id,
                                "sn": drone.drone_sn,
                                "status": drone_properties["status"]
                            }]
                        }

                        # Add target feature if coordinates exist
                        if target.longitude and target.latitude:
                            features.append({
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [float(target.longitude), float(target.latitude)]
                                },
                                "properties": {
                                    **mission_properties,
                                    "target_id": target.id,
                                    "target_name": target.name
                                }
                            })

                        # Add waypoints if needed
                        # for waypoint in assignment.waypoints.all():
                        #     wp_properties = {
                        #         **mission_properties,
                        #         "type": "waypoint",
                        #         "sequence": waypoint.sequence,
                        #         "altitude": waypoint.height,
                        #         "is_reached": waypoint.is_reached,
                        #         "reached_at": waypoint.reached_at.isoformat() if waypoint.reached_at else None
                        #     }
                            
                        #     features.append({
                        #         "type": "Feature",
                        #         "geometry": {
                        #             "type": "Point",
                        #             "coordinates": [float(waypoint.longitude), float(waypoint.latitude)]
                        #         },
                        #         "properties": wp_properties
                        #     })
            return {
                "type": "FeatureCollection",
                "features": features
            }

        except Exception as e:
            print(f"数据生成失败: {e}")
            return {
                "type": "FeatureCollection",
                "features": [],
                "error": "数据生成失败"
            }


    async def receive_json(self, content, **kwargs):
        if content.get('action') == 'request_update':
            try:
                geojson_data = await self.get_geojson_data()
                await self.send_json(geojson_data)
            except Exception as e:
                await self.send_json({"error": str(e)})