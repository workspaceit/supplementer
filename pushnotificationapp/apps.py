from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PushnotificationappConfig(AppConfig):
    name = 'pushnotificationapp'
    verbose_name = _('push')

    def ready(self):
        import pushnotificationapp.signals