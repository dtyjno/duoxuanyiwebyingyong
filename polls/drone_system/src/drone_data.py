from dataclasses import dataclass
from typing import Optional

@dataclass
class DroneTelemetry:
    """无人机与机场状态遥测数据模型"""
    
    dockSn: str                    # 机场SN (string)
    droneSn: str                   # 无人机SN (string)
    longitude: float               # 经度 (度, double)
    latitude: float                # 纬度 (度, double)
    height: float                  # 高度 (米, double)
    elevation: float               # 相对起飞点高度 (米, double)
    horizontalSpeed: float         # 水平速度 (米/秒, double)
    verticalSpeed: float           # 垂直速度 (米/秒, double)
    attitudePitch: float           # 俯仰轴角度 (度, double)
    attitudeRoll: float            # 横滚轴角度 (度, double)
    attitudeHead: float            # 机头朝向角度 (度, double)
    capacityPercent: float         # 电池电量 (百分比, double)
    dockStatus: int                # 设备状态 (int: 0=空闲中, 1=现场调试...)
    timeStamp: int                  # 时间戳 (long)
    gimbalYaw: float               # 云台偏航轴角度 (度, double)
    zoomFactor: int                # 云台变焦倍数 (int)
    gimbalPitch: float             # 云台俯仰轴角度 (度, double)
    
    def __post_init__(self):
        assert -180 <= self.longitude <= 180, "经度范围错误"
        assert -90 <= self.latitude <= 90, "纬度范围错误"
        assert 0 <= self.capacityPercent <= 100, "电量百分比无效"

from enum import Enum
class DockStatus(Enum):
    IDLE = 0
    FIELD_DEBUG = 1
    # ...其他状态码
