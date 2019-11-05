import json
import os
import random, string

from django.shortcuts import render, redirect
from django.views import generic
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from adminapp.views.mail import MailHelper
from adminapp.views.helper import LogHelper
from adminapp.models import Components, Projects, BuildingComponents, Tasks, QrCode, Buildings, Flats, NotificationStatus
from django.db.models import Q, Count
from datetime import datetime
import qrcode
import io
from PIL import Image
from resizeimage import resizeimage


class IndexView(generic.DetailView):
    # url: /
    # This function will show the dashboard page
    def get(self, request):
        response = {}
        try:
            response["user_id"] = request.user.id 
            notifications = NotificationStatus.objects.filter(user_id=request.user.id).order_by('-sending_at')
            notification_list = notifications[:10]
            response["notification_list"] = notification_list
            response['today'] = datetime.today().strftime('%Y-%m-%d')
            return render(request, 'dashboard/index.html', response)
        except Exception as e:
            print(e)


class CommonView(generic.DetailView):

    # All the email send through this function
    def sendEmail(request, template, context, subject, to, user_id=None):
        response = {}
        try:
            context["request"] = request
            # context["base_url"] = settings.SITE_URL
            context["base_url"] = "http://"+request.get_host()
            context["project_title"] = settings.PROJECT_TITLE
            mail_template_content = render_to_string(template, context)
            sender_mail = settings.EMAIL_HOST_USER
            # if user_id:
            #     CommonHelper.set_history(user_id=user_id, subject=subject, type="email")
            import threading
            task = threading.Thread(target=MailHelper.mail_send, args=(mail_template_content, subject, to, sender_mail))
            task.start()
            response['success'] = True
        except Exception as e:
            LogHelper.elog(e)
            response['success'] = False
        return HttpResponse(json.dumps(response), content_type='application/json')

    # All the common settings of datatable comes from this function
    def common_datatable_context(self):
        show_entries = 10
        sorted_column = 0
        sorting_order = 'asc'
        context = {
            'show_entries': show_entries,
            'sorting_order': sorting_order,
            'sorted_column': sorted_column
        }
        return context

    def get_file_path(file):
        file = str(file)
        file_path = ""
        try:
            # path = file.split("adminapp/")[1]
            file_path = settings.MEDIA_URL+file
        except Exception as e:
            LogHelper.elog(e)
        return file_path

    # This function return all the parent components
    # We need this in company form view
    def get_all_main_component(request):
        components = Components.objects.filter(parent__isnull=True)
        return components

    # Here we checking is the user is superAdmin
    def superuser_login(request):
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        else:
            return False

    # This function return all the Projects
    def get_all_projects(request):
        projects = Projects.objects.all()
        return projects

    # This function is called when a new building is added and this function created all it's default components
    def create_default_building_components(request, building):
        try:
            default_components = Components.objects.filter(Q(type__isnull=True) | Q(type='') | Q(type=building.grundung) | Q(type=building.aussenwande_eg_og_dg) | Q(type=building.fenster_beschattung) | Q(type=building.dach)).filter(building=True)
            building_components = []
            for component in default_components:
                component_form = {
                    "description": component.static_description,
                    "building": building,
                    "created_by": request.user,
                    "updated_by": request.user,
                    "component": component
                }
                building_components.append(BuildingComponents(**component_form))
            BuildingComponents.objects.bulk_create(building_components)
            return True
        except Exception as e:
            LogHelper.efail(e)
            return False

    # This function is called when a new flat is added and this function created all it's default components
    def create_default_flat_components(request, flat):
        try:
            default_components = Components.objects.filter(flat=True)
            flat_components = []
            for component in default_components:
                component_form = {
                    "description": component.static_description,
                    "flat": flat,
                    "building": flat.building,
                    "created_by": request.user,
                    "updated_by": request.user,
                    "component": component
                }
                flat_components.append(BuildingComponents(**component_form))
            BuildingComponents.objects.bulk_create(flat_components)
            return True
        except Exception as e:
            LogHelper.efail(e)
            return False

    # This function is called when a new building or flat is added and this function created all it's default components tasks
    def create_default_tasks(request, components):
        try:
            task_list = []
            for component in components:
                task_flag = False
                if component.component.parent:
                    task_flag = True
                elif not Components.objects.filter(parent_id=component.component.id).exists():
                    task_flag = True
                if task_flag:
                    task_form = {
                        "building_component": component,
                        "followers": None,
                        "created_by": request.user,
                        "updated_by": request.user
                    }
                    task_list.append(Tasks(**task_form))
            Tasks.objects.bulk_create(task_list)
            return True
        except Exception as e:
            LogHelper.efail(e)
            return False

    # In this function we save the QR code for building and flats
    def generate_qr_code(request, building, flat=None):
        unique_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        qr_form = {
            "unique_key": unique_key,
            "building": building,
            "flat": flat,
            "created_by": request.user,
        }
        qr_code = QrCode(**qr_form)
        qr_code.save()
        return qr_code

    # Imaginary function to handle an uploaded file.
    def handle_uploaded_file(request, f):
        random_number = CommonView.randomString(10)
        file = str(f.name).rsplit('.', 1)
        filename = file[0] + "_" + random_number + "." + file[1]
        thumb_filename = file[0] + "_" + random_number + "_thumb." + file[1]
        full_filename = os.path.join(settings.MEDIA_ROOT, "comments", filename)
        thumb_full_filename = os.path.join(settings.MEDIA_ROOT, "comments", thumb_filename)
        fout = open(full_filename, 'wb+')
        # host_url = "http://"+request.get_host()
        host_url = ""
        try:
            for chunk in f.chunks():
                fout.write(chunk)
            fout.close()
            with open(full_filename, 'r+b') as f:
                with Image.open(f) as image:
                    cover = resizeimage.resize_cover(image, [150, 150])
                    cover.save(thumb_full_filename, image.format)
                    if os.stat(full_filename).st_size > 1200000:
                        resized_image = resizeimage.resize_cover(image, [1700, 1500])
                        resized_image.save(full_filename, image.format)
            file_info = {
                "path": host_url + "/media/comments/" + filename,
                "thumb_path": host_url + "/media/comments/" + thumb_filename,
                "ext": file[1]
            }
            return file_info
        except Exception as e:
            LogHelper.efail(e)
            return ""

    # This function is used for create a random string which we need in upload files name
    def randomString(stringLength=10):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))


