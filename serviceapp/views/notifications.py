from rest_framework.permissions import BasePermission
from rest_framework.views import APIView

from adminapp.models import NotificationStatus, ProjectStuff
from rest_framework.pagination import PageNumberPagination
from serviceapp.serializers.notification_serializer import NotificationSerializer
from django.http.response import JsonResponse

from pushnotificationapp.models import Subscribers
from adminapp.views.helper import LogHelper
from rest_framework import viewsets, status
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from django.db import transaction


class NotificationPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == 'GET':
            return True
        return False


class NotificationsViewSet(APIView):
    permission_classes = (NotificationPermissions,)

    def get(self, request, **kwargs):
        notifications = NotificationStatus.objects.filter(user_id=request.user.id).order_by('-sending_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(notifications, request)
        serializer = NotificationSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)


class SubscriberDevice(APIView):

    @api_view(["post"])
    @login_required()
    def update_device_info(request):
        try:
            if request.user.is_authenticated:
                user_id = request.user.id
                device = request.data.pop("device", '')
                endpoint = request.data.pop("endpoint", '')
                reset_endpoint = Subscribers.objects.filter(user=user_id, device=device)
                if reset_endpoint.exists():
                    Subscribers.objects.filter(id=reset_endpoint[0].id).update(endpoint=endpoint)
                    return JsonResponse({'success': True, 'message': "Device Info Updated Successfully"}, status=status.HTTP_200_OK)
                else:
                    try:
                        Subscribers(user_id=user_id, endpoint=endpoint, device=device).save()
                        return JsonResponse({'success': True, 'message': "Device Info Inserted Successfully"}, status=status.HTTP_200_OK)
                    except Exception as e:
                        return JsonResponse({'success': False, 'message': "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return JsonResponse({'success': False, 'message': "Session Time Out"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            LogHelper.efail(e)
            return JsonResponse({'status': False, 'message': "Something went wrong."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
