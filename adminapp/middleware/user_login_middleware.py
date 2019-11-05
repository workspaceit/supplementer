import json

import requests
from django.db.models import Case, When
from django.views import generic
from adminapp.models import Users, Projects, Buildings, Flats
from adminapp.views.common_views import CommonView
import os.path
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import resolve


class UserLoginMiddleware(generic.DetailView):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.split('/')[1]
        if path != 'api' and path != 'media' and path != 'login' and path != 'forget-password' and path != 'reset-password' and path != 'privacy_policy':
            if request.is_ajax() == False:
                # settings.USE_TZ = False
                browser_current_url = resolve(request.path_info).url_name
                # if browser_current_url != 'login' and browser_current_url != 'forget-password' and browser_current_url != 'reset-password':
                if not request.user.is_authenticated:
                    return redirect('login')
                if request.user.is_superuser:
                    current_projects = list(Projects.objects.filter(is_complete=False).order_by('-id').values('id', 'name'))
                else:
                    current_projects = list(Projects.objects.filter(is_complete=False, projectstuff__user_id=request.user.id).order_by('-id').values('id', 'name').distinct())
                request.session["current_projects"] = current_projects
                if request.user.current_activity:
                    current_activity = json.loads(request.user.current_activity)
                    if 'project_id' in current_activity:
                        request.session["active_project"] = {
                            'id': current_activity['project_id'],
                            'name': current_activity['project_name']
                        }
                    if 'building_id' in current_activity:
                        request.session["active_building"] = {
                            'id': current_activity['building_id'],
                            'number': current_activity['building_number']
                        }
                    if 'flat_id' in current_activity:
                        request.session["active_flat"] = {
                            'id': current_activity['flat_id'],
                            'number': current_activity['flat_number']
                        }
                if 'active_project' not in request.session:
                    request.session["active_project"] = {
                        'id': '',
                        'name': ''
                    }
                if 'active_building' not in request.session:
                    request.session["active_building"] = {
                        'id': '',
                        'number': ''
                    }
                if 'active_flat' not in request.session:
                    request.session["active_flat"] = {
                        'id': '',
                        'number': ''
                    }
                request.session.modified = True
        # elif path != 'api':
        #     if request.is_ajax() == False:
        #         if 'user_bikeshare_settings' not in request.session:
        #             response = requests.get(settings.API_URL+"/settings/")
        #             default_settings = json.loads(response._content)
        #             request.session["user_bikeshare_settings"] = default_settings
        #             request.session.modified = True
        #         if 'is_user_login' in request.session and request.session['is_user_login']:
        #             print("logged in")
        #         else:
        #             return redirect('user-login')
        return self.get_response(request)

    def process_response(self, request, response):
        path = request.path.split('/')[1]
        response['Pragma'] = 'no-cache'
        if path == 'admin' or path == '':
            response['Cache-Control'] = 'no-cache must-revalidate proxy-revalidate'
        else:
            response['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
        return response

