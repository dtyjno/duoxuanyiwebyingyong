from django.urls import path, include

from . import views

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'drones', views.DroneViewSet, basename='drone')
router.register(r'targets', views.MissionTargetViewSet)
router.register(r'assignments', views.MissionAssignmentViewSet)



app_name = "polls"
urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('drone_system', views.drone_system, name='drone_system'),

    # path('', views.IndexView.as_view(), name='index'),
    # ex: /polls/5/
    # path('<int:question_id>/', views.detail, name='detail'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # ex: /polls/5/results/
    # path('<int:question_id>/results/', views.results, name='results'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # ex: /polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),

    # path('api/drones/<str:drone_sn>/control/', views.DroneControlView.as_view(), name='drone-control'),
    # path('api/drones/<str:drone_sn>/status/', views.DroneStatusView.as_view(), name='drone-status'),

    path('api/login/', views.login_api, name='api/login'),
    path('api/register/', views.register_api, name='api/register'),
    path('api/logout/', views.logout_api, name='api/logout'),
    path('api/drone_manage/', views.drone_manage_api, name='api/drone_manage'),
    
    path('api/', include(router.urls)), # 将视图集注册到 router 类来自动生成 API 的 URL conf
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')) # 默认的登录和注销视图
]
# Compare this snippet from polls/views.py: