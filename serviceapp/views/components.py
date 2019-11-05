from django.db.models import F
from rest_framework import status, pagination
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from adminapp.models import QrCode, BuildingComponents

from adminapp.views.helper import LogHelper
from serviceapp.serializers.building_serializer import ComponentSerializer
from serviceapp.views.activities import ActivityView


class ComponentPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == 'GET':
            return True
        return False


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data, flat, building, project):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
            "flat": flat,
            "building": building,
            "project": project,
        })


class ComponentsViewSet(APIView):
    permission_classes = (ComponentPermissions,)
    pagination_class = CustomPagination

    def get(self, request):
        try:
            unique_key = request.GET.get("unique_key")
            scan_obj = QrCode.objects.filter(unique_key=unique_key).first()
            if scan_obj.flat:
                if request.user.is_staff:
                    components = BuildingComponents.objects.annotate(name=F('component__name')).filter(flat_id=scan_obj.flat_id, component__parent__isnull=True)
                else:
                    components = BuildingComponents.objects.annotate(name=F('component__name')).filter(
                        flat_id=scan_obj.flat_id, component__parent__isnull=True, assign_to_id=request.user.id)
            else:
                if request.user.is_staff:
                    components = BuildingComponents.objects.annotate(name=F('component__name')).filter(building_id=scan_obj.building_id, flat__isnull=True, component__parent__isnull=True)
                else:
                    components = BuildingComponents.objects.annotate(name=F('component__name')).filter(
                        building_id=scan_obj.building_id, flat__isnull=True, component__parent__isnull=True, assign_to_id=request.user.id)
            if len(components) < 1:
                return Response({'success': False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
            if scan_obj.flat:
                ActivityView.change_active_flat(request, scan_obj.flat_id)
            else:
                ActivityView.change_active_building(request, scan_obj.building_id)
            paginator = CustomPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(components, request)
            serializer = ComponentSerializer(result_page, many=True)
            if scan_obj.flat:
                flat_info = {
                    "id": scan_obj.flat.id,
                    "number": scan_obj.flat.number
                }
            else:
                flat_info = None
            building_info = {
                "id": scan_obj.building.id,
                "display_number": scan_obj.building.display_number
            }
            project_info = {
                "id": scan_obj.building.project.id,
                "name": scan_obj.building.project.name
            }
            return paginator.get_paginated_response(data=serializer.data, flat=flat_info, building=building_info, project=project_info)
        except Exception as e:
            LogHelper.efail(e)
            return Response({'status': False, 'message': "Something went wrong."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
