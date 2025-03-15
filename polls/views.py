from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.db.models import F, Prefetch
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader

from .models import Question, Choice, User, Group, Drone, MissionTarget, MissionAssignment, WayPoint


from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import LoginForm, RegisterForm

def index(request):
    return render(request, "polls/index.html", {
        "latest_question_list": Question.objects.order_by("-pub_date")[:5],
        "username": request.user.username if request.user.is_authenticated else None
    })

def login(request):
    if request.user.is_authenticated:
        return redirect("polls:index")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            # 获取表单数据 
            username = form.cleaned_data["username"]
            raw_password = form.cleaned_data["password"]
            user = User.objects.filter(username=username).first()
            if user and check_password(raw_password + settings.SECRET_KEY, user.password):
                auth_login(request, User.objects.get(username=username))
                request.session["is_login"] = True
                return redirect("polls:drone_system")
            else:
                    return render(request, "polls/login.html", {
                        "form": form, 
                        "error": "用户名或密码错误",
                        "username": username
                    })
    else:
        form = LoginForm()
    return render(request, "polls/login.html", {"form": form})

def register(request):
    if request.user.is_authenticated:  # 登录状态不允许注册
        return redirect("polls:index")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 获取表单数据
            password = form.cleaned_data["password"]
            user = form.save(commit=False)
            user.password = make_password(password + settings.SECRET_KEY)
            user.save()
            return redirect("polls:login")
        else:
            return render(request, "polls/register.html", {
                "form": form, 
                "error": form.errors
            })
    else:
        form = RegisterForm()
    return render(request, "polls/register.html", {"form": form})

def logout(request):
    if not request.user.is_authenticated:  # 如果本来就未登录，也就没有登出一说
        return redirect("polls:index")
    auth_logout(request)
    return redirect('polls:index')
    
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import json

def drone_system(request):
    # 基础验证
    if not request.user.is_authenticated:
        return redirect("polls:index")
    
    # 获取用户所有无人机及相关任务数据并预加载关联
    drones = Drone.objects.filter(user=request.user).prefetch_related(
        Prefetch('missions', 
            queryset=MissionTarget.objects.prefetch_related('assignments')
            )
        ).order_by("-time_stamp")
    
    # 构建GeoJSON数据
    targets_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [t.longitude, t.latitude]
                },
                "properties": {
                    "id": t.id,
                    "name": t.name,
                    "status": max(a.status for a in t.assignments.all()),
                    "drones": [
                        {
                            "sn": a.drone.drone_sn,
                            "status": a.status,
                            "video": a.video_recording.url if a.video_recording else None,
                            "thumbnail": a.thumbnail.url if a.thumbnail else None,
                            "time": f"{a.start_time:%Y-%m-%d %H:%M} ~ {a.end_time:%Y-%m-%d %H:%M}" if a.end_time else "进行中"
                        }
                        for a in t.assignments.all()
                    ]
                }
            }
            for t in MissionTarget.objects.filter(assignments__drone__user=request.user).distinct()
        ]
    }
       
    # 设置默认中心坐标
    default_center = [116.397428, 39.90923]  # 北京天安门坐标

    # 获取第一个存在且有效的无人机坐标
    center = default_center
    for drone in drones:
        if drone.longitude and drone.latitude:
            center = [drone.longitude, drone.latitude]
            break

    # 构建上下文
    context = {
        'drones': drones,
        'geo_json': serialize_geo_json(drones),  # 新增地理JSON数据
        'status_choices': Drone.DOCK_STATUS_CHOICES,
        'map_config': {
            'key': '1',#'fe97d423fdb0de8f8bc51bfc01b576b5',
            'center': center,
            'zoom': 17,
            # 'map_style': 'amap://styles/whitesmoke'
        },
        'username': request.user.username if request.user.is_authenticated else None,
        'targets_geojson': json.dumps(targets_geojson) # 新增目标地理JSON数据
    }

    return render(request, "polls/drone_system.html", context)


