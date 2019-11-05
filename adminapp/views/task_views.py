from datetime import datetime
import json
import math
import os
import random
import string

from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from adminapp.models import Tasks, BuildingComponents, Buildings, Flats, HandWorker, Users, Comments
from adminapp.views.helper import LogHelper
from adminapp.views.common_views import CurrentProjects, CommonView, NotificationText
from adminapp.views.notification_views import NotificationsView


class TasksView(generic.DetailView):
    def get_all_building_tasks(request, *args, **kwargs):
        try:
            building_id = kwargs['building_id']
            building = Buildings.objects.get(id=building_id)
            if str(building.project_id) == str(request.session['active_project']['id']):
                CurrentProjects.change_active_building(request, building_id)
            return render(request, 'tasks/task_list.html', {'building': building})
        except Exception as e:
            LogHelper.efail(e)
            return redirect('index')

    def get_all_flat_tasks(request, *args, **kwargs):
        try:
            flat_id = kwargs['flat_id']
            flat = Flats.objects.get(id=flat_id)
            if str(flat.building_id) == str(request.session['active_building']['id']):
                CurrentProjects.change_active_flat(request, flat_id)
            return render(request, 'tasks/task_list.html', {'flat': flat})
        except Exception as e:
            LogHelper.efail(e)
            return redirect('index')

    def get_pending_components(request):
        response = {}
        try:
            if 'building_id' in request.POST:
                building_id = request.POST.get('building_id')
                components = BuildingComponents.objects.filter(building_id=building_id, flat__isnull=True,
                                                               component__parent__isnull=True)
                for component in components:
                    component.total_tasks = Tasks.objects.filter(building_component__building_id=building_id, building_component__flat__isnull=True).filter(Q(Q(building_component__component__parent_id=component.component_id) | Q(building_component__component_id=component.component_id))).exclude(status='done').count()
            elif 'flat_id' in request.POST:
                flat_id = request.POST.get('flat_id')
                components = BuildingComponents.objects.filter(flat_id=flat_id, component__parent__isnull=True)
                for component in components:
                    component.total_tasks = Tasks.objects.filter(building_component__flat_id=flat_id).filter(Q(Q(building_component__component__parent_id=component.component_id) | Q(building_component__component_id=component.component_id))).exclude(status='done').count()
            components_list = render_to_string('tasks/pending_components.html', {"components": components, "request": request})
            response['success'] = True
            response['components_list'] = components_list
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def get_done_components(request):
        response = {}
        try:
            if 'building_id' in request.POST:
                building_id = request.POST.get('building_id')
                components = BuildingComponents.objects.filter(building_id=building_id, flat__isnull=True,
                                                               component__parent__isnull=True)
                for component in components:
                    component.total_tasks = Tasks.objects.filter(building_component__building_id=building_id,
                                                 building_component__flat__isnull=True, status='done').filter(Q(
                        Q(building_component__component__parent_id=component.component_id) | Q(
                            building_component__component_id=component.component_id))).count()
            elif 'flat_id' in request.POST:
                flat_id = request.POST.get('flat_id')
                components = BuildingComponents.objects.filter(flat_id=flat_id, component__parent__isnull=True)
                for component in components:
                    component.total_tasks = Tasks.objects.filter(building_component__flat_id=flat_id, status='done').filter(Q(
                        Q(building_component__component__parent_id=component.component_id) | Q(
                            building_component__component_id=component.component_id))).count()
            components_list = render_to_string('tasks/done_components.html', {"components": components, "request": request})
            response['success'] = True
            response['components_list'] = components_list
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def get_all_components(request):
        response = {}
        try:
            if 'building_id' in request.POST:
                building_id = request.POST.get('building_id')
                components = BuildingComponents.objects.filter(building_id=building_id, flat__isnull=True,
                                                               component__parent__isnull=True)
            elif 'flat_id' in request.POST:
                flat_id = request.POST.get('flat_id')
                components = BuildingComponents.objects.filter(flat_id=flat_id, component__parent__isnull=True)
            components_list = render_to_string('tasks/all_components.html', {"components": components, "request": request})
            response['success'] = True
            response['components_list'] = components_list
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def get_component_tasks(request):
        response = {}
        try:
            type = request.POST.get('type')
            component_id = request.POST.get('id')
            if 'building_id' in request.POST:
                building_id = request.POST.get('building_id')
                if type == 'pending':
                    tasks = Tasks.objects.filter(building_component__building_id=building_id, building_component__flat__isnull=True).filter(Q(Q(building_component__component__parent_id=component_id) | Q(building_component__component_id=component_id))).exclude(status='done')
                elif type == 'done':
                    tasks = Tasks.objects.filter(building_component__building_id=building_id,
                                                 building_component__flat__isnull=True, status='done').filter(Q(
                        Q(building_component__component__parent_id=component_id) | Q(
                            building_component__component_id=component_id)))
                else:
                    tasks = Tasks.objects.filter(building_component__building_id=building_id,
                                                 building_component__flat__isnull=True).filter(Q(
                        Q(building_component__component__parent_id=component_id) | Q(
                            building_component__component_id=component_id)))
            elif 'flat_id' in request.POST:
                flat_id = request.POST.get('flat_id')
                if type == 'pending':
                    tasks = Tasks.objects.filter(building_component__flat_id=flat_id).filter(Q(Q(building_component__component__parent_id=component_id) | Q(building_component__component_id=component_id))).exclude(status='done')
                elif type == 'done':
                    tasks = Tasks.objects.filter(building_component__flat_id=flat_id, status='done').filter(Q(
                        Q(building_component__component__parent_id=component_id) | Q(
                            building_component__component_id=component_id)))
                else:
                    tasks = Tasks.objects.filter(building_component__flat_id=flat_id).filter(Q(
                        Q(building_component__component__parent_id=component_id) | Q(
                            building_component__component_id=component_id)))
            for task in tasks:
                try:
                    task.comment = Comments.objects.filter(task_id=task.id, text__isnull=False).last()
                except Exception as e:
                    task.comment = None
            tasks_list = render_to_string('tasks/task.html', {"tasks": tasks, "request": request})
            response['success'] = True
            response['tasks_list'] = tasks_list
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def get_active_tasks(request):
        response = {}
        try:
            if 'building_id' in request.POST:
                building_id = request.POST.get('building_id')
                components = BuildingComponents.objects.filter(building_id=building_id, flat__isnull=True, component__parent__isnull=True)
                for component in components:
                    component.tasks = Tasks.objects.filter(building_component__building_id=building_id, building_component__flat__isnull=True).filter(Q(Q(building_component__component__parent_id=component.component_id) | Q(building_component__component_id=component.component_id))).exclude(status='done')
            elif 'flat_id' in request.POST:
                flat_id = request.POST.get('flat_id')
                components = BuildingComponents.objects.filter(flat_id=flat_id, component__parent__isnull=True)
                for component in components:
                    component.tasks = Tasks.objects.filter(building_component__component__parent_id=component.component_id).exclude(status='done')
            active_tasks = render_to_string('tasks/task.html', {"components": components, "request": request})
            response['success'] = True
            response['active_tasks'] = active_tasks
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def get_handwerker_list(request):
        response = {}
        try:
            component_id = request.POST.get('component_id')
            handworker_list = []
            handworkers = HandWorker.objects.values('company_name', 'user_id').filter(user__is_active=True, working_type__contains={"id":component_id})
            for handworker in handworkers:
                data = {
                    "text": handworker['company_name'],
                    "id": handworker['user_id'],
                }
                handworker_list.append(data)
            response['success'] = True
            response['handworkers'] = handworker_list
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def assign_handwerker(request):
        response = {}
        try:
            component_id = request.POST.get('component_id')
            user_id = request.POST.get('user_id')
            BuildingComponents.objects.filter(id=component_id).update(assign_to_id=user_id, assigned_by=request.user)
            component = BuildingComponents.objects.get(id=component_id)
            # handworker = Users.objects.get(id=user_id)
            if component.flat:
                task = Tasks.objects.filter(building_component__component__parent_id=component.component_id).first()
            else:
                task = Tasks.objects.filter(building_component__building_id=component.building_id,
                                            building_component__flat__isnull=True).filter(Q(
                    Q(building_component__component__parent_id=component.component_id) | Q(
                        building_component__component_id=component.component_id))).first()
            task.save()
            handworker = HandWorker.objects.get(user_id=user_id)
            # Send Notification
            message = NotificationText.get_assign_worker_notification_text(request.user.get_full_name(), handworker.company_name,
                                                                           component.component.name)
            NotificationsView.create_notfication(request, 'assign_worker', message, task.id, request.user.id)
            handworker_info = {
                "fullname": handworker.company_name,
                "avatar": handworker.user.avatar.url if handworker.user.avatar else ''
            }
            response['success'] = True
            response['handworker'] = handworker_info
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')


