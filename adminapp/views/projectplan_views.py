from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import generic

from adminapp.forms.projectplan_form import ProjectPlansForm
from adminapp.models import ProjectPlans

import json
from adminapp.views.helper import LogHelper


class ProjectPlansView(generic.DetailView):

    def get_all_plans_by_active_project(request):
        response = {}
        try:
            project_id = request.session['active_project']['id']
            if 'project_id' in request.POST:
                project_id = request.POST.get('project_id')
            plans = ProjectPlans.objects.filter(project_id=project_id)
            plan_list_tab = render_to_string('projects/plan.html', {"plans": plans, "project_id": project_id})
            response['plan_list_tab'] = plan_list_tab
            response['success'] = True
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def delete(request):
        response = {}
        try:
            flat_plan_id = request.POST.get('id')
            ProjectPlans.objects.get(id=flat_plan_id).delete()
            response['success'] = True
            response['message'] = "Project delete successfully"
        except Exception as e:
            LogHelper.elog(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')


class ProjectPlansAddView(generic.DetailView):
    form_class = ProjectPlansForm
    template_name = 'projects/add_plans.html'

    def get(self, request, *args, **kwargs):
        project_id = kwargs['project_id']
        form = self.form_class
        return render(request, self.template_name, {'form': form, 'project_id': project_id})

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST, request.FILES)
        response['form'] = form
        project_id = kwargs['project_id']
        request.project_id = project_id
        response['project_id'] = project_id
        try:
            if form.is_valid():
                form.save(request=request)
                return HttpResponseRedirect('/current-project-buildings/#plans')
            else:
                return render(request, self.template_name, response)
        except Exception as e:
            LogHelper.efail(e)
            return render(request, self.template_name, response)