def serialize_geo_json(queryset):
    """生成GeoJSON格式数据"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [drone.longitude, drone.latitude]
                },
                "properties": drone_serializer(drone)
            } for drone in queryset
        ]
    }

def drone_serializer(drone):
    """自定义序列化器"""
    return {
        "id": drone.id,
        "sn": drone.drone_sn,
        "status": {
            "code": drone.dock_status,
            "text": drone.get_dock_status_display(),
            "class": get_status_class(drone.dock_status)
        },
        "battery": drone.capacity_percent,
        "altitude": drone.height,
        "last_update": drone.time_stamp,
        "details_url": f"/drones/{drone.id}/"
    }

def get_status_class(status_code):
    """获取状态CSS类"""
    status_classes = {
        0: 'available',
        1: 'debugging',
        2: 'upgrading',
        3: 'working',
        -1: 'offline'
    }
    return status_classes.get(status_code, 'unknown')

# API端点（可选）
@require_GET
def drone_data_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    drones = Drone.objects.filter(user=request.user)
    return JsonResponse({
        "data": [drone_serializer(drone) for drone in drones],
        "meta": {
            "count": drones.count(),
            "user": request.user.username
        }
    })

# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "polls/detail.html", {"question": question})
#     # try:
#     #     question = Question.objects.get(pk=question_id)
#     # except Question.DoesNotExist:
#     #     raise Http404("Question does not exist")
#     # return render(request, "polls/detail.html", {"question": question})
#     # return HttpResponse("You're looking at question %s." % question_id)

# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "polls/results.html", {"question": question})
#     # return HttpResponse("You're looking at the results of question %s." % question_id)

from django.views import generic
    
# class IndexView(generic.ListView):
#     template_name = "polls/index.html"
#     context_object_name = "latest_question_list"

#     """Return the last five published questions."""
#     def get_queryset(self):
#         return Question.objects.order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html", 
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            }
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    # return HttpResponse("You're voting on question %s." % question_id)




# tutorial/quickstart/views.py

# from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets

from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import status
from rest_framework.authtoken.models import Token
# from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
# import sys
# sys.path.append("..")
from .drone_system.DroneSystem import DroneSystem
# import logging
import traceback
from django.utils import timezone
from asgiref.sync import sync_to_async
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s.%(msecs)03d-%(name)s-%(levelname)s - %(message)s',
#     datefmt='%H:%M:%S',
#     handlers=[
#         logging.FileHandler('views.log'),
#         logging.StreamHandler()
#     ]
# )
# 延迟初始化（在第一次使用时创建）
_drone_system = None

def get_drone_system():
    global _drone_system
    if _drone_system is None:
        _drone_system = DroneSystem()
    return _drone_system

_mission_assignment = None
_mission_assignment_count = 0

def start_mission_assignment():
    """Start or reuse an existing mission assignment"""
    global _mission_assignment, _mission_assignment_count
    
    if _mission_assignment is None:
         # Create new mission assignment with required fields
        _mission_assignment = MissionAssignment(
            name=f"任务_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=timezone.now(),  # Explicitly set start_time
            status=0  # Set initial status
        )
        try:
            _mission_assignment.save()
        except Exception as e:
            print(f"Failed to create mission assignment: {str(e)}")
            raise
    
    _mission_assignment_count += 1
    return _mission_assignment

def stop_mission_assignment():
    """Stop mission assignment if no more drones are using it"""
    global _mission_assignment, _mission_assignment_count
    
    if _mission_assignment_count > 0:
        _mission_assignment_count -= 1
    
    if _mission_assignment_count <= 0:
        if _mission_assignment:
            _mission_assignment.status = 2  # Set status to completed
            _mission_assignment.end_time = timezone.now()
            _mission_assignment.save()
        _mission_assignment = None

async def run_drone(drone_id: int):
    """Start drone operation asynchronously"""
    drone_system = get_drone_system()
    drone = await sync_to_async(Drone.objects.get)(id=drone_id)
    mission_assignment = await sync_to_async(start_mission_assignment)()
    
    config = {
        "drone_id": drone.id,
        "drone_hardware": {
            "base_url": "https://all.xinkongan.com",
            "app_id": drone.app_id,
            "app_secret": drone.app_secret,
            "device_sn": drone.drone_sn,
            "mission_id": mission_assignment.id
        }
    }
    
    return await sync_to_async(drone_system.run_drone)(config, drone_id)

async def stop_drone(drone_id: int):
    """Stop drone operation asynchronously"""
    await sync_to_async(stop_mission_assignment)()
    drone_system = get_drone_system()
    return await sync_to_async(drone_system.stop_drone)(drone_id=drone_id)
import asyncio
from asgiref.sync import async_to_sync
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def drone_manage_api(request):
    """Handle drone management operations with proper async handling"""
    if not request.user.is_authenticated:
        return Response(
            {"error": "未登录"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        data = request.data
        if not data.get("type") or not data.get("id"):
            return Response(
                {"error": "缺少必要字段: type 或 id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        drone_id = data["id"]
        operation_type = data["type"]

        # Verify drone exists and belongs to user
        try:
            drone = Drone.objects.select_related('user').get(
                id=drone_id, 
                user=request.user
            )
        except Drone.DoesNotExist:
            return Response(
                {"error": f"无人机 {drone_id} 不存在或无权限操作"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Handle operations with timeout
        async def handle_operation():
            try:
                if operation_type == "start":
                    await asyncio.wait_for(
                        asyncio.create_task(run_drone(drone_id)),
                        timeout=5.0  # 5 second timeout
                    )
                elif operation_type == "stop":
                    await asyncio.wait_for(
                        asyncio.create_task(stop_drone(drone_id)),
                        timeout=5.0
                    )
                else:
                    raise ValueError(f"不支持的操作类型: {operation_type}")
                
                return None  # Operation successful
            except asyncio.TimeoutError:
                return "操作超时"
            except Exception as e:
                return str(e)

        # Run operation with async handling
        error = async_to_sync(handle_operation)()
        if error:
            return Response(
                {"error": error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            "message": "操作成功",
            "drone_id": drone_id,
            "operation": operation_type
        })

    except Exception as e:
        return Response({
            "error": "操作失败",
            "detail": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# api_view装饰器用于将基于函数的视图转换为API视图
@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny]) # 任何用户都可以访问
def login_api(request):
    # request['Access - Control - Allow - Origin'] = '*'
    if request.user.is_authenticated:
        # print("你已经登陆了" ,request.data)
        return Response({"message": "你已经登录了！", "token":
            Token.objects.get_or_create(user=request.user)[0].key}, status=status.HTTP_200_OK)
        # return Response({"error": "你已经登录了！"}, status=status.HTTP_400_BAD_REQUEST)
     
    # 提取加密字符串
    # encrypted_str = request.data.get('encrypted_data')
    # if not encrypted_str:
    #     print("缺少加密数据" ,request.data)
    #     return Response({"error": "缺少加密数据"}, status=status.HTTP_400_BAD_REQUEST)
    
    # 使用序列化器验证登录字段
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid(): # 功能：验证数据是否有效，验证内容包括字段类型、字段值、字段长度等，验证通过返回True，否则返回False，validate()方法会自动调用
        user = serializer.validated_data['user'] # 从序列化器中获取验证后的用户对象
        # refresh = RefreshToken.for_user(user) # 生成Token
        auth_login(request, user) # 使用Django内置的登录方法
        return Response({"message": "登录成功。", "token":
            Token.objects.get_or_create(user=user)[0].key}, status=status.HTTP_200_OK)
    print(serializer.errors, request.data, Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST))
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_api(request):
    if request.user.is_authenticated:
        return Response({"error": "你已经登录了！"}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid(): # 功能：验证数据是否有效，验证内容包括字段类型、字段值、字段长度等，验证通过返回True，否则返回False
        serializer.save() # 调用序列化器的create()方法来创建一个新的User实例。
        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_api(request):
    if not request.user.is_authenticated:
        return Response({"error": "你还没有登录！"}, status=status.HTTP_400_BAD_REQUEST)
    Token.objects.filter(user=request.user).delete() # 删除Token
    auth_logout(request) # 使用Django内置的登出方法
    #清楚客户端的cookie
    response = Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
    response.delete_cookie('token') 
    return response

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser] # 仅管理员可操作

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        # 获取当前用户
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class DroneViewSet(viewsets.ModelViewSet):
    """
    无人机管理API端点，支持完整的CRUD操作。
    包含以下功能：
    - 查询无人机（GET /drones/）
    - 创建无人机（POST /drones/）
    - 获取单个无人机详情（GET /drones/{id}/）
    - 更新/删除无人机（PUT/PATCH/DELETE /drones/{id}/）
    """
    serializer_class = DroneSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = '-created_at'  # 默认排序字段

    def get_queryset(self):
        """获取当前用户的无人机，并预取关联数据"""
        return Drone.objects.prefetch_related('assignments').filter(
            user=self.request.user
        ).order_by(self.ordering)

    def perform_create(self, serializer):
        """创建时自动关联当前用户"""
        serializer.save(user=self.request.user)


class MissionTargetViewSet(viewsets.ModelViewSet):
    """
    任务目标管理API端点，支持：
    - 查看/创建/修改任务目标
    - 嵌套显示关联的任务分配记录（通过序列化器）
    """
    queryset = MissionTarget.objects.all().order_by('-created_at')
    serializer_class = MissionTargetSerializer
    permission_classes = [permissions.IsAdminUser]  # 仅管理员可修改任务目标

class MissionAssignmentViewSet(viewsets.ModelViewSet):
    """
    任务分配管理API端点，特性：
    - 自动生成文件URL（需传递request上下文）
    - 唯一性约束：同一无人机不能重复分配同一目标
    """
    queryset = MissionAssignment.objects.all().order_by('-start_time')
    serializer_class = MissionAssignmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # 认证用户可写，其他只读

    # lookup_field = "id"  # 如果主键字段名不是 pk

    def get_serializer_context(self):
        """向序列化器传递request，用于生成文件完整URL"""
        return {'request': self.request}



