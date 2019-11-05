import json

from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, UpdateView
from adminapp.models import Buildings, BuildingComponents, Flats, QrCode
from adminapp.views.common_views import CommonView
from adminapp.views.helper import LogHelper
from adminapp.forms.flat_form import FlatForm


class FlatsView(generic.DetailView):
    def get(self, request, *args, **kwargs):
        try:
            building_id = kwargs['building_id']
            context = CommonView.common_datatable_context(self)
            context['building_id'] = building_id
            building = Buildings.objects.get(id=building_id)
            context['building'] = building
            return render(request, 'flats/flat.html', context)
        except Exception as e:
            LogHelper.efail(e)
            return redirect('index')

    def preview_qr(request, pk):
        try:
            context = {}
            qr_info = QrCode.objects.filter(flat_id=pk).select_related('flat').first()
            context['qr_info'] = qr_info
            return render(request, 'flats/preview_qr.html', context)
        except Exception as e:
            LogHelper.efail(e)
            return redirect('index')

    def delete(request):
        response = {}
        try:
            flat_id = request.POST.get('id')
            Flats.objects.get(id=flat_id).delete()
            response['success'] = True
            response['message'] = "Wohnung deleted successfully"
        except Exception as e:
            LogHelper.elog(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')


class FlatFormView(View):
    form_class = FlatForm
    template_name = 'flats/add_flat.html'

    def get(self, request, *args, **kwargs):
        building_id = kwargs['building_id']
        form = self.form_class
        return render(request, self.template_name, {'form': form, 'building_id': building_id})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        building_id = kwargs['building_id']
        try:
            if form.is_valid():
                request.building_id = building_id
                obj = form.save(request=request)
                default_components = CommonView.create_default_flat_components(request, obj)
                qr = CommonView.generate_qr_code(request, obj.building, obj)
                if default_components:
                    building_components = BuildingComponents.objects.filter(flat_id=obj.id)
                    default_tasks = CommonView.create_default_tasks(request, building_components)
                return HttpResponseRedirect('/buildings/'+str(obj.building_id)+'/flats/')
        except Exception as e:
            LogHelper.efail(e)
        return render(request, self.template_name, {'form': form, 'building_id': building_id})


class FlatUpdateView(UpdateView):
    model = Flats
    template_name = 'flats/edit_flat.html'
    form_class = FlatForm

    def form_valid(self, form):
        form.update(request=self.request)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('flats', kwargs={'building_id': self.object.building_id})

    def get_context_data(self, **kwargs):
        context = super(FlatUpdateView, self).get_context_data(**kwargs)
        return context




