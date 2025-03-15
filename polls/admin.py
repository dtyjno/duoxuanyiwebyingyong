from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

# Register your models here.
from .models import Question, Drone, MissionTarget, MissionAssignment, WayPoint

from django.contrib import admin
from .models import Question, Drone, MissionTarget, MissionAssignment, WayPoint

def get_all_field_names(model):
    return [field.name for field in model._meta.get_fields()]

@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'drone_sn', 'user', 'dock_status', 'capacity_percent')
    list_filter = ('dock_status', 'user')
    search_fields = ('name', 'drone_sn')
    filter_horizontal = ('assignments',)  # Changed from 'missions' to 'assignments'

@admin.register(MissionAssignment)
class MissionAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_time', 'end_time', 'status')
    list_filter = ('status',)
    search_fields = ('name',)
    filter_horizontal = ('targets',)

# Simple registrations for other models
admin.site.register(Question)
admin.site.register(MissionTarget)
admin.site.register(WayPoint)