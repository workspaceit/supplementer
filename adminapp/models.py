from django.db import models
from django.core.validators import FileExtensionValidator
# from django.contrib.auth.models import User
from django_mysql.models import JSONField
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import FileSystemStorage
# from pywebpush import webpush, WebPushException
import logging
# from pushnotificationapp.models import Subscribers
# from pyfcm import FCMNotification
import json

# Create your models here.
# from notifications.signals import notify

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


def my_default():
    return {'foo': 'bar'}


class EnumField(models.Field):
    def __init__(self, *args, **kwargs):
        super(EnumField, self).__init__(*args, **kwargs)
        assert self.choices, "Need choices for enumeration"

    def db_type(self, connection):
        if not all(isinstance(col, basestring) for col, _ in self.choices):
            raise ValueError("MySQL ENUM values should be strings")
        return "ENUM({})".format(','.join("'{}'".format(col)
                                          for col, _ in self.choices))


class CommentType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('text', 'Text'),
            ('file', 'File')
        ]
        kwargs.setdefault('choices', roles)
        super(CommentType, self).__init__(*args, **kwargs)


class NotificationType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('edit_task', 'Edit Task'),
            ('assign_worker', 'Assign Worker'),
            ('change_task_status', 'Change Task Status'),
            ('task_comment', 'Task Comment'),
            ('attach_file', 'Attach File'),
            ('change_due_date', 'Change Due Date'),
        ]
        kwargs.setdefault('choices', roles)
        super(NotificationType, self).__init__(*args, **kwargs)


class TaskStatusType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('to_do', 'To Do'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
        ]
        kwargs.setdefault('choices', roles)
        super(TaskStatusType, self).__init__(*args, **kwargs)


class Users(AbstractUser):
    address = models.TextField(null=True)
    avatar = models.FileField(null=True, upload_to='avatar/', validators=[FileExtensionValidator(allowed_extensions=['jpg','png','svg','jpeg'])], storage=FileSystemStorage())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_activity = JSONField(null=True, blank=True)

    # USERNAME_FIELD = 'email'

    def get_full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        db_table = "users"


@receiver(post_delete, sender=Users)
def submission_delete(sender, instance, **kwargs):
   instance.avatar.delete(False)


class Projects(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    energetic_standard = models.CharField(max_length=100, null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(Users, related_name='project_created_by', null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(Users, related_name='project_last_updated_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"


class ProjectPlans(models.Model):
    title = models.CharField(max_length=100)
    plan_file = models.FileField(null=True, upload_to='project/plans/', storage=FileSystemStorage())
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=45)
    created_by = models.ForeignKey(Users, related_name='project_plan_created_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_plans"


class ProjectStuff(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    created_by = models.ForeignKey(Users, related_name='project_assigned_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_stuff"


class Buildings(models.Model):
    hause_number = models.CharField(max_length=45)
    display_number = models.CharField(max_length=45)
    description = models.TextField(null=True, blank=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    grundung = models.CharField(max_length=45)
    aussenwande_eg_og_dg = models.CharField(max_length=45)
    fenster_beschattung = models.CharField(max_length=45)
    dach = models.CharField(max_length=45, null=True, blank=True)
    created_by = models.ForeignKey(Users, related_name='building_created_by', null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(Users, related_name='building_last_updated_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "buildings"


class BuildingPlans(models.Model):
    title = models.CharField(max_length=100)
    plan_file = models.FileField(null=True, upload_to='building/plans/', storage=FileSystemStorage())
    building = models.ForeignKey(Buildings, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=45)
    created_by = models.ForeignKey(Users, related_name='building_plan_created_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "building_plans"


class Flats(models.Model):
    number = models.CharField(max_length=45)
    description = models.TextField(null=True, blank=True)
    building = models.ForeignKey(Buildings, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100, null=True, blank=True)
    client_address = models.TextField(null=True, blank=True)
    client_email = models.CharField(max_length=50, null=True, blank=True)
    client_tel = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.ForeignKey(Users, related_name='flat_created_by', null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(Users, related_name='flat_last_updated_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "flats"


class FlatPlans(models.Model):
    title = models.CharField(max_length=100)
    plan_file = models.FileField(null=True, upload_to='flat/plans/', storage=FileSystemStorage())
    flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=45)
    created_by = models.ForeignKey(Users, related_name='flat_plan_created_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "flat_plans"


class Components(models.Model):
    name = models.CharField(max_length=100)
    static_description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, related_name='parent_component', on_delete=models.CASCADE)
    type = models.CharField(max_length=255, null=True, blank=True)
    building = models.BooleanField(default=True)
    flat = models.BooleanField(default=True)
    created_by = models.ForeignKey(Users, related_name='component_created_by', null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(Users, related_name='component_last_updated_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "components"


class BuildingComponents(models.Model):
    building = models.ForeignKey(Buildings, on_delete=models.CASCADE)
    flat = models.ForeignKey(Flats, null=True, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    component = models.ForeignKey(Components, null=True, on_delete=models.SET_NULL)
    assign_to = models.ForeignKey(Users, related_name='component_assign_to', null=True, on_delete=models.SET_NULL)
    assigned_by = models.ForeignKey(Users, related_name='component_assigned_by', null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(Users, related_name='building_component_created_by', null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(Users, related_name='building_component_last_updated_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "building_components"


class Tasks(models.Model):
    building_component = models.ForeignKey(BuildingComponents, on_delete=models.CASCADE)
    followers = JSONField(null=True, blank=True)
    status = TaskStatusType(max_length=20, default="to_do")
    due_date = models.DateField(default=None, null=True, blank=True)
    created_by = models.ForeignKey(Users, related_name='task_created_by', null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(Users, related_name='task_last_updated_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"


class Comments(models.Model):
    text = models.TextField()
    type = CommentType(max_length=10, default="text")
    file_type = JSONField(null=True, blank=True)
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comments"


class HandWorker(models.Model):
    company_name = models.CharField(max_length=100)
    telephone_office = models.CharField(max_length=50, null=True, blank=True)
    telephone_mobile = models.CharField(max_length=50, null=True, blank=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    working_type = JSONField(null=True, blank=True)

    class Meta:
        db_table = "handworker"


class QrCode(models.Model):
    unique_key = models.CharField(max_length=50, unique=True)
    building = models.ForeignKey(Buildings, on_delete=models.CASCADE)
    flat = models.ForeignKey(Flats, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(Users, related_name='qr_created_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "qr_code"


class Notification(models.Model):
    type = NotificationType(max_length=20)
    text = models.TextField()
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    sending_by = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        db_table = "notification"


class NotificationStatus(models.Model):
    status = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    sending_at = models.DateTimeField(auto_now_add=True)

    # objects = BulkCreateManager()
    class Meta:
        db_table = "notification_status"


class ResetPassword(models.Model):
    hash_code = models.CharField(max_length=200)
    already_used = models.BooleanField(default=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    expired_at = models.DateTimeField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reset_password"
