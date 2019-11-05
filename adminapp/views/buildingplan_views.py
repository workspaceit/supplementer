from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import generic
from adminapp.forms.buildingplans_form import BuildingPlansForm
from adminapp.models import BuildingPlans
import json
from adminapp.views.helper import LogHelper


class BuildingPlansView(generic.DetailView):

    # url: building-plans/
    # This function will get all plans by a building
    def get_all_plans_by_active_building(request):
        response = {}
        try:
            building_id = request.session['active_building']['id']
            if 'building_id' in request.POST:
                building_id = request.POST.get('building_id')
            plans = BuildingPlans.objects.filter(building_id=building_id)
            plan_list_tab = render_to_string('buildings/plan.html', {"plans": plans, "building_id": building_id})
            response['plan_list_tab'] = plan_list_tab
            response['success'] = True
        except Exception as e:
            LogHelper.efail(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    # url: building-plan/delete/
    # This function will delete a building plan
    def delete(request):
        response = {}
        try:
            building_plan_id = request.POST.get('id')
            BuildingPlans.objects.get(id=building_plan_id).delete()
            response['success'] = True
            response['message'] = "Buildings Plan delete successfully"
        except Exception as e:
            LogHelper.elog(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')


class BuildingPlansAddView(generic.DetailView):
    form_class = BuildingPlansForm
    template_name = 'buildings/add_plans.html'

    # url: building/<building_id>/plan/add/
    # This function will show add building plan form
    def get(self, request, *args, **kwargs):
        building_id = kwargs['building_id']
        form = self.form_class
        return render(request, self.template_name, {'form': form, 'building_id': building_id})

    # url: building/<building_id>/plan/add/
    # This function will submit add building plan form
    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST, request.FILES)
        response['form'] = form
        building_id = kwargs['building_id']
        request.building_id = building_id
        response['building_id'] = building_id
        try:
            if form.is_valid():
                form.save(request=request)
                return HttpResponseRedirect('/buildings/'+str(building_id)+'/tasks/#plans')
            else:
                return render(request, self.template_name, response)
        except Exception as e:
            LogHelper.efail(e)
            return render(request, self.template_name, response)
