from django.db.models import Q, F
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView

from adminapp.models import Tasks, BuildingComponents, Comments
from rest_framework.pagination import PageNumberPagination

from adminapp.views.common_views import NotificationText
from adminapp.views.helper import LogHelper
from adminapp.views.notification_views import NotificationsView
from serviceapp.serializers.task_serializer import TaskSerializer, TaskDetailsSerializer
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.db import transaction
import threading


class TaskPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == 'GET':
            return True
        return False


class BuildingTasksViewSet(APIView):
    permission_classes = (TaskPermissions,)

    def get(self, request, **kwargs):
        building_id = kwargs['building_id']
        component_id = kwargs['component_id']
        status = request.GET.get('type')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        if status == 'pending':
            tasks = Tasks.objects.annotate(name=F('building_component__component__name'), description=F('building_component__description')).filter(building_component__building_id=building_id, building_component__flat__isnull=True).filter(Q(Q(building_component__component__parent_id=component_id) | Q(building_component__component_id=component_id))).exclude(status='done')
        elif status == 'done':
            tasks = Tasks.objects.annotate(name=F('building_component__component__name'), description=F('building_component__description')).filter(
                building_component__building_id=building_id,
                building_component__flat__isnull=True, status='done').filter(Q(
                Q(building_component__component__parent_id=component_id) | Q(
                    building_component__component_id=component_id)))
        else:
            tasks = Tasks.objects.annotate(name=F('building_component__component__name'), description=F('building_component__description')).filter(building_component__building_id=building_id,
                                         building_component__flat__isnull=True).filter(Q(
                Q(building_component__component__parent_id=component_id) | Q(
                    building_component__component_id=component_id)))
        result_page = paginator.paginate_queryset(tasks, request)
        serializer = TaskSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)


class FlatTasksViewSet(APIView):
    permission_classes = (TaskPermissions,)

    def get(self, request, **kwargs):
        flat_id = kwargs['flat_id']
        component_id = kwargs['component_id']
        type = request.data.pop("type", None)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        if type == 'pending':
            tasks = Tasks.objects.annotate(name=F('building_component__component__name'), description=F('building_component__description')).filter(building_component__flat_id=flat_id).filter(Q(Q(building_component__component__parent_id=component_id) | Q(building_component__component_id=component_id))).exclude(status='done')
        elif type == 'done':
            tasks = Tasks.objects.annotate(name=F('building_component__component__name'), description=F('building_component__description')).filter(building_component__flat_id=flat_id, status='done').filter(Q(
                        Q(building_component__component__parent_id=component_id) | Q(
                            building_component__component_id=component_id)))
        else:
            tasks = Tasks.objects.annotate(name=F('building_component__component__name'), description=F('building_component__description')).filter(building_component__flat_id=flat_id).filter(Q(
                        Q(building_component__component__parent_id=component_id) | Q(
                            building_component__component_id=component_id)))
        result_page = paginator.paginate_queryset(tasks, request)
        serializer = TaskSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)


class TaskDetailsViewSet(APIView):
    permission_classes = (TaskPermissions,)

    def get(self, request, **kwargs):
        try:
            task_id = kwargs['task_id']
            task = Tasks.objects.get(id=task_id)
            task.name = task.building_component.component.name
            task.description = task.building_component.description
            if task.building_component.component.parent:
                assign_to_user = BuildingComponents.objects.filter(
                    component_id=task.building_component.component.parent_id,
                    building_id=task.building_component.building_id, flat_id=task.building_component.flat_id).first()
            else:
                assign_to_user = task.building_component
            if assign_to_user.assign_to:
                assign_to = {
                    "company_name": assign_to_user.assign_to.handworker.company_name,
                    "avatar": assign_to_user.assign_to.avatar.url if assign_to_user.assign_to.avatar else ''
                }
            else:
                assign_to = None
            task.assign_to = assign_to
            status_list = [{"option": "to_do", "value": "Nicht Begonnen"}, {"option": "in_progress", "value": "In Bearbeitung"}, {"option": "done", "value": "Fertig"}]
            task.status_list = status_list
            comments = Comments.objects.filter(task_id=task_id).order_by('-created_at')
            task_comments = []
            more_comments = False
            if comments.count() > 10:
                more_comments = True
            comments_list = comments[:10]
            for comment in comments_list:
                if comment.user.is_staff:
                    user_info = {
                        "name": comment.user.get_full_name(),
                        "avatar": comment.user.avatar.url if comment.user.avatar else ''
                    }
                else:
                    user_info = {
                        "name": comment.user.handworker.company_name,
                        "avatar": comment.user.avatar.url if comment.user.avatar else ''
                    }
                comment_data = {
                    "text": comment.text,
                    "type": comment.type,
                    "file_type": comment.file_type if comment.file_type else None,
                    "user": user_info,
                    "created_at": str(comment.created_at)
                }
                task_comments.append(comment_data)
            task.comments = task_comments
            task.more_comments = more_comments
            task.total_comments = comments.count()
            serializer = TaskDetailsSerializer(task)
            NotificationsView.read_notification(request, task_id)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            LogHelper.efail(e)
            return Response({'success': False, 'message': "Something went wrong."},
                            status=status.HTTP_404_NOT_FOUND)

    @api_view(["post"])
    @login_required()
    @transaction.atomic()
    def change_task_status(request, task_id):
        try:
            with transaction.atomic():
                response = {}
                task_status = request.data.pop("status", '')
                task = Tasks.objects.get(id=task_id)
                task.status = task_status
                task.save()
                # Send Notification
                if request.user.is_staff:
                    user_name = request.user.get_full_name()
                else:
                    user_name = request.user.handworker.company_name
                message = NotificationText.get_change_task_status_notification_text(user_name,
                                                                                    task.building_component.component.name,
                                                                                    task.status)
                task_thread = threading.Thread(target=NotificationsView.create_notfication,
                                        args=(request, 'change_task_status', message, task_id, request.user.id))
                task_thread.start()

                response['success'] = True
                response['message'] = "Task status changed successfully"
                return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            LogHelper.efail(e)
            return Response({'status': False, 'message': "Something went wrong."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @api_view(["post"])
    @login_required()
    @transaction.atomic()
    def change_task_due_date(request, task_id):
        try:
            with transaction.atomic():
                response = {}
                if not request.user.is_staff:
                    raise ModuleNotFoundError
                due_date = request.data.pop("due_date", '')
                task = Tasks.objects.get(id=task_id)
                task.due_date = due_date
                task.save()
                # Send Notification
                message = NotificationText.get_change_due_date_notification_text(request.user.get_full_name(),
                                                                                 task.building_component.component.name, due_date)
                task_thread = threading.Thread(target=NotificationsView.create_notfication,
                                               args=(request, 'change_due_date', message, task_id, request.user.id))
                task_thread.start()
                response['success'] = True
                response['message'] = "Deadline Update successfully"
                return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            LogHelper.efail(e)
            return Response({'status': False, 'message': "Something went wrong."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
