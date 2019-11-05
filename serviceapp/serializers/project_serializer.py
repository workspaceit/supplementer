from django.conf import settings
from rest_framework import serializers
from adminapp.models import Projects, ProjectPlans


class ProjectSerializer(serializers.ModelSerializer):
    total_tasks = serializers.IntegerField(read_only=True, default=None)
    tasks_done = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Projects
        fields = ('id', 'name', 'address', 'description', 'city', 'type', 'energetic_standard', 'total_tasks', 'tasks_done')


class PlanSerializer(serializers.ModelSerializer):
    plan_file = serializers.SerializerMethodField()

    class Meta:
        model = ProjectPlans
        fields = ('id', 'title', 'plan_file', 'file_type')

    def get_plan_file(self, plan):
        if plan.plan_file and hasattr(plan.plan_file, 'url'):
            plan_file = plan.plan_file.url
            return plan_file
        else:
            return None