# In this class we generate the QR code for building and flats
class QRResponse(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            qr_id = kwargs['qr_id']
            qr_info = QrCode.objects.get(id=qr_id)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=2
            )
            qr.add_data(qr_info.unique_key)
            qr.make(fit=True)
            img = qr.make_image()
            output = io.BytesIO()
            img.save(output, format='PNG')
            output.seek(0)
            output_s = output.read()
            return HttpResponse(output_s, content_type="image/png")
        except Exception as e:
            LogHelper.efail(e)
            return HttpResponse("", content_type="image/png")


class CurrentProjects(generic.DetailView):
    # url: current-buildings/
    # Here we get all the buildings for selected project and will show in the sidebar
    # Also update user last active project
    def get_all_current_buildings(request):
        response = {}
        try:
            project_id = request.POST.get('project_id')
            change_project = request.POST.get('change_project')
            buildings = Buildings.objects.annotate(total_flats=Count('flats')).filter(project_id=project_id)
            if change_project == 'true':
                CurrentProjects.change_active_project(request, project_id)
                building_list_tab = render_to_string('profiles/buildings.html', {"buildings": buildings, "request": request})
                response['building_list_tab'] = building_list_tab
            current_buildings = []
            for building in buildings:
                current_buildings.append({'id': building.id, 'number': building.display_number})
            response['success'] = True
            response['current_buildings'] = current_buildings
        except Exception as e:
            LogHelper.elog(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    # url: current-flats/
    # Here we get all the flats for selected building and will show in the sidebar
    # Also update user last active project and building
    def get_all_current_flats(request):
        response = {}
        try:
            building_id = request.session["active_building"]['id']
            flats = Flats.objects.filter(building_id=building_id)
            current_flats = []
            for flat in flats:
                current_flats.append({'id': flat.id, 'number': flat.number})
            response['success'] = True
            response['current_flats'] = current_flats
        except Exception as e:
            LogHelper.elog(e)
            response['success'] = False
            response['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response), content_type='application/json')

    # In this function we update user last active project
    def change_active_project(request, project_id):
        try:
            project = Projects.objects.get(id=project_id)
            request.session['active_project']['id'] = str(project_id)
            request.session['active_project']['name'] = project.name
            request.session["active_building"]['id'] = ''
            request.session["active_building"]['number'] = ''
            request.session["active_flat"]['id'] = ''
            request.session["active_flat"]['number'] = ''
            request.session.modified = True
            current_activity = {
                'project_id': project.id,
                'project_name': project.name
            }
            request.user.current_activity = json.dumps(current_activity)
            request.user.save()
        except Exception as e:
            LogHelper.efail(e)
        return True

    # In this function we update user last active building and project
    def change_active_building(request, building_id):
        try:
            building = Buildings.objects.get(id=building_id)
            request.session['active_project']['id'] = str(building.project_id)
            request.session['active_project']['name'] = building.project.name
            request.session["active_building"]['id'] = str(building_id)
            request.session["active_building"]['number'] = building.display_number
            request.session["active_flat"]['id'] = ''
            request.session["active_flat"]['number'] = ''
            request.session.modified = True
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

    # In this function we update user last active flat, building and project
    def change_active_flat(request, flat_id):
        try:
            flat = Flats.objects.get(id=flat_id)
            request.session['active_project']['id'] = str(flat.building.project_id)
            request.session['active_project']['name'] = flat.building.project.name
            request.session["active_building"]['id'] = str(flat.building_id)
            request.session["active_building"]['number'] = flat.building.display_number
            request.session["active_flat"]['id'] = str(flat_id)
            request.session["active_flat"]['number'] = flat.number
            request.session.modified = True
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

    # This function will return all the buildings by user last active project
    def get_all_buildings_by_active_project(request):
        try:
            project_id = request.session['active_project']['id']
            buildings = Buildings.objects.annotate(total_flats=Count('flats')).filter(project_id=project_id)
            return render(request, 'profiles/buildings.html', {"buildings": buildings})
        except Exception as e:
            LogHelper.elog(e)
            return redirect('index')

    # This function will return all the falts by user last active building
    def get_all_flats_by_active_building(request):
        try:
            building_id = request.session['active_building']['id']
            flats = Flats.objects.annotate(total_tasks=Count('buildingcomponents__tasks')).filter(building_id=building_id)
            return render(request, 'profiles/flats.html', {"flats": flats})
        except Exception as e:
            LogHelper.elog(e)
            return redirect('index')


# All the notification text will set from here
class NotificationText(generic.DetailView):
    def get_edit_task_notification_text(user_name, task_title):
        text = "{} hat {} geändert"
        return text.format(user_name, task_title)

    def get_assign_worker_notification_text(user_name, company_name, task_title):
        text = "{} hat {} zu {} hinzugefügt"
        return text.format(user_name, company_name, task_title)

    def get_change_task_status_notification_text(user_name, task_title, task_status):
        status = "Noch nicht begonnen"
        if task_status == 'in_progress':
            status = "in Arbeit"
        elif task_status == 'done':
            status = "Fertig"
        text = "{} hat den status von {} geändert: {}"
        return text.format(user_name, task_title, status)

    def get_task_comment_notification_text(user_name, task_title):
        text = "{} hat {} kommentiert"
        return text.format(user_name, task_title)

    def get_attach_file_notification_text(user_name, task_title):
        text = "{} hat File in {} hinzugefügt"
        return text.format(user_name, task_title)

    def get_change_due_date_notification_text(user_name, task_title, due_date):
        text = "Die frist von {} hat sich  geändert: {}"
        return text.format(task_title, due_date)

