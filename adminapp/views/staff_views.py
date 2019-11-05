import json

from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, UpdateView
from adminapp.models import Users, ProjectStuff
from adminapp.forms.user_form import UserForm, UserUpdateForm, UserPasswordChangeForm
from adminapp.views.common_views import CommonView
from adminapp.views.helper import LogHelper
from adminapp.views.project_views import ProjectsView


class StaffsView(generic.DetailView):
    def get(self, request):
        if request.user.is_superuser:
            context = CommonView.common_datatable_context(self)
            return render(request, 'staffs/staff.html', context)
        else:
            return redirect('index')

    def delete(request):
        response = {}
        if CommonView.superuser_login(request):
            try:
                userId = request.POST.get('id')
                # Users.objects.filter(id=userId).update(is_active='0')
                Users.objects.get(id=userId).delete()
                response['success'] = True
                response['message'] = "User delete successfully"
            except Exception as e:
                LogHelper.elog(e)
                response['success'] = False
                response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    def change_user_status(request):
        response = {}
        if CommonView.superuser_login(request):
            try:
                userId = request.POST.get('id')
                status = request.POST.get('status')
                Users.objects.filter(id=userId).update(is_active=status)
                response['success'] = True
                response['message'] = "Status Changed Successfully"
            except Exception as e:
                LogHelper.elog(e)
                response['success'] = False
                response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')


class StaffFormView(View):
    form_class = UserForm
    template_name = 'staffs/add_staff.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            form = self.form_class
            projects = CommonView.get_all_projects(request)
            return render(request, self.template_name, {'form': form, 'projects': projects})
        else:
            return redirect('index')

    def post(self, request, *args, **kwargs):
        if CommonView.superuser_login(request):
            form = self.form_class(request.POST, request.FILES)
            project_list = request.POST.getlist('project_list')
            if form.is_valid():
                obj = form.save(self, request)
                ProjectsView.assign_staff(request, project_list, obj.id)
                mailTemplate = "mails/user_registered.html"
                context = {
                    "user_full_name": obj.get_full_name(),
                    "password": self.request.POST.get('password'),
                    "username": self.request.POST.get('username')
                }
                subject = "Staff Register"
                to = obj.email
                CommonView.sendEmail(self.request, mailTemplate, context, subject, to, obj.id)
                return HttpResponseRedirect('/staffs/')
            projects = CommonView.get_all_projects(request)
            return render(request, self.template_name, {'form': form, 'projects': projects, 'project_list': project_list})
        else:
            return redirect('index')


class StaffUpdateView(UpdateView):

    model = Users
    template_name = 'staffs/edit_staff.html'
    form_class = UserUpdateForm

    def form_valid(self, form):
        if CommonView.superuser_login(self.request):
            form.update(request=self.request)
            projects = self.request.POST.getlist('project_list')
            ProjectsView.assign_staff(self.request, projects, self.object.id)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return redirect('index')

    def get_success_url(self):
        return reverse_lazy('staffs')

    def get_context_data(self, **kwargs):
        context = super(StaffUpdateView, self).get_context_data(**kwargs)
        context['projects'] = CommonView.get_all_projects(self.request)
        context['avatar'] = self.object.avatar.url if self.object.avatar else ''
        context['project_list'] = list(ProjectStuff.objects.filter(user_id=self.object.id).values_list('project_id', flat=True))
        return context


class StaffPasswordChangeView(UpdateView):
    model = Users
    form_class = UserPasswordChangeForm
    template_name = 'staffs/staff_password_change.html'

    def get_success_url(self):
        return reverse_lazy('staffs')

    def form_valid(self, form):
        if CommonView.superuser_login(self.request):
            form.save(request=self.request)
            mailTemplate = "mails/user_password_change.html"
            context = {
                "user_full_name": self.object.get_full_name(),
                "password": self.request.POST.get('password')
            }
            subject = "Password Change"
            to = self.object.email
            CommonView.sendEmail(self.request, mailTemplate, context, subject, to, self.object.id)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return redirect('index')

