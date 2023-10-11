from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from .models import Action
from rest_framework.response import Response
from rest_framework import status
from .serializers import ActionSerializer,ActionUpdateSerializer

# Create your views here.
class NotificationAPIView(generics.ListAPIView):
    serializer_class = ActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        actions = Action.objects.exclude(user=self.request.user)
        # following_ids = self.request.user.following.values_list('id', flat=True)

        # if following_ids:
        #     actions = actions.filter(user_id__in=following_ids)
        actions = actions.filter(recipient=self.request.user).order_by('-created')
        actions = actions[:50]
        return actions
    
class NotificationUpdateAPIView(generics.UpdateAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionUpdateSerializer
    lookup_field = 'id' 
    
    def perform_update(self, serializer):
        serializer.save(read=True)
        
        