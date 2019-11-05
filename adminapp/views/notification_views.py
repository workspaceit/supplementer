import math
from datetime import datetime
import json

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views import generic
from adminapp.models import Notification, NotificationStatus, BuildingComponents, ProjectStuff, Users
from adminapp.views.helper import LogHelper


class NotificationsView(generic.DetailView):
    def get(self, request, *args, **kwargs):
        response = {}
        try:
            notifications = NotificationStatus.objects.filter(user_id=request.user.id).order_by('-sending_at')
            response['more_notifications'] = False
            if notifications.count() > 20:
                response['more_notifications'] = True
            notifications_list = notifications[:20]
            response['notifications_list'] = notifications_list
            response['today'] = datetime.today().strftime('%Y-%m-%d')
            return render(request, 'profiles/notifications.html', response)
        except Exception as e:
            LogHelper.efail(e)
            return redirect('index')

    def get_more_notifications(request):
        response_data = {}
        try:
            response = {}
            page_num = int(request.POST.get('page_number'))
            notifications = NotificationStatus.objects.filter(user_id=request.user.id).order_by('-sending_at')
            total = len(notifications)
            limit = 20
            more_btn_visible = True
            if total > limit:
                offset = (page_num - 1) * limit
                highest = (offset + limit)
                no_of_pages = math.ceil(total / limit)
                pages = range(1, no_of_pages + 1)
                if page_num in pages:
                    next_page_number = page_num + 1
                    last_page_no = pages[-1]
                    if page_num == last_page_no:
                        more_btn_visible = False
                    notifications_list = notifications[offset:highest]
                    response['notifications_list'] = notifications_list
                    response['today'] = datetime.today().strftime('%Y-%m-%d')
                    response['request'] = request
                    all_list = render_to_string('profiles/notification_list.html', response)
                    response_data['new_lists'] = all_list
                    response_data['success'] = True
                    response_data['total_notifications'] = len(notifications_list)
                    response_data['next_page_number'] = next_page_number
                    response_data['more_btn_visible'] = more_btn_visible
                else:
                    response_data['success'] = False
            else:
                response_data['success'] = False
        except Exception as e:
            LogHelper.elog(e)
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def create_notfication(request, type, text, task_id, sending_by_id):
        try:
            notification_form = {
                "type": type,
                "text": text,
                "task_id": task_id,
                "sending_by_id": sending_by_id
            }
            notification = Notification(**notification_form)
            notification.save()
            NotificationsView.create_notification_user(request, notification)
        except Exception as e:
            LogHelper.efail(e)
        return


    # Notification will send to
    # Super Admin
    # Assigned user
    # All staffs of this project
    # All followers

    def create_notification_user(request, notification):
        try:
            # notification_users = []
            super_admin = Users.objects.filter(is_superuser=True).first()
            notification_user_form = {
                "user_id": super_admin.id,
                "notification_id": notification.id
            }
            # notification_users.append(NotificationStatus(**notification_user_form))
            notification_user = NotificationStatus(**notification_user_form)
            notification_user.save()

            assigned_user = BuildingComponents.objects.filter(component_id=notification.task.building_component.component.parent_id,
                                                               building_id=notification.task.building_component.building_id,
                                                               flat_id=notification.task.building_component.flat_id).first()
            if assigned_user.assign_to:
                notification_user_form = {
                    "user_id": assigned_user.assign_to.id,
                    "notification_id": notification.id
                }
                # notification_users.append(NotificationStatus(**notification_user_form))
                notification_user = NotificationStatus(**notification_user_form)
                notification_user.save()
            staffs = ProjectStuff.objects.filter(project_id=notification.task.building_component.building.project_id, user__is_active=True)
            for staff in staffs:
                notification_user_form = {
                    "user_id": staff.user_id,
                    "notification_id": notification.id
                }
                # notification_users.append(NotificationStatus(**notification_user_form))
                notification_user = NotificationStatus(**notification_user_form)
                notification_user.save()
            followers = notification.task.followers
            if followers:
                for follower in followers:
                    notification_user_form = {
                        "user_id": follower['id'],
                        "notification_id": notification.id
                    }
                    # notification_users.append(NotificationStatus(**notification_user_form))
                    notification_user = NotificationStatus(**notification_user_form)
                    notification_user.save()
            # NotificationStatus.objects.bulk_create(notification_users)
        except Exception as e:
            LogHelper.efail(e)
        return

    def get_new_notifications(request):
        response = {}
        try:
            notification_list = []
            notifications = NotificationStatus.objects.filter(user_id=request.user.id).order_by('-sending_at', 'status')[:5]
            for notification in notifications:
                notification_data = {
                    "avatar": notification.notification.sending_by.avatar.url if notification.notification.sending_by.avatar else '',
                    "message": notification.notification.text,
                    "status": notification.status,
                    "task_id": notification.notification.task_id,
                    "sending_time": str(notification.sending_at)
                }
                notification_list.append(notification_data)
            unread_notifications = NotificationStatus.objects.filter(user_id=request.user.id, status=False).count()
            new_notifications = False
            if NotificationStatus.objects.filter(user_id=request.user.id, is_sent=False).count() > 0:
                new_notifications = True
            NotificationStatus.objects.filter(user_id=request.user.id).update(is_sent=True)
            response['success'] = True
            response['notifications'] = notification_list
            response['unread_notifications'] = unread_notifications
            response['new_notifications'] = new_notifications
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def read_notification(request, task_id):
        try:
            NotificationStatus.objects.filter(user_id=request.user.id, notification__task_id=task_id).update(status=True)
        except Exception as e:
            LogHelper.efail(e)

    def read_all_notification(request):
        response = {}
        try:
            NotificationStatus.objects.filter(user_id=request.user.id).update(status=True)
            response['success'] = True
            response['message'] = "All notifications read successfully"
        except Exception as e:
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
            LogHelper.efail(e)
        return HttpResponse(json.dumps(response), content_type='application/json')
