from rest_framework import serializers
from .models import Drone, MissionTarget, MissionAssignment, Group, User, WayPoint
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from django.conf import settings

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Protocol.KDF import PBKDF2
import base64
import json

secret_key="HSUTEMOAPLQHZJUT"

def decrypt(ciphertext: str, secret_key: str) -> dict:
    # Base64 解码
    ciphertext_bytes = base64.b64decode(ciphertext)
    # 提取 Salt（位于第8-16字节）
    assert ciphertext_bytes.startswith(b'Salted__'), "Invalid Salt Header"
    salt = ciphertext_bytes[8:16]
    encrypted_data = ciphertext_bytes[16:]
    # PBKDF2 密钥派生（与 CryptoJS 默认一致）
    # 参数：密码、盐、密钥长度、迭代次数、哈希算法
    key_iv = PBKDF2(
        password=secret_key,
        salt=salt,
        dkLen=32 + 16,  # AES-256 密钥 + 16字节 IV
        count=1,        # CryptoJS 默认迭代次数
        hmac_hash_module=None  # 默认使用 SHA1
    )
    key = key_iv[:32]
    iv = key_iv[32:48]
    # 解密
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return json.loads(decrypted.decode('utf-8'))


class LoginSerializer(serializers.Serializer):
    # 定义接受的登录字段
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True) # write_only表示只在写操作时使用

    # 创建一个新的方法，用于验证登录字段 在调用is_valid()方法时被自动调用
    def validate(self, data):
        # 获取登录字段
        username = data.get('username')
        password = data.get('password')
        if username and password:
            # 使用authenticate()方法验证用户名和密码
            user = User.objects.filter(username=username).first()
            if user and check_password(password + settings.SECRET_KEY, user.password):
            # if user:
                if not user.is_active:
                    raise serializers.ValidationError("用户已被禁用。")
            else:
                raise serializers.ValidationError("用户名或密码错误。")
        else:
            raise serializers.ValidationError("必须提供用户名和密码。")

        data['user'] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    # Meta类用于定义序列化器的元数据
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'] + settings.SECRET_KEY)
        user = User.objects.create(**validated_data)
        return user

# 使用了超链接关系
class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="polls:user-detail")
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class DroneSerializer(serializers.ModelSerializer):
    # 自定义字段：将dock_status的整数值转为中文（如"作业中"）
    dock_status_display = serializers.CharField(
        source="get_dock_status_display", 
        read_only=True
    )
    class Meta:
        model = Drone
        fields = "__all__"

class MissionTargetSerializer(serializers.ModelSerializer):

    class Meta:
        model = MissionTarget
        fields = "__all__"

class MissionAssignmentSerializer(serializers.ModelSerializer):
    # 关联字段：显示该任务的所有无人机（只读）
    drone = DroneSerializer(
        many=True, 
        read_only=True
    )
    
    # 关联字段：显示该任务的所有目标（只读）
    target = MissionTargetSerializer(
        many=True, 
        read_only=True
    )

    # 自定义字段：将status的整数值转为可读的文本（如"执行中"）
    status_display = serializers.CharField(
        source="get_status_display", 
        read_only=True
    )
    
    # 文件字段：生成完整的URL（需配合`context={'request': request}`使用）
    video_recording = serializers.FileField(
        max_length=None, 
        allow_empty_file=False, 
        use_url=True
    )
    thumbnail = serializers.ImageField(
        max_length=None, 
        use_url=True, 
        allow_null=True
    )

    class Meta:
        model = MissionAssignment
        fields = "__all__"
        extra_kwargs = {
            "drone": {"write_only": True},  # 写操作时仅接受ID
            "target": {"write_only": True},
        }

class WayPointSerializer(serializers.ModelSerializer):
    # 关联字段：显示所有分配到此目标的无人机任务（只读）
    assignments = MissionAssignmentSerializer(
        many=True, 
        read_only=True
    )
    # 关联字段：显示所有分配到此目标的无人机任务（只读）
    drone = DroneSerializer(
        many=True, 
        read_only=True
    )
    class Meta:
        model = WayPoint
        fields = "__all__"
        