import json
from django.views import generic

from adminapp.models import Projects, Buildings, Flats
from adminapp.views.helper import LogHelper


class ActivityView(generic.DetailView):
    def change_active_project(request, project_id):
        try:
            project = Projects.objects.get(id=project_id)
            current_activity = {
                'project_id': project.id,
                'project_name': project.name
            }
            request.user.current_activity = json.dumps(current_activity)
            request.user.save()
        except Exception as e:
            LogHelper.efail(e)
        return True

    def change_active_building(request, building_id):
        try:
            building = Buildings.objects.get(id=building_id)
            current_activity = {
                'project_id': building.project.id,
                'project_name': building.project.name,
                'building_id': building.id,
                'building_number': building.display_number
            }
            request.user.current_activity = json.dumps(current_activity)
            request.user.save()
        except Exception as e:
            LogHelper.efail(e)
        return True

    def change_active_flat(request, flat_id):
        try:
            flat = Flats.objects.get(id=flat_id)
            current_activity = {
                'project_id': flat.building.project.id,
                'project_name': flat.building.project.name,
                'building_id': flat.building.id,
                'building_number': flat.building.display_number,
                'flat_id': flat.id,
                'flat_number': flat.number
            }
            request.user.current_activity = json.dumps(current_activity)
            request.user.save()
        except Exception as e:
            LogHelper.efail(e)
        return True
