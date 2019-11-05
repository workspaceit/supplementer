from django.conf import settings
from django.db.models import Q
from rest_framework import serializers
from adminapp.models import Buildings, BuildingPlans, BuildingComponents, Tasks
from datetime import datetime


class BuildingSerializer(serializers.ModelSerializer):
    total_tasks = serializers.IntegerField(read_only=True, default=None)
    tasks_done = serializers.IntegerField(read_only=True,  default=None)
    total_flats = serializers.IntegerField(read_only=True,  default=None)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Buildings
        fields = ('id', 'hause_number', 'description', 'display_number', 'total_tasks', 'tasks_done', 'total_flats', 'status')

    def get_status(self, building):
        status = "other"
        current_date = datetime.now()
        if Tasks.objects.filter(building_component__building_id=building.id, building_component__flat__isnull=True, due_date__lt=current_date).exclude(status='done').exists():
            status = "overdue"
        return status


class BuildingPlanSerializer(serializers.ModelSerializer):
    plan_file = serializers.SerializerMethodField()

    class Meta:
        model = BuildingPlans
        fields = ('id', 'title', 'plan_file', 'file_type')

    def get_plan_file(self, plan):
        if plan.plan_file and hasattr(plan.plan_file, 'url'):
            plan_file = plan.plan_file.url
            return plan_file
        else:
            return None


class ComponentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, read_only=True)
    total_tasks = serializers.IntegerField(read_only=True, default=None)
    tasks_done = serializers.IntegerField(read_only=True, default=None)
    status = serializers.SerializerMethodField()

    class Meta:
        model = BuildingComponents
        fields = ('component_id', 'name', 'total_tasks', 'tasks_done', 'status')

    def get_status(self, component):
        status = "other"
        current_date = datetime.now()
        if component.flat:
            if Tasks.objects.filter(building_component__flat_id=component.flat_id, due_date__lt=current_date).filter(Q(Q(building_component__component__parent_id=component.component_id) | Q(building_component__component_id=component.component_id))).exclude(status='done').exists():
                status = "overdue"
        else:
            if Tasks.objects.filter(building_component__building_id=component.building_id, building_component__flat__isnull=True, due_date__lt=current_date).filter(Q(Q(building_component__component__parent_id=component.component_id) | Q(building_component__component_id=component.component_id))).exclude(status='done').exists():
                status = "overdue"
        return status
