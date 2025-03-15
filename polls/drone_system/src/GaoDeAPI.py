import json
import time
import threading
import requests
import asyncio
from urllib.parse import urljoin
import base64
from typing import Dict, Optional
import logging
import yaml
from utils import load_config
from dataclasses import dataclass
from retrying import retry

from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from ImageHubAPI import ImageHubUploader

@dataclass
class GeoPos:
    longitude: float               # 经度 (度, double)
    latitude: float                # 纬度 (度, double)
 

class GaoDeAPI:

    def __init__(self):
        config = load_config("config/gaodeapi.yaml")
        self.key = config["key"]
            
    def convert_coordinates(self, locations: list[GeoPos], coordsys='gps', output='json'):
        """
        调用高德地图坐标转换API
        
        参数:
            locations : str 
                需要转换的坐标字符串，格式 "经度,纬度" 或 "经度1,纬度1|经度2,纬度2"
            key : str
                高德地图API的授权key
            coordsys : str, 可选
                原坐标系类型 (gps/mapbar/baidu/autonavi)，默认gps
            output : str, 可选
                返回格式 (json/xml)，默认json
        
        返回:
            dict: 包含转换结果和状态的字典
        """
        # API端点
        url = "https://restapi.amap.com/v3/assistant/coordinate/convert"
        
        # 构造请求参数
        locations_str = "|".join([f"{geopos.longitude},{geopos.latitude}" for geopos in locations])

        # 构造请求参数
        params = {
            'key': self.key,
            'locations': locations_str,
            'coordsys': coordsys,
            'output': output
        }
        
        try:
            # 发送GET请求
            response = self._request_api(url, params)
            
            # 解析JSON响应
            result = response.json()
            
            # 检查API返回状态
            if result.get('status') == '1':
                locations = [GeoPos(float(loc.split(',')[0]), float(loc.split(',')[1])) for loc in result['locations'].split(';')]
                return {
                    'success': True,
                    'locations': locations,
                    'info': result['info']
                }
            else:
                return {
                    'success': False,
                    'info': f"Error {result.get('status')}: {result.get('info')}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'info': f"Request failed: {str(e)}"
            }

    def generate_static_map(self, **kwargs):
        """
        生成高德静态地图
        
        参数：
        key : str - 高德API Key
        location : GeoPos - 中心点坐标，格式"经度,纬度"
        zoom : int - 地图级别[1,17]
        size : str - 图片尺寸，格式"宽*高"，默认400*400
        scale : int - 1普通/2高清
        markers : list - 标注点列表，格式见示例
        labels : list - 标签列表，格式见示例
        paths : list - 路径列表，格式见示例
        traffic : int - 是否显示交通路况(0/1)
        
        返回：图片二进制数据或错误信息
        """
        base_url = "https://restapi.amap.com/v3/staticmap"
        
        # 构建基础参数
        params = {
            'key': self.key,
            'size': kwargs.get('size', '400*400'),
            'scale': kwargs.get('scale', 1),
            'traffic': kwargs.get('traffic', 0)
        }
        
        # 处理中心点和缩放级别
        if 'location' in kwargs and 'zoom' in kwargs:
            params.update({
                'location': f"{kwargs['location'].longitude},{kwargs['location'].latitude}",
                'zoom': kwargs['zoom']
            })
        
        # 构建标注参数
        if 'markers' in kwargs:
            markers_str = self._build_markers(kwargs['markers'])
            params['markers'] = markers_str
        
        # 构建标签参数
        if 'labels' in kwargs:
            labels_str = self._build_labels(kwargs['labels'])
            params['labels'] = labels_str
        
        # 构建路径参数
        if 'paths' in kwargs:
            paths_str = self._build_paths(kwargs['paths'])
            params['paths'] = paths_str
        
        # 发送请求
        response = self._request_api(base_url, params)

        # 检查是否为图片数据
        if response.headers['Content-Type'].startswith('image'):
            return response.content
        else:
            return response.json()

    def _build_markers(self, markers_list):
        """ 构造标注点参数 """
        parts = []
        for marker in markers_list:
            # 支持系统样式或自定义样式
            if marker.get('custom'):
                style = f"-1,{marker['icon_url']},0"
            else:
                style = f"{marker.get('size','small')}," \
                        f"{marker.get('color','0xFF0000')}," \
                        f"{marker.get('label','')}"
            
            locations = ";".join([f"{lon},{lat}" for lon, lat in marker['locations']])
            parts.append(f"{style}:{locations}")
        return "|".join(parts)

    def _build_labels(self, labels_list):
        """ 构造标签参数 """
        parts = []
        for label in labels_list:
            style = f"{label['content']}," \
                    f"{label.get('font',0)}," \
                    f"{label.get('bold',0)}," \
                    f"{label.get('fontSize',16)}," \
                    f"{label.get('fontColor','0xFFFFFF')}," \
                    f"{label.get('background','0x5288d8')}"
            
            locations = ";".join([f"{lon},{lat}" for lon, lat in label['locations']])
            parts.append(f"{style}:{locations}")
        return "|".join(parts)

    def _build_paths(self, paths_list):
        """ 构造路径参数 """
        parts = []
        for path in paths_list:
            style = f"{path.get('weight',5)}," \
                    f"{path.get('color','0x0000FF')}," \
                    f"{path.get('transparency',1)}," \
                    f"{path.get('fillcolor','')}," \
                    f"{path.get('fillTransparency',0.5)}"
            
            locations = ";".join([f"{lon},{lat}" for lon, lat in path['locations']])
            parts.append(f"{style}:{locations}")
        return "|".join(parts)

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def _request_api(self, url, params):
        prepared_url = self._build_full_url(url, params)
        print(prepared_url)
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {str(e)}")
            raise

    def _build_full_url(self, base_url, params):
        """手动构建完整URL"""
        url_parts = list(urlparse(base_url))
        query = dict(parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query, doseq=True)
        url_parts[0] = ""
        url_parts[1] = ""
        url_parts[2] = ""
        return urlunparse(url_parts)


