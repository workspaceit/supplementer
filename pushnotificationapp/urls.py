from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from pushnotificationapp.views import SubscriberViewSet
from django.views.decorators.csrf import csrf_exempt

router = routers.DefaultRouter()
# router.register(r'subscribe', SubscriberViewSet)

urlpatterns = [
    # path('user-device-info/', csrf_exempt(SubscriberDevice.update_device_info), name='user_device'),
    path('docs/', include_docs_urls(title='API Lists')),
]

urlpatterns += router.urls