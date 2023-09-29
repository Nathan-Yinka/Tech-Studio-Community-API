from rest_framework import viewsets
from .models import JobPost,Skill,JobPoster,Tool
from .serializers import JobPostSerializer,SkillSerializer,JobPosterSerializer,JobListSerializer,ToolSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.db.models import Q
from django.shortcuts import redirect
from rest_framework import status
from .dropdown import deadline_choices,job_type,job_experiences,jobposts_pays

class JobPostViewSet(generics.GenericAPIView):
    queryset = JobPost.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return JobListSerializer  # Serializer for GET requests with depth
        else :
            return JobPostSerializer  # Serializer for POST requests (create)
    
    def get(self, request, *args, **kwargs):
        jobposts = self.get_queryset()
        serializer = self.get_serializer(jobposts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class JobPosterView(generics.GenericAPIView):
    serializer_class = JobPosterSerializer
    queryset = JobPoster.objects.all()
    
    def get(self,request):
        jobposters = self.get_queryset()
        serializer = self.get_serializer(jobposters,many=True)
        
        return Response(serializer.data)
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            full_name = serializer.validated_data.get("full_name")
            jobposter, created = JobPoster.objects.get_or_create(email=email)
            jobposter.full_name = full_name
            jobposter.save()
            
            serializer = self.get_serializer(jobposter)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SkillCreateView(generics.CreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    
    def perform_create(self, serializer):
        email = serializer.validated_data.get("email")
        client_created = serializer.validated_data.get("client_created")
        if email:
            client_created = True
        serializer.save(client_created=client_created)
        
class ToolCreateView(generics.CreateAPIView):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    
    def perform_create(self, serializer):
        email = serializer.validated_data.get("email")
        client_created = serializer.validated_data.get("client_created")
        if email:
            client_created = True
        serializer.save(client_created=client_created)
            
class DropDownItem(APIView):
    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        skills = Skill.objects.filter(Q(email=None) | Q(email=email))
        tools = Tool.objects.filter(Q(email=None) | Q(email=email))
        skills = SkillSerializer(instance=skills, many=True)
        tools = ToolSerializer(instance=tools, many=True)
        
        dropdown_items ={"deadline_choices":deadline_choices,'job_type':job_type,'job_experiences':job_experiences,"jobposts_pays":jobposts_pays,"skills":skills.data,"tools":tools.data}
        return Response(dropdown_items)