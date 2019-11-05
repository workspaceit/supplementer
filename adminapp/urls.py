"""supplementer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView

from adminapp.views import common_views, login_views, staff_views, company_views, project_views, building_views, \
    flat_views, buildingplan_views, flatplan_views, component_views, reset_password, datatables, profile_views, \
    projectplan_views, task_views, notification_views, update_database, misc_views
from django.conf import settings
from django.views.static import serve
urlpatterns = [
    url(r'^$', common_views.IndexView.as_view(), name='index'),
    url(r'^login/$', login_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', login_views.LogoutView.as_view(), name='logout'),
    url(r'^forget-password/$', reset_password.ResetPasswordRequestView.as_view(), name='forget-password'),
    url(r'^reset-password/$', reset_password.ResetPasswordView.as_view(), name='reset-password'),

    url(r'^profile/update/$', profile_views.ProfileUpdateView.as_view(), name='profile-update'),
    url(r'^change-password/$', profile_views.ChangePassword.as_view(), name='change-password'),

    url(r'^staffs/$', staff_views.StaffsView.as_view(), name='staffs'),
    url(r'^staffs/add/$', staff_views.StaffFormView.as_view(), name='staffs-add'),
    url(r'^staffs/update/(?P<pk>[\w-]+)/$', staff_views.StaffUpdateView.as_view(), name='staffs-update'),
    url(r'^staffs/delete/$', staff_views.StaffsView.delete, name='staffs-delete'),
    url(r'^staff-list/$', datatables.StaffListView.as_view(), name='staffList'),
    url(r'^staffs/change-password/(?P<pk>[\w-]+)$', staff_views.StaffPasswordChangeView.as_view(),name='staffs-password-update'),

    url(r'^companies/$', company_views.CompaniesView.as_view(), name='companies'),
    url(r'^companies/add/$', company_views.CompanyFormView.as_view(), name='companies-add'),
    url(r'^companies/update/(?P<pk>[\w-]+)/$', company_views.CompanyUpdateView.as_view(), name='companies-update'),
    url(r'^companies/delete/$', company_views.CompaniesView.delete, name='companies-delete'),
    url(r'^company-list/$', datatables.CompanyListView.as_view(), name='companyList'),
    url(r'^companies/change-password/(?P<pk>[\w-]+)$', company_views.CompanyPasswordChangeView.as_view(),name='companies-password-update'),

    url(r'^change-user-status/$', staff_views.StaffsView.change_user_status, name='change-user-status'),

    url(r'^projects/$', project_views.ProjectsView.as_view(), name='projects'),
    url(r'^projects/add/$', project_views.ProjectFormView.as_view(), name='projects-add'),
    url(r'^projects/update/(?P<pk>[\w-]+)/$', project_views.ProjectUpdateView.as_view(), name='projects-update'),
    url(r'^projects/delete/$', project_views.ProjectsView.delete, name='projects-delete'),
    url(r'^project-list/$', datatables.ProjectListView.as_view(), name='projectList'),

    url(r'^change-project-status/$', project_views.ProjectsView.change_project_status, name='change-project-status'),

    url(r'^projects/(?P<project_id>[\w-]+)/buildings/$', building_views.BuildingsView.as_view(), name='buildings'),
    url(r'^building-list/$', datatables.BuildingListView.as_view(), name='buildingList'),
    url(r'^projects/(?P<project_id>[\w-]+)/buildings/add/$', building_views.BuildingFormView.as_view(), name='buildings-add'),
    url(r'^buildings/update/(?P<pk>[\w-]+)/$', building_views.BuildingUpdateView.as_view(), name='buildings-update'),
    url(r'^buildings/delete/$', building_views.BuildingsView.delete, name='buildings-delete'),
    url(r'^buildings/qr/(?P<pk>[\w-]+)/$', building_views.BuildingsView.preview_qr, name='buildings-qr'),
    url(r'^buildings/(?P<building_id>[\w-]+)/tasks/$', task_views.TasksView.get_all_building_tasks, name='building-tasks'),

    url(r'^buildings/(?P<building_id>[\w-]+)/flats/$', flat_views.FlatsView.as_view(), name='flats'),
    url(r'^flats-list/$', datatables.FlatListView.as_view(), name='flatList'),
    url(r'^buildings/(?P<building_id>[\w-]+)/flats/add/$', flat_views.FlatFormView.as_view(), name='flats-add'),
    url(r'^flats/update/(?P<pk>[\w-]+)/$', flat_views.FlatUpdateView.as_view(), name='flats-update'),
    url(r'^flats/delete/$', flat_views.FlatsView.delete, name='flats-delete'),
    url(r'^flats/qr/(?P<pk>[\w-]+)/$', flat_views.FlatsView.preview_qr, name='flats-qr'),
    url(r'^flats/(?P<flat_id>[\w-]+)/tasks/$', task_views.TasksView.get_all_flat_tasks, name='flat-tasks'),

    url(r'^components/$', component_views.ComponentView.as_view(), name='components'),
    url(r'^components/add/$', component_views.ComponentAddView.as_view(), name='component-add'),
    url(r'^components/update/(?P<pk>[\w-]+)/$', component_views.ComponentUpdateView.as_view(), name='component-update'),
    url(r'^components/delete/$', component_views.ComponentView.delete, name='component-delete'),

    url(r'^building-plans/$', buildingplan_views.BuildingPlansView.get_all_plans_by_active_building, name='building-plans'),
    url(r'^building/(?P<building_id>[\w-]+)/plan/add/$', buildingplan_views.BuildingPlansAddView.as_view(), name='building-plan-add'),
    # url(r'^building-plan/update/(?P<pk>[\w-]+)/$', buildingplan_views.BuildingPlansUpdateView.as_view(), name='building-plan-update'),
    url(r'^building-plan/delete/$', buildingplan_views.BuildingPlansView.delete, name='building-plan-delete'),

    url(r'^flat-plans/$', flatplan_views.FlatPlansView.get_all_plans_by_active_flat, name='flat-plans'),
    url(r'^flat/(?P<flat_id>[\w-]+)/plan/add/$', flatplan_views.FlatPlansAddView.as_view(), name='flat-plan-add'),
    # url(r'^flat-plan/update/(?P<pk>[\w-]+)/$', flatplan_views.FlatPlansUpdateView.as_view(), name='flat-plan-update'),
    url(r'^flat-plan/delete/$', flatplan_views.FlatPlansView.delete, name='flat-plan-delete'),

    url(r'^project-plans/$', projectplan_views.ProjectPlansView.get_all_plans_by_active_project, name='project-plans'),
    url(r'^project/(?P<project_id>[\w-]+)/plan/add/$', projectplan_views.ProjectPlansAddView.as_view(), name='project-plan-add'),
    # url(r'^project-plan/update/(?P<pk>[\w-]+)/$', projectplan_views.ProjectPlansUpdateView.as_view(), name='project-plan-update'),
    url(r'^project-plan/delete/$', projectplan_views.ProjectPlansView.delete, name='project-plan-delete'),

    url(r'^sw.js', (TemplateView.as_view(template_name="sw.js", content_type='application/javascript', )), name='sw.js'),

    url(r'^qr-to-png/(?P<qr_id>[\w-]+)/$', common_views.QRResponse.as_view(), name='qr-to-png'),

    url(r'^current-buildings/$', common_views.CurrentProjects.get_all_current_buildings, name='current-buildings'),
    url(r'^current-project-buildings/$', common_views.CurrentProjects.get_all_buildings_by_active_project, name='current-project-buildings'),
    url(r'^current-project-flats/$', common_views.CurrentProjects.get_all_flats_by_active_building, name='current-project-flats'),
    url(r'^current-flats/$', common_views.CurrentProjects.get_all_current_flats, name='current-flats'),

    url(r'^get-pending-components/$', task_views.TasksView.get_pending_components, name='get-pending-components'),
    url(r'^get-done-components/$', task_views.TasksView.get_done_components, name='get-done-components'),
    url(r'^get-all-components/$', task_views.TasksView.get_all_components, name='get-all-components'),
    url(r'^get-component-tasks/$', task_views.TasksView.get_component_tasks, name='get-component-tasks'),
    url(r'^get-handworker-list/$', task_views.TasksView.get_handwerker_list, name='get-handworker-list'),
    url(r'^assign-handworker/$', task_views.TasksView.assign_handwerker, name='assign-handworker'),
    # url(r'^get-active-tasks/$', task_views.TasksView.get_active_tasks, name='get-active-tasks'),

    url(r'^tasks/(?P<task_id>[\w-]+)/$', task_views.TaskDetailsView.as_view(), name='task-details'),
    url(r'^save-task-description/$', task_views.TaskDetailsView.save_task_description, name='save-task-description'),
    url(r'^change-task-status/$', task_views.TaskDetailsView.change_task_status, name='change-task-status'),
    url(r'^change-task-deadline/$', task_views.TaskDetailsView.change_task_deadline, name='change-task-deadline'),
    url(r'^add-new-comment/(?P<task_id>[\w-]+)/$', task_views.TaskDetailsView.add_new_comment, name='add-new-comment'),
    url(r'^get-more-comments/$', task_views.TaskDetailsView.get_more_comments, name='get-more-comments'),
    url(r'^add-task-followers/$', task_views.TaskDetailsView.add_task_followers, name='add-task-followers'),
    url(r'^get-new-notifications/$', notification_views.NotificationsView.get_new_notifications, name='get-new-notifications'),
    url(r'^get-all-notifications/$', notification_views.NotificationsView.as_view(), name='get-all-notifications'),
    url(r'^get-more-notifications/$', notification_views.NotificationsView.get_more_notifications, name='get-more-notifications'),
    url(r'^read-all-notifications/$', notification_views.NotificationsView.read_all_notification, name='read-all-notifications'),
    url(r'^privacy_policy/$', misc_views.privacy_policy.as_view(), name='privacy_policy'),

    url(r'^update-database/$', update_database.UpdateDatabaseView.as_view(), name='update-database'),
    url(r'^update-database-request/$', update_database.UpdateDatabaseView.update_database, name='update-database-request'),


]

