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
from django.conf.urls import include
from django.conf.urls import url
from serviceapp.views.user_views import UserInfo, ResetPasswordRequestViewSet
from rest_framework.routers import SimpleRouter
from serviceapp.views.projects import ProjectViewSet, ProjectPlanViewSet
from serviceapp.views.buildings import BuildingViewSet, BuildingPlanViewSet, BuildingComponentViewSet
from serviceapp.views.flats import FlatViewSet, FlatPlanViewSet, FlatComponentViewSet
from serviceapp.views.tasks import BuildingTasksViewSet, FlatTasksViewSet, TaskDetailsViewSet
from serviceapp.views.comments import CommentsViewSet
from serviceapp.views.notifications import NotificationsViewSet
from serviceapp.views.components import ComponentsViewSet
from serviceapp.views.notifications import SubscriberDevice
from django.views.decorators.csrf import csrf_exempt

router = SimpleRouter()
router.register(r'projects', ProjectViewSet)

urlpatterns = [
    url(r'^auth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^user-profile/', UserInfo.as_view()),
    url(r'^forget-password/', ResetPasswordRequestViewSet.forget_password),
    url(r'^change-user-password/', ResetPasswordRequestViewSet.change_user_password),

    url(r'^project/(?P<project_id>[\w-]+)/plans/$', ProjectPlanViewSet.as_view()),
    url(r'^project/(?P<project_id>[\w-]+)/buildings/$', BuildingViewSet.as_view()),
    url(r'^building/(?P<building_id>[\w-]+)/plans/$', BuildingPlanViewSet.as_view()),
    url(r'^building/(?P<building_id>[\w-]+)/components/$', BuildingComponentViewSet.as_view()),
    url(r'^building/(?P<building_id>[\w-]+)/component/(?P<component_id>[\w-]+)/tasks/$', BuildingTasksViewSet.as_view()),
    url(r'^building/(?P<building_id>[\w-]+)/flats/$', FlatViewSet.as_view()),
    url(r'^flat/(?P<flat_id>[\w-]+)/plans/$', FlatPlanViewSet.as_view()),
    url(r'^flat/(?P<flat_id>[\w-]+)/components/$', FlatComponentViewSet.as_view()),
    url(r'^flat/(?P<flat_id>[\w-]+)/component/(?P<component_id>[\w-]+)/tasks/$', FlatTasksViewSet.as_view()),
    url(r'^task/(?P<task_id>[\w-]+)/$', TaskDetailsViewSet.as_view()),
    url(r'^task/(?P<task_id>[\w-]+)/comments/$', CommentsViewSet.as_view()),
    url(r'^task/(?P<task_id>[\w-]+)/change-status/$', TaskDetailsViewSet.change_task_status),
    url(r'^task/(?P<task_id>[\w-]+)/change-due-date/$', TaskDetailsViewSet.change_task_due_date),
    url(r'^notifications/$', NotificationsViewSet.as_view()),
    url(r'^scan/$', ComponentsViewSet.as_view()),
    url(r'^user-device-info/$', SubscriberDevice.update_device_info, name='user_device'),
] + router.urls