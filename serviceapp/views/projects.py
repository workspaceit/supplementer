from django.db.models import Count, Q
from rest_framework.permissions import BasePermission
from rest_framework import viewsets, mixins
from rest_framework.views import APIView

from adminapp.models import Projects, ProjectStuff, ProjectPlans, BuildingComponents
from rest_framework.pagination import PageNumberPagination
from serviceapp.serializers.project_serializer import ProjectSerializer, PlanSerializer


class ProjectPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == 'GET':
            return True
        return False


# Override default pagination settings
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10


class ProjectViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ProjectStuff.objects.filter(project__is_complete=False)
    serializer_class = ProjectSerializer
    permission_classes = (ProjectPermissions,)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Projects.objects.annotate(total_tasks=Count('buildings__buildingcomponents__tasks'),
                                                 tasks_done=Count('buildings__buildingcomponents__tasks', filter=Q(
                                                     buildings__buildingcomponents__tasks__status='done'))).filter(is_complete=False)
        elif self.request.user.is_staff:
            projects = list(ProjectStuff.objects.values('id').filter(user_id=self.request.user.id,
                                                                     project__is_complete=False).values_list('project_id', flat=True))
            queryset = Projects.objects.annotate(total_tasks=Count('buildings__buildingcomponents__tasks'),
                                                 tasks_done=Count('buildings__buildingcomponents__tasks', filter=Q(
                                                     buildings__buildingcomponents__tasks__status='done'))).filter(
                id__in=projects)
        else:
            queryset = Projects.objects.filter(buildings__buildingcomponents__assign_to=self.request.user.id, is_complete=False).distinct()
        return queryset


class ProjectPlanViewSet(APIView):
    permission_classes = (ProjectPermissions, )

    def get(self, request, **kwargs):
        project_id = kwargs['project_id']
        paginator = PageNumberPagination()
        paginator.page_size = 10
        plans = ProjectPlans.objects.filter(project_id=project_id)
        result_page = paginator.paginate_queryset(plans, request)
        serializer = PlanSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)
