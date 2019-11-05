from django.db.models import Count, Q, F
from rest_framework.permissions import BasePermission
from rest_framework import viewsets, mixins
from rest_framework.views import APIView

from adminapp.models import Buildings, BuildingPlans, BuildingComponents, Tasks
from rest_framework.pagination import PageNumberPagination
from serviceapp.serializers.building_serializer import BuildingSerializer, BuildingPlanSerializer, ComponentSerializer
from serviceapp.views.activities import ActivityView


class BuildingPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == 'GET':
            return True
        return False


class BuildingViewSet(APIView):
    permission_classes = (BuildingPermissions,)

    def get(self, request, **kwargs):
        project_id = kwargs['project_id']
        paginator = PageNumberPagination()
        paginator.page_size = 10
        if request.user.is_staff:
            buildings = Buildings.objects.annotate(total_flats=Count('flats', distinct=True), total_tasks=Count('buildingcomponents__tasks', filter=Q(buildingcomponents__flat__isnull=True)), tasks_done=Count('buildingcomponents__tasks', filter=Q(buildingcomponents__tasks__status='done', buildingcomponents__flat__isnull=True))).filter(project_id=project_id)
        else:
            buildings = Buildings.objects.filter(project_id=project_id, buildingcomponents__assign_to=request.user.id).distinct()
        result_page = paginator.paginate_queryset(buildings, request)
        serializer = BuildingSerializer(result_page, many=True)
        ActivityView.change_active_project(request, project_id)
        return paginator.get_paginated_response(data=serializer.data)


class BuildingComponentViewSet(APIView):
    permission_classes = (BuildingPermissions,)

    def get(self, request, **kwargs):
        building_id = kwargs['building_id']
        paginator = PageNumberPagination()
        paginator.page_size = 10
        if request.user.is_staff:
            components = BuildingComponents.objects.annotate(name=F('component__name')).filter(building_id=building_id, flat__isnull=True, component__parent__isnull=True)
            for component in components:
                component.total_tasks = Tasks.objects.filter(building_component__building_id=building_id,
                                                             building_component__flat__isnull=True).filter(Q(Q(building_component__component__parent_id=component.component_id) | Q(building_component__component_id=component.component_id))).count()
                component.tasks_done = Tasks.objects.filter(building_component__building_id=building_id,building_component__flat__isnull=True, status='done').filter(Q(Q(building_component__component__parent_id=component.component_id) | Q(building_component__component_id=component.component_id))).count()
        else:
            components = BuildingComponents.objects.annotate(name=F('component__name')).filter(building_id=building_id,
                                                                                               flat__isnull=True,
                                                                                               component__parent__isnull=True, assign_to=request.user.id).distinct()
        result_page = paginator.paginate_queryset(components, request)
        serializer = ComponentSerializer(result_page, many=True)
        ActivityView.change_active_building(request, building_id)
        return paginator.get_paginated_response(data=serializer.data)


class BuildingPlanViewSet(APIView):
    permission_classes = (BuildingPermissions, )

    def get(self, request, **kwargs):
        building_id = kwargs['building_id']
        paginator = PageNumberPagination()
        paginator.page_size = 10
        plans = BuildingPlans.objects.filter(building_id=building_id)
        result_page = paginator.paginate_queryset(plans, request)
        serializer = BuildingPlanSerializer(result_page, many=True)
        ActivityView.change_active_building(request, building_id)
        return paginator.get_paginated_response(data=serializer.data)
