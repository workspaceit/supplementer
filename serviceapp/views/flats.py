from django.db.models import Count, Q, F
from rest_framework.permissions import BasePermission
from rest_framework import viewsets, mixins
from rest_framework.views import APIView

from adminapp.models import Flats, FlatPlans, BuildingComponents, Tasks
from rest_framework.pagination import PageNumberPagination
from serviceapp.serializers.flat_serializer import FlatSerializer, FlatPlanSerializer
from serviceapp.serializers.building_serializer import ComponentSerializer
from serviceapp.views.activities import ActivityView


class FlatPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == 'GET':
            return True
        return False


class FlatViewSet(APIView):
    permission_classes = (FlatPermissions,)

    def get(self, request, **kwargs):
        building_id = kwargs['building_id']
        paginator = PageNumberPagination()
        paginator.page_size = 10
        if request.user.is_staff:
            flats = Flats.objects.annotate(total_tasks=Count('buildingcomponents__tasks'), tasks_done=Count('buildingcomponents__tasks', filter=Q(buildingcomponents__tasks__status='done'))).filter(building_id=building_id)
        else:
            flats = Flats.objects.filter(building_id=building_id, buildingcomponents__assign_to=request.user.id).distinct()
        result_page = paginator.paginate_queryset(flats, request)
        serializer = FlatSerializer(result_page, many=True)
        ActivityView.change_active_building(request, building_id)
        return paginator.get_paginated_response(data=serializer.data)


class FlatComponentViewSet(APIView):
    permission_classes = (FlatPermissions,)

    def get(self, request, **kwargs):
        flat_id = kwargs['flat_id']
        paginator = PageNumberPagination()
        paginator.page_size = 10
        if request.user.is_staff:
            components = BuildingComponents.objects.annotate(name=F('component__name')).filter(flat_id=flat_id, component__parent__isnull=True)
            for component in components:
                component.total_tasks = Tasks.objects.filter(building_component__flat_id=flat_id).filter(Q(Q(building_component__component__parent_id=component.component_id) | Q(building_component__component_id=component.component_id))).count()
                component.tasks_done = Tasks.objects.filter(building_component__flat_id=flat_id, status='done').filter(Q(Q(building_component__component__parent_id=component.component_id) | Q(building_component__component_id=component.component_id))).count()
        else:
            components = BuildingComponents.objects.annotate(name=F('component__name')).filter(flat_id=flat_id, component__parent__isnull=True, assign_to=request.user.id).distinct()
        result_page = paginator.paginate_queryset(components, request)
        serializer = ComponentSerializer(result_page, many=True)
        ActivityView.change_active_flat(request, flat_id)
        return paginator.get_paginated_response(data=serializer.data)


class FlatPlanViewSet(APIView):
    permission_classes = (FlatPermissions, )

    def get(self, request, **kwargs):
        flat_id = kwargs['flat_id']
        paginator = PageNumberPagination()
        paginator.page_size = 10
        plans = FlatPlans.objects.filter(flat_id=flat_id)
        result_page = paginator.paginate_queryset(plans, request)
        serializer = FlatPlanSerializer(result_page, many=True)
        ActivityView.change_active_flat(request, flat_id)
        return paginator.get_paginated_response(data=serializer.data)
