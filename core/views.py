from django.shortcuts import render
from rest_framework import generics
from users.serializers import UserLoginSerializer
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly,IsAuthenticated
from django.contrib.auth import get_user_model,authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from jobs.models import JobPost
from jobs.serializers import JobListSerializer,JobPostSerializer
from api.authentication import StaffUserTokenAuthentication,StaffUserSessionAuthentication
import csv
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
import re
from .serializers import CSVFileUploadSerializer,AllowedEmailSerializer
from .models import AllowedEmail
from api.pagination import MyCustomPagination2
from rest_framework import filters


# Create your views here.
class SuperUserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer
    # authentication_classes = [SuperUserTokenAuthentication]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)

        if user is not None and user.is_active and user.is_superuser:
            user_serializer = UserLoginSerializer(user)
            token, created = Token.objects.get_or_create(user=user)
            response_data = {'id': user.id,'token': token.key }
            return Response(response_data, status=status.HTTP_200_OK)
        
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)
        
class JobPostViewSet(generics.GenericAPIView):
    queryset = JobPost.objects.all()
    authentication_classes =[StaffUserTokenAuthentication,StaffUserSessionAuthentication]
    permission_classes = [IsAuthenticated]
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return JobListSerializer 
        else :
            return JobPostSerializer
    
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
        
        
class AllowedEmailCSVUploadView(generics.GenericAPIView):
    # parser_classes = (FileUploadParser,)
    authentication_classes =[StaffUserTokenAuthentication,StaffUserSessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CSVFileUploadSerializer
        
    def post(self, request, format=None):
        serializer = CSVFileUploadSerializer(data=request.data)

        if serializer.is_valid():
            csv_file = serializer.validated_data['file']
            file_name = csv_file.name

            if not file_name.lower().endswith('.csv'):
                return Response({'detail': 'Invalid file format. Only .csv files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.reader(decoded_file.splitlines(), delimiter=',')
        except Exception as e:
            return Response({'detail': 'Invalid file format'}, status=status.HTTP_400_BAD_REQUEST)

        created_emails = []
        skipped_emails = [] 
        invalid_emails = []

        for row in csv_data:
            if len(row) >= 1:
                email = row[0]

                # Check if the email is in the correct format
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    invalid_emails.append(email)
                    
                # Check if the email already exists in the AllowedEmail model
                elif not AllowedEmail.objects.filter(email=email).exists():
                    allowed_email = AllowedEmail(email=email)
                    allowed_email.save()
                    created_emails.append(email)
                else:
                    skipped_emails.append(email)

        response_data = {
            'created_emails': created_emails,
            'skipped_emails': skipped_emails,
            'invalid_emails': invalid_emails
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
class AllowEmailView(generics.ListCreateAPIView):
    queryset = AllowedEmail.objects.all().order_by("id")
    serializer_class = AllowedEmailSerializer
    pagination_class = MyCustomPagination2
    authentication_classes =[StaffUserTokenAuthentication,StaffUserSessionAuthentication]
    permission_classes = [IsAuthenticated]
    search_fields = ['email']
    filter_backends = [filters.SearchFilter]
    
    def create(self, request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        email = request.data.get("email")
        
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            self.perform_create(serializer)
            return Response({"message":f"{email} has been added"},status=status.HTTP_201_CREATED)
        else:
            if AllowedEmail.objects.filter(email=email).exists():
                return Response({'message':'Email already exists'}, status=status.HTTP_409_CONFLICT)
            error_message = {'message': 'Invaild Email'}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        
class AllowEmailDeleteView(generics.DestroyAPIView):
    queryset = AllowedEmail.objects.all()
    serializer_class = AllowedEmailSerializer
    authentication_classes = [StaffUserTokenAuthentication, StaffUserSessionAuthentication]
    permission_classes = [IsAuthenticated]
        
