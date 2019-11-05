import json
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View, UpdateView
from adminapp.models import Users, HandWorker
from adminapp.forms.user_form import WorkerForm, WorkerUpdateForm, UserPasswordChangeForm
from adminapp.views.common_views import CommonView
from adminapp.views.helper import LogHelper


class CompaniesView(generic.DetailView):
    # url: companies/
    # This function will return all the Company list
    def get(self, request):
        context = CommonView.common_datatable_context(self)
        return render(request, 'companies/worker.html', context)

    # url: companies/delete/
    # This function will delete a company
    def delete(request):
        response = {}
        try:
            userId = request.POST.get('id')
            Users.objects.get(id=userId).delete()
            response['success'] = True
            response['message'] = "Worker delete successfully"
        except Exception as e:
            LogHelper.elog(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    # This function is call from company create function
    # This will create additional handworker row
    def create_worker(request, data):
        try:
            form_data = {
                'company_name': data['company_name'],
                'telephone_office': data['telephone_office'],
                'telephone_mobile': data['telephone_mobile'],
                'user_id': data['user_id'],
                'working_type': data['working_type'],
            }
            HandWorker.objects.create(**form_data)
        except Exception as e:
            LogHelper.efail(e)

    # This function is call from company update function
    # This will update additional handworker row
    def update_worker(request, data, user_id):
        try:
            form_data = {
                'company_name': data['company_name'],
                'telephone_office': data['telephone_office'],
                'telephone_mobile': data['telephone_mobile'],
                'working_type': data['working_type'],
            }
            HandWorker.objects.filter(user_id=user_id).update(**form_data)
        except Exception as e:
            LogHelper.efail(e)


class CompanyFormView(View):
    form_class = WorkerForm
    template_name = 'companies/add_worker.html'

    # url: companies/add/
    # This function will show the add company form
    def get(self, request, *args, **kwargs):
        form = self.form_class
        components = CommonView.get_all_main_component(request)
        return render(request, self.template_name, {'form': form, 'components': components})

    # url: companies/add/
    # This function will submit the add company form
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        working_types = []
        working_components = request.POST.getlist('working_type')
        for component in working_components:
            component_id = component.split("-")[0]
            component_name = component.split("-")[1]
            working_types.append({'id': component_id, 'component': component_name})
        if form.is_valid():
            obj = form.save(self, request)
            data = {
                "company_name": request.POST.get('company_name'),
                "telephone_office": request.POST.get('telephone_office'),
                "telephone_mobile": request.POST.get('telephone_mobile'),
                "working_type": working_types,
                "user_id": obj.id,
            }
            CompaniesView.create_worker(request, data)
            mailTemplate = "mails/user_registered.html"
            context = {
                "user_full_name": obj.get_full_name(),
                "password": self.request.POST.get('password'),
                "username": self.request.POST.get('username')
            }
            subject = "Worker Register"
            to = obj.email
            CommonView.sendEmail(self.request, mailTemplate, context, subject, to, obj.id)
            return HttpResponseRedirect('/companies/')
        components = CommonView.get_all_main_component(request)
        return render(request, self.template_name, {'form': form, 'components': components, 'working_types': working_components})


# url: companies/update/
# This function will show and update the company form
class CompanyUpdateView(UpdateView):

    model = Users
    template_name = 'companies/edit_worker.html'
    form_class = WorkerUpdateForm

    def form_valid(self, form):
        form.update(request=self.request)
        working_types = []
        working_components = self.request.POST.getlist('working_type')
        for component in working_components:
            component_id = component.split("-")[0]
            component_name = component.split("-")[1]
            working_types.append({'id': component_id, 'component': component_name})
        data = {
            "company_name": self.request.POST.get('company_name'),
            "telephone_office": self.request.POST.get('telephone_office'),
            "telephone_mobile": self.request.POST.get('telephone_mobile'),
            "working_type": working_types,
        }
        CompaniesView.update_worker(self.request, data, self.object.id)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('companies')

    # This function return the custom data to comapany update form view
    def get_context_data(self, **kwargs):
        context = super(CompanyUpdateView, self).get_context_data(**kwargs)
        context['components'] = CommonView.get_all_main_component(self.request)
        context['avatar'] = self.object.avatar.url if self.object.avatar else ''
        context['company_name'] = self.object.handworker.company_name
        context['telephone_office'] = self.object.handworker.telephone_office
        context['telephone_mobile'] = self.object.handworker.telephone_mobile
        working_components = self.object.handworker.working_type
        working_types = []
        if working_components:
            for component in working_components:
                value = component['id']+"-"+component['component']
                working_types.append(value)
        context['working_type'] = working_types
        return context


# url: companies/change-password/
# Admin can change comapny's password in this function.
# This function show the form and save the submitted password
class CompanyPasswordChangeView(UpdateView):
    model = Users
    form_class = UserPasswordChangeForm
    template_name = 'staffs/staff_password_change.html'

    def get_success_url(self):
        return reverse_lazy('companies')

    def form_valid(self, form):
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




