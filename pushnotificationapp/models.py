from django.db import models
from adminapp.models import Users
from pywebpush import webpush, WebPushException
import logging
from pyfcm import FCMNotification
import json
# Create your models here.
from notifications.signals import notify


class Subscribers(models.Model):
    endpoint = models.TextField(max_length=2000)
    expirationTime = models.DateTimeField(null=True)
    keys = models.TextField(max_length=2000, null=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    device = models.CharField(max_length=512)


class BulkCreateQuerySet(models.query.QuerySet):
    def bulk_create(self, objs, **kwargs):
        for i in objs:
            user = Users.objects.get(id=i.user_id)
            avatar = i.notification.sending_by.avatar.url if i.notification.sending_by.avatar else ''
            notify.send(i.notification.sending_by, recipient=user, verb=i.notification.text, description=avatar, target=i.notification.task)
            self.send_notification(user,i)
        return super().bulk_create(objs,**kwargs)

    def send_notification(self,sender, instance):
        try:
            subscribers = Subscribers.objects.filter(user_id=instance.user_id)
            for subscriber in subscribers:
                if subscriber.device == "mobile":
                    push_service = FCMNotification(api_key="AIzaSyDe760rQNsg6JOJbohxdrYTW86E9FtDSyw")
                    registration_id = "d7mMlK4FKR4:APA91bGCnJ-fPmlmvRDJTnTBTeg7-ZSeUh-puqrSHdAShkNIZEJrF5c2pTcadmU5rioks8aOIwek9oFKCxI0jIJXC1I19gMhyyD3gnGOU0eTeo8SDjkGTejxjYyDYww7d5t77yqsruUs"
                    result = push_service.notify_single_device(registration_id=registration_id,
                                                               message_title=instance.notification.task,
                                                               message_body=instance.notification.text)

                else:
                    subscription_info = {"endpoint": subscriber.endpoint, "keys": json.loads(subscriber.keys)}
                    self.notification_sender(subscription_info, instance.notification.text)
        except Exception as e:
            print(e)

    def notification_sender(self,subscription_info, data):
        count = 0
        VAPID_CLAIMS = {
            "exp": 1212121212,
            "sub": "mailto:service@workspaceit.com"
        }

        subscription_info = subscription_info
        try:
            webpush(
                subscription_info=subscription_info,
                data=data,
                vapid_private_key="bF0oatL1tc0-vPr_9Lx8VMUmXA4Fgp_dJaQMpZk25ag",
                vapid_claims=VAPID_CLAIMS
            )
            count += 1
        except WebPushException as e:
            logging.exception("webpush fail")


class BulkCreateManager(models.Manager):
    def get_queryset(self):
        return BulkCreateQuerySet(self.model)

