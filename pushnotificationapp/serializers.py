from rest_framework import serializers

from pushnotificationapp.models import Subscribers


class SubscribersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribers
        fields = '__all__'
