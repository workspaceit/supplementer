# from pywebpush import webpush, WebPushException
# import logging
# from django.db.models.signals import post_save, pre_save
# from django.dispatch import receiver
# from pushnotificationapp.models import Subscribers
#
#
# @receiver(pre_save, sender=Subscribers)
# def send_notification(sender, **kwargs):
#     print("Trigger Happened")
#     print(kwargs['instance']['id'])
#     print(kwargs['instance']['keys'])
#     print("Trigger Happened 2")
#
# # pre_save.connect(send_notification, sender= Subscribers)
# #
# # post_save.connect(send_notification, sender= Subscribers)
#
#
# def notification_sender(subscription_info, data):
#     WEBPUSH_VAPID_PRIVATE_KEY = 'NLSiChEl9fXKpH4V0diB-FIzrsYTQZJI3t6m29cMoxU'
#     count = 0
#     # subscription_info = {"endpoint":"https://fcm.googleapis.com/fcm/send/fsjbvwa06ik:APA91bFmUDOncHeDAY7tTSnd4QxatnnTqJXkrv8sB0r2LnPekNrRmMtAaEockO5XqEaQKUBipGpphQxRFkdfYVf38gy8fjcra7x2-M5eO0wfwWE2yEFJl0iuBpIiXdaCP_KsVh1lz3rY","expirationTime":None,"keys":{"p256dh":"BNDo7RaVN_DDd5tb-Yr-FU21hH-G8kNs_h1cOWGjp_I6um0dGoImR_m8mI7MXn8jqFowReDqD_5m3Pa8P3CmHIw","auth":"AMoKHDep1LCZeFfU2OS0Sw"}}
#     subscription_info = subscription_info
#     try:
#         webpush(
#             subscription_info=subscription_info,
#             data=data,
#             vapid_private_key=WEBPUSH_VAPID_PRIVATE_KEY,
#             vapid_claims={
#                 "sub": "mailto:webpush@mydomain.com"
#             }
#         )
#         count += 1
#     except WebPushException as e:
#         logging.exception("webpush fail")