if __name__ == "__main__":
    # 示例使用 替换为你的高德API Key
    # api_key = "<YOUR_API_KEY>"
    
    # 单个坐标转换示例
    coordinates = "120.348117,30.319536"
    api = GaoDeAPI()
    geopos = []
    geopos.append(GeoPos(120.348117,30.319536))
    
    # 调用转换函数
    result = api.convert_coordinates(geopos)
    
    if result['success']:
        print("转换成功！")
        print(f"原始坐标: {coordinates}")
        print(f"转换后坐标: {result['locations']}")
        print("转换后坐标: " + "".join(f"{geopos.longitude},{geopos.latitude}" for geopos in result['locations']))
        print(f"状态信息: {result['info']}")
    else:
        print("转换失败:", result['info'])

    print(f"geopos: {geopos[0]}")
    print(f"new_geopos: {result['locations'][0]}")
    new_geopos = geopos[0]
    # new_geopos = result['locations'][0]

    # # 示例1：基础地图
    # img_data = api.generate_static_map(
    #     location=new_geopos,  # 天安门坐标
    #     zoom=15,
    #     size="600*400",
    #     scale=2
    # )
    # with open("base_map.png", "wb") as f:
    #     f.write(img_data)
    
    # 示例2：带标注点和标签
    markers = [
        {
            'size': 'large',
            'color': '0xFF0000',
            'label': 'A',
            'locations': [
                (new_geopos.longitude, new_geopos.latitude)
            ]
        },
        {
            'custom': True,
            'icon_url': 'https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png',
            'locations': [(new_geopos.longitude, new_geopos.latitude)]
        }
    ]
    
    labels = [
        {
            'content': '天安门广场',
            'fontSize': 14,
            'background': '0xFF0000',
            'locations': [(new_geopos.longitude, new_geopos.latitude)]
        }
    ]
    
    img_data = api.generate_static_map(
        markers=markers,
        labels=labels,
        size="1080*800",
        traffic=1
    )
    with open("map/annotated_map.png", "wb") as f:
        f.write(img_data)
    
    # # 示例3：带路径规划
    # paths = [
    #     {
    #         'weight': 8,
    #         'color': '0x009688',
    #         'locations': [
    #             (116.397428, 39.90923),
    #             (116.407428, 39.91923),
    #             (116.417428, 39.90923)
    #         ],
    #         'fillcolor': '0x80DEEA'
    #     }
    # ]
    
    # img_data = api.generate_static_map(
    #     paths=paths,
    #     size="800*600"
    # )
    # with open("path_map.png", "wb") as f:
    #     f.write(img_data)

     # 初始化配置
    UPLOAD_API = "https://www.imagehub.cc/api/1/upload"
    API_KEY = "chv_ctza_a7f99e53587ab2b6bf6f63255e57bf09965d9b82ac42dda888a90c1ccfcaa10e898122f9439a46e3d1c4f4d904f9a061f19ded67d36eb869bc1cf6a3c02d46bb"
    uploader = ImageHubUploader(UPLOAD_API, API_KEY)

    # 示例1：上传本地文件
    result = uploader.upload_file(
        "map/annotated_map.png",
        title="地图照片",
        description="2025年拍摄",
        tags="旅行,自然",
        album_id="12345",
        expiration="P3D",  # 3天后过期
        nsfw=0,
        format="json"
    )
    print("上传结果:", result)
    print("短链接:", result['url_short'])
