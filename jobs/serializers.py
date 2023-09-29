from rest_framework import serializers
from .models import JobPost, Skill, Tool,JobPoster
from datetime import datetime, timedelta
from django.utils import timezone
from .dropdown import deadline_choices

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = '__all__'

class JobPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = '__all__'
        
    def create(self, validated_data):
        deadline = validated_data.get("deadline")
        current_datetime = datetime.now()
        deadline_delta = deadline_mapping.get(deadline)
        
        if deadline_delta:
            calculated_deadline = current_datetime + deadline_delta
            
        else:
            calculated_deadline = current_datetime + timedelta(weeks=2)
            
        formatted_deadline = calculated_deadline.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        validated_data['deadline'] = formatted_deadline
        
        return super().create(validated_data)
        
class JobListSerializer(serializers.ModelSerializer):
    active = serializers.SerializerMethodField(read_only=True)
    time_left = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = JobPost
        fields = '__all__'
        depth = 1
    
    def get_active(self, obj):
        deadline_datetime = datetime.strptime(obj.deadline, "%Y-%m-%dT%H:%M:%S.%f%z")
        created_datetime = obj.created
        return deadline_datetime > created_datetime
    
    def get_time_left(self, obj):
        deadline_datetime = datetime.strptime(obj.deadline, "%Y-%m-%dT%H:%M:%S.%f%z")
        created_datetime = obj.created
        time_difference = deadline_datetime - created_datetime

        time_left_in_days = time_difference.days
        
        if time_left_in_days > 0:
            return time_left_in_days
        
        return 0
        
        
class JobPosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPoster
        fields = "__all__"
        


