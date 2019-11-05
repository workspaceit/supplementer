import json

from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, UpdateView
from adminapp.models import Projects, ProjectStuff
from adminapp.forms.project_form import ProjectForm
from adminapp.views.common_views import CommonView
from adminapp.views.helper import LogHelper


class ProjectsView(generic.DetailView):
    def get(self, request):
        context = CommonView.common_datatable_context(self)
        context['sorted_column'] = 0
        context['sorting_order'] = 'desc'
        return render(request, 'projects/project.html', context)

    def delete(request):
        response = {}
        if CommonView.superuser_login(request):
            try:
                project_id = request.POST.get('id')
                Projects.objects.get(id=project_id).delete()
                response['success'] = True
                response['message'] = "Project deleted successfully"
            except Exception as e:
                LogHelper.elog(e)
                response['success'] = False
                response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def assign_staff(request, projects, user_id):
        try:
            project_exists = []
            project_staff_list = []
            for project in projects:
                project_exists.append(project)
                if not (ProjectStuff.objects.filter(user_id=user_id, project_id=project).exists()):
                    project_staff = ProjectStuff(project_id=project, user_id=user_id, created_by=request.user)
                    project_staff_list.append(project_staff)
            ProjectStuff.objects.bulk_create(project_staff_list)
            ProjectStuff.objects.filter(user_id=user_id).exclude(project_id__in=project_exists).delete()
            return True
        except Exception as e:
            LogHelper.efail(e)
            return True

    def change_project_status(request):
        response = {}
        try:
            project_id = request.POST.get('id')
            status = request.POST.get('status')
            Projects.objects.filter(id=project_id).update(is_complete=status)
            response['success'] = True
            response['message'] = "Status Changed Successfully"
        except Exception as e:
            LogHelper.elog(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')


class ProjectFormView(View):
    form_class = ProjectForm
    template_name = 'projects/add_project.html'

    def get(self, request, *args, **kwargs):
        if CommonView.superuser_login(request):
            form = self.form_class
            return render(request, self.template_name, {'form': form})
        else:
            return redirect('index')

    def post(self, request, *args, **kwargs):
        if CommonView.superuser_login(request):
            form = self.form_class(request.POST)
            try:
                if form.is_valid():
                    form.save(request=request)
                    return HttpResponseRedirect('/projects/')
            except Exception as e:
                LogHelper.efail(e)
            return render(request, self.template_name, {'form': form})
        else:
            return redirect('index')


class ProjectUpdateView(UpdateView):
    model = Projects
    template_name = 'projects/edit_project.html'
    form_class = ProjectForm

    def form_valid(self, form):
        if CommonView.superuser_login(self.request):
            form.update(request=self.request)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return redirect('index')

    def get_success_url(self):
        return reverse_lazy('projects')

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data(**kwargs)
        return context




