from rest_framework import serializers
from adminapp.models import Users


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.CharField(read_only=True)
    avatar = serializers.CharField(required=False)
    address = serializers.CharField(read_only=True)
    telephone_office = serializers.CharField(required=False)
    telephone_mobile = serializers.CharField(required=False)
    company_name = serializers.CharField(required=False)
    working_type = serializers.CharField(required=False)
    current_activity = serializers.CharField(required=False)

    class Meta:
        model = Users
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'avatar', 'address', 'telephone_office', 'telephone_mobile', 'company_name', 'working_type', 'current_activity')

