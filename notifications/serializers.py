from rest_framework import serializers
from .models import Action
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email','fullname','image')

class ActionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Action
        fields = '__all__'
        
class ActionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ["id","read"]