from rest_framework import serializers
from adminapp.models import NotificationStatus


class NotificationSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    status = serializers.BooleanField()
    task_id = serializers.SerializerMethodField()
    sending_at = serializers.CharField(max_length=100, read_only=True)

    class Meta:
        model = NotificationStatus
        fields = ('id', 'text', 'avatar', 'status', 'task_id', 'sending_at')

    def get_text(self, notification):
        return notification.notification.text

    def get_task_id(self, notification):
        return notification.notification.task_id

    def get_avatar(self, notification):
        return notification.notification.sending_by.avatar.url if notification.notification.sending_by.avatar else ''
