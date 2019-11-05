from rest_framework import serializers
from adminapp.models import Tasks


class TaskSerializer(serializers.ModelSerializer):
    due_date = serializers.CharField(max_length=100, read_only=True)
    created_by_id = serializers.IntegerField(read_only=True)
    updated_by_id = serializers.IntegerField(read_only=True)
    created_at = serializers.CharField(max_length=100, read_only=True)
    updated_at = serializers.CharField(max_length=100, read_only=True)
    name = serializers.CharField(max_length=100, read_only=True)
    description = serializers.CharField(max_length=1000, read_only=True)
    status = serializers.CharField(max_length=20)

    class Meta:
        model = Tasks
        fields = ('id', 'name', 'description', 'due_date', 'status', 'created_by_id', 'updated_by_id', 'created_at', 'updated_at')


class TaskDetailsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, read_only=True)
    due_date = serializers.CharField(max_length=100, read_only=True)
    status = serializers.CharField(max_length=20)
    created_by_id = serializers.IntegerField(read_only=True)
    updated_by_id = serializers.IntegerField(read_only=True)
    created_at = serializers.CharField(max_length=100, read_only=True)
    updated_at = serializers.CharField(max_length=100, read_only=True)
    description = serializers.CharField(max_length=1000, read_only=True)
    assign_to = serializers.JSONField(read_only=True)
    status_list = serializers.ListField(read_only=True)
    comments = serializers.JSONField(read_only=True)
    more_comments = serializers.BooleanField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tasks
        fields = ('id', 'name',  'status', 'description', 'due_date', 'created_by_id', 'updated_by_id', 'created_at', 'updated_at', 'assign_to', 'status_list', 'comments', 'more_comments', 'total_comments')