class TaskDetailsView(generic.DetailView):
    def get(self, request, *args, **kwargs):
        try:
            response = {}
            task_id = kwargs['task_id']
            task = Tasks.objects.get(id=task_id)
            if task.building_component.component.parent:
                assign_to_user = BuildingComponents.objects.filter(component_id=task.building_component.component.parent_id, building_id=task.building_component.building_id, flat_id=task.building_component.flat_id).first()
            else:
                assign_to_user = task.building_component
            if assign_to_user.assign_to:
                assign_to = {
                    "fullname": assign_to_user.assign_to.handworker.company_name,
                    "avatar": assign_to_user.assign_to.avatar.url if assign_to_user.assign_to.avatar else ''
                }
            else:
                assign_to = None
            response['task'] = task
            response['assign_to'] = assign_to
            comments = Comments.objects.filter(task_id=task_id).order_by('-created_at')
            response['more_comments'] = False
            if comments.count() > 5:
                response['more_comments'] = True
            comments_list = comments[:5]
            response['comments_list'] = comments_list
            response['today'] = datetime.today().strftime('%Y-%m-%d')
            followers_response = TaskDetailsView.get_task_followers(request, task, assign_to_user.assign_to)
            response.update(followers_response)
            NotificationsView.read_notification(request,task_id)
            return render(request, 'tasks/task_details.html', response)
        except Exception as e:
            LogHelper.efail(e)
            return redirect('index')

    def get_task_followers(request, task, assign_to):
        response = {}
        followers = []
        if assign_to:
            handworkers = HandWorker.objects.all().exclude(user_id=assign_to.id)
        else:
            handworkers = HandWorker.objects.all()
        for handworker in handworkers:
            data = {
                "text": handworker.company_name,
                "id": handworker.user_id,
            }
            followers.append(data)
        task_followers = []
        if task.followers:
            for follower in task.followers:
                value = follower['id']
                task_followers.append(value)
        response['task_followers'] = task_followers
        response['followers'] = followers
        return response

    def add_task_followers(request):
        response = {}
        try:
            task_id = request.POST.get('task_id')
            followers = json.loads(request.POST.get('followers'))
            Tasks.objects.filter(id=task_id).update(followers=followers)
            response['success'] = True
            response['message'] = "Followers added successfully"
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')


    def get_more_comments(request):
        response_data = {}
        try:
            response = {}
            page_num = int(request.POST.get('page_number'))
            task_id = request.POST.get('task_id')
            comments = Comments.objects.filter(task_id=task_id).order_by('-created_at')
            total = len(comments)
            limit = 5
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
                    comments_list = comments[offset:highest]
                    response['comments_list'] = comments_list
                    response['today'] = datetime.today().strftime('%Y-%m-%d')
                    response['request'] = request
                    all_list = render_to_string('tasks/comments.html', response)
                    response_data['new_lists'] = all_list
                    response_data['success'] = True
                    response_data['total_comments'] = len(comments_list)
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

    def save_task_description(request):
        response = {}
        try:
            task_id = request.POST.get('task_id')
            description = request.POST.get('description')
            task = Tasks.objects.get(id=task_id)
            task.building_component.description = description
            task.building_component.save()
            task.save()
            # Send Notification
            message = NotificationText.get_edit_task_notification_text(request.user.get_full_name(), task.building_component.component.name)
            NotificationsView.create_notfication(request, 'edit_task', message, task_id, request.user.id)
            response['success'] = True
            response['message'] = "Description Update successfully"
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def change_task_status(request):
        response = {}
        try:
            task_id = request.POST.get('task_id')
            status = request.POST.get('status')
            task = Tasks.objects.get(id=task_id)
            task.status = status
            task.save()
            # Send Notification
            message = NotificationText.get_change_task_status_notification_text(request.user.get_full_name(),
                                                                       task.building_component.component.name, task.status)
            NotificationsView.create_notfication(request, 'change_task_status', message, task_id, request.user.id)
            response['success'] = True
            response['message'] = "Status Update successfully"
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def change_task_deadline(request):
        response = {}
        try:
            task_id = request.POST.get('task_id')
            due_date = request.POST.get('due_date')
            task = Tasks.objects.get(id=task_id)
            if str(task.due_date) != str(due_date):
                task.due_date = due_date
                task.save()
                # Send Notification
                message = NotificationText.get_change_due_date_notification_text(request.user.get_full_name(),
                                                                                    task.building_component.component.name, due_date)
                NotificationsView.create_notfication(request, 'change_due_date', message, task_id, request.user.id)
                response['message'] = "Deadline Update successfully"
            response['success'] = True
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def add_new_comment(request, *args, **kwargs):
        task_id = kwargs['task_id']
        try:
            comment = request.POST.get('task_comment_text')
            files = request.FILES.getlist('task_comment_files')
            file_list = []
            dir = os.path.join(settings.MEDIA_ROOT, "comments")
            if not os.path.exists(dir):
                os.makedirs(dir)
            for file in files:
                uploaded_file = CommonView.handle_uploaded_file(request, file)
                if uploaded_file != "":
                    file_list.append(uploaded_file)
            if comment != '' or len(file_list) > 0:
                comment_form = {
                    "text": comment,
                    "file_type": file_list if(len(file_list) > 0) else None,
                    "task_id": task_id,
                    "user": request.user,
                    "type": "text"
                }
                new_comment = Comments(**comment_form)
                new_comment.save()
                task = Tasks.objects.get(id=task_id)
                task.save()
                if comment != '':
                    # Send Notification
                    message = NotificationText.get_task_comment_notification_text(request.user.get_full_name(),
                                                                                     task.building_component.component.name)
                    NotificationsView.create_notfication(request, 'task_comment', message, task_id, request.user.id)
                if len(file_list) > 0:
                    # Send Notification
                    message = NotificationText.get_attach_file_notification_text(request.user.get_full_name(),
                                                                                  task.building_component.component.name)
                    NotificationsView.create_notfication(request, 'attach_file', message, task_id, request.user.id)
        except Exception as e:
            LogHelper.efail(e)
        return HttpResponseRedirect('/tasks/'+str(task_id)+'/')







