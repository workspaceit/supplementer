from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from pushnotificationapp.models import Subscribers
from pushnotificationapp.serializers import SubscribersSerializer


class SubscriberViewSet(viewsets.ModelViewSet):
    queryset = Subscribers.objects.all()
    serializer_class = SubscribersSerializer

    def get_queryset(self):
        user_id = self.request.GET.get("user_id")
        queryset = Subscribers.objects.all()
        if user_id:
            queryset = Subscribers.objects.filter(user_id=user_id)
        return queryset


    @action(detail=False, methods=['DELETE'], name='delete')
    def destroy_by_user(self, request, *args, **kwargs):
        user_id = request.POST['user_id']
        device = request.POST['device']
        if user_id:
            queryset = Subscribers.objects.filter(user_id=user_id) & Subscribers.objects.filter(device=device)
            self.perform_destroy(queryset)
        return Response(status=status.HTTP_204_NO_CONTENT)
