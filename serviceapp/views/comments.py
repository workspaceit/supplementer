import os

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from adminapp.models import Comments, Tasks
from rest_framework.pagination import PageNumberPagination

from adminapp.views.common_views import CommonView, NotificationText
from adminapp.views.notification_views import NotificationsView
from serviceapp.serializers.comment_serializer import CommentSerializer
import threading

from adminapp.views.helper import LogHelper



class CommentPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method == 'GET':
                return True
            elif request.method == 'POST':
                return True
            return False
        return False


class CommentsViewSet(APIView):
    permission_classes = (CommentPermissions,)

    def get(self, request, **kwargs):
        task_id = kwargs['task_id']
        paginator = PageNumberPagination()
        paginator.page_size = 10
        comments = Comments.objects.filter(task_id=task_id).order_by('-created_at')
        result_page = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    def post(self, request, **kwargs):
        try:
            task_id = kwargs['task_id']
            comment = ''
            file_list = []
            dir = os.path.join(settings.MEDIA_ROOT, "comments")
            if not os.path.exists(dir):
                os.makedirs(dir)
            if 'files' in request.data:
                files = request.data.getlist('files')
                for file in files:
                    uploaded_file = CommonView.handle_uploaded_file(request, file)
                    if uploaded_file != "":
                        file_list.append(uploaded_file)
            if 'text' in request.data:
                comment = request.data["text"]
            if comment != '' or len(file_list) > 0:
                comment_form = {
                    "text": comment,
                    "file_type": file_list if (len(file_list) > 0) else None,
                    "task_id": task_id,
                    "user": request.user,
                    "type": "text"
                }
                new_comment = Comments(**comment_form)
                new_comment.save()
                task = Tasks.objects.get(id=task_id)
                task.save()
                if request.user.is_staff:
                    user_name = request.user.get_full_name()
                else:
                    user_name = request.user.handworker.company_name
                if comment != '':
                    # Send Notification
                    message = NotificationText.get_task_comment_notification_text(user_name,
                                                                                  task.building_component.component.name)
                    task_thread = threading.Thread(target=NotificationsView.create_notfication,
                                                   args=(request, 'task_comment', message, task_id, request.user.id))
                    task_thread.start()
                if len(file_list) > 0:
                    # Send Notification
                    message = NotificationText.get_attach_file_notification_text(user_name,
                                                                                 task.building_component.component.name)
                    task_thread = threading.Thread(target=NotificationsView.create_notfication,
                                                   args=(request, 'attach_file', message, task_id, request.user.id))
                    task_thread.start()
                paginator = PageNumberPagination()
                paginator.page_size = 10
                comments = Comments.objects.filter(task_id=task_id).order_by('-created_at')
                result_page = paginator.paginate_queryset(comments, request)
                serializer = CommentSerializer(result_page, many=True)
                return paginator.get_paginated_response(data=serializer.data)
            else:
                return Response({'success': False, 'message': "Something went wrong."},
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            LogHelper.efail(e)
            return Response({'success': False, 'message': "Something went wrong."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
