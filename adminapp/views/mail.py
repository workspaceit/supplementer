# import os
#
# from django.views import generic
# from django.core.mail import EmailMultiAlternatives
#
#
# class MailHelper(generic.View):
#     def mail_send(context, subject, to, sender_mail):
#         html_content = context
#         # logger = logging.getLogger(__name__)
#         # logger.debug("-----------------sender Email------------------------")
#         # logger.debug(sender_mail)
#         # logger.debug("-----------------receiver Email------------------------")
#         # logger.debug(to)
#         # logger.debug("-----------------subject------------------------")
#         # logger.debug(subject)
#         # live
#         if os.environ['ENVIRONMENT_TYPE'] == 'master':
#             msg = EmailMultiAlternatives(subject=subject, from_email=sender_mail,
#                                          to=['workspaceinfotech@gmail.com',to], body=html_content)
#             msg.attach_alternative(html_content, "text/html")
#             msg.send()
#         else:
#             msg = EmailMultiAlternatives(subject=subject, from_email=sender_mail,
#                                          to=['mahedi@workspaceit.com'], body=html_content)
#             msg.attach_alternative(html_content, "text/html")
#             msg.send()


import os

from django.views import generic
from django.conf import settings
from django.template.loader import render_to_string
import boto.ses
import boto
import logging
import html2text

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer():
    from_addr = settings.EMAIL_HOST_USER
    subject = ""
    to = ""

    def __init__(self, subject, to, from_addr=settings.EMAIL_HOST_USER):
        self.from_addr = from_addr
        self.subject = subject
        self.to = to

        access_key = settings.SMTP_USERNAME
        secret_key = settings.SMTP_PASSWORD
        region = settings.SES_REGION

        self.conn = boto.ses.connect_to_region(
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

    def send(self, message):
        # call this to send an email
        # it takes html string as a message
        from_email_address = self.from_addr
        subject = self.subject
        to = self.to
        if settings.LOCAL_ENV:
            to = 'workspaceinfotech@gmail.com'
        messages=self.mime_email(subject,from_email_address,to,html2text.html2text(message,"",256),message)
        self.conn.send_raw_email(messages)

    def mime_email(self,subject, from_address, to_address, text_message=None, html_message=None):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_address
        msg['To'] = to_address
        if text_message:
            msg.attach(MIMEText(text_message, 'plain'))
        if html_message:
            msg.attach(MIMEText(html_message, 'html'))

        return msg.as_string()


class MailHelper(generic.View):
    def mail_send(context, subject, to, sender_mail):
        html_content = context
        if os.environ['ENVIRONMENT_TYPE'] == 'master':
            # email = Mailer(subject=subject, to='webservice@frprojektbau.de', from_addr=sender_mail)
            # email.send(html_content)
            email = Mailer(subject=subject, to=to, from_addr=sender_mail)
            email.send(html_content)
        else:
            email = Mailer(subject=subject, to='webservice@frprojektbau.de', from_addr=sender_mail)
            email.send(html_content)





