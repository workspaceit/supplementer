from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import UpdateView
from django.db.models import Q
from adminapp.forms.component_form import ComponentForm
from adminapp.models import Components
import json

from adminapp.views.common_views import CommonView
from adminapp.views.helper import LogHelper


class ComponentView(generic.DetailView):
    def get(self, request):
        response = {}
        if request.user.is_superuser:
            components = Components.objects.filter(parent__isnull=True)
            for component in components:
                component.sub_components = Components.objects.filter(parent_id=component.id)
            response['components'] = components
            return render(request, 'components/component.html', response)
        else:
            return redirect('index')

    def delete(request):
        response = {}
        if CommonView.superuser_login(request):
            try:
                component_id = request.POST.get('id')
                component = Components.objects.get(id=component_id)
                if component.parent is None:
                    response['success'] = False
                    response['message'] = "Something went wrong. Please try again"
                    return HttpResponse(json.dumps(response), content_type='application/json')

                Components.objects.get(id=component_id).delete()
                response['success'] = True
                response['message'] = "Component delete successfully"
                return HttpResponse(json.dumps(response), content_type='application/json')
            except Exception as e:
                LogHelper.elog(e)
                response['success'] = False
                response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')


class ComponentAddView(generic.DetailView):
    form_class = ComponentForm
    template_name = 'components/add_component.html'

    def get(self, request):
        if request.user.is_superuser:
            response = {}
            form = self.form_class
            parents = Components.objects.filter(Q(parent__isnull=True) | Q(parent_id=0))
            response['parents'] = parents
            response['form'] = form
            return render(request, self.template_name, response)
        else:
            return redirect('index')

    def post(self, request, *args, **kwargs):
        if CommonView.superuser_login(request):
            response = {}
            form = self.form_class(request.POST)
            form.created_by = request.user
            parents = Components.objects.filter(Q(parent__isnull=True) | Q(parent_id=0))
            response['parents'] = parents
            response['form'] = form
            try:
                if form.is_valid():
                    form.save(request=request)
                    return HttpResponseRedirect('/components/')
            except Exception as e:
                LogHelper.efail(e)
                return render(request, self.template_name, response)
        else:
            return redirect('index')


class ComponentUpdateView(UpdateView):
    form_class = ComponentForm
    template_name = 'components/edit_component.html'
    model = Components

    def form_valid(self, form):
        if CommonView.superuser_login(self.request):
            form.update(request=self.request)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return redirect('index')

    def get_success_url(self):
        return reverse_lazy('components')

    def get_context_data(self, **kwargs):
        context = super(ComponentUpdateView, self).get_context_data(**kwargs)
        parents = Components.objects.filter(Q(parent__isnull=True) | Q(parent_id=0))
        context['parents'] = parents
        context['parent_id'] = self.object.parent_id
        return context
