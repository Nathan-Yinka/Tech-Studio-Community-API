from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from api.permissions import IsOwnerOrReadOnly,IsStaffOrReadOnly
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model,authenticate
from .serializers import CustomUserSerializer,UserLoginSerializer,CommumitySerializer,PasswordResetRequestSerializer,PasswordResetConfirmSerializer,EmailConfirmSerializer,ResendConfirmationEmailSerializer,FollowUnfollowSerializer
from .models import Community,EmailConfirmationToken,AllowedEmail,PasswordResetConfirmationToken,Contact
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.core import signing
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from django.http import Http404
from .utilis import send_confirmation_email,send_password_reset_email
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from api.pagination import MyCustomPagination
from django.shortcuts import get_object_or_404
from notifications.utils import create_action

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        email = request.data.get("email")
        if email:
            allowed_mail = AllowedEmail.objects.filter(email=email).first()

            if allowed_mail is None:
                return Response({"message": "You are not allowed to register because you are not an alumnus of Tech Studio Academy."},status=status.HTTP_403_FORBIDDEN)

        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            if existing_user.is_active:
                return Response({'message': 'An account with this email address already exists and is active.'}, status=status.HTTP_409_CONFLICT)
            else:
                send_confirmation_email(existing_user,request)

                return Response({'message': 'An account with this email address already exists but is not yet active. We have sent you a confirmation link. \n\n will expire in 5 mintues.'}, status=status.HTTP_202_ACCEPTED)

        if serializer.is_valid():
            user = serializer.save(is_active=False)

            # Generate a confirmation token
            send_confirmation_email(user,request)

            return Response({'message': 'Registration successful. Check your email for a confirmation link. \n\n will expire in 5 mintues.'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
class EmailConfirmationView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailConfirmSerializer
    def post(self, request):
        try:
            serializer = EmailConfirmSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            uid = serializer.validated_data['uid']
            token = serializer.validated_data['token']
            
            serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
            data = serializer.loads(uid, max_age=172800)
            uid = data['user_id']

            user = User.objects.get(id=uid)

            if user.is_active:
                return Response({'message': 'Email already confirmed proceed to login page'}, status=status.HTTP_200_OK)
            
            try:
                email_confirmation = EmailConfirmationToken.objects.get(user=user,token=token)

                data = serializer.loads(token, max_age=300) 
                token = data['token']
                
                if default_token_generator.check_token(user, token):
                    email_confirmation.delete()

                    user.is_active = True
                    user.save()

                    return Response({'message': 'Email confirmed successfully.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid Link.'}, status=status.HTTP_400_BAD_REQUEST)
            except SignatureExpired:
                return Response({'message': 'Link has expired. Click resend link to get new confimation link.'}, status=status.HTTP_400_BAD_REQUEST)
            except BadSignature:
                return Response({'message': 'Invalid Link.'}, status=status.HTTP_400_BAD_REQUEST)
            except EmailConfirmationToken.DoesNotExist:
                return Response({'message': 'User Not Found.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'User Not Found.'}, status=status.HTTP_400_BAD_REQUEST)
        except SignatureExpired:
                return Response({'message': 'User Not Found.'}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
                return Response({'message': 'Invalid Link.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def post(self,request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'No user found with this email.'}, status=status.HTTP_400_BAD_REQUEST)
        send_password_reset_email(user,request)
        
        return Response({'message': 'Password reset link sent successfully to your email.'}, status=status.HTTP_200_OK)
    
class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            uid = serializer.validated_data['uid']
            token = serializer.validated_data['token']
            password = serializer.validated_data['new_password']
            
            serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
            data = serializer.loads(uid, max_age=172800)
            uid = data['user_id']
            
            user = User.objects.get(id=uid)
            
            try:
                email_confirmation = PasswordResetConfirmationToken.objects.get(user=user,token=token)
                
                data = serializer.loads(token, max_age=300) 
                token = data['token']
                
                if default_token_generator.check_token(user, token):
                    email_confirmation.delete()
                    
                    user.set_password(password)
                    user.save()
                    
                    return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid Link.'}, status=status.HTTP_400_BAD_REQUEST)
            except SignatureExpired:
                return Response({'message': 'Link has expired.'}, status=status.HTTP_400_BAD_REQUEST)
            except BadSignature:
                return Response({'message': 'Invalid Link.'}, status=status.HTTP_400_BAD_REQUEST)
            except EmailConfirmationToken.DoesNotExist:
                return Response({'message': 'User Not Found.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'User Not Found.'}, status=status.HTTP_400_BAD_REQUEST)
        except SignatureExpired:
                return Response({'message': 'User Not Found.'}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
                return Response({'message': 'Invalid Link.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
class UserListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = get_user_model().objects.filter(is_active =True)
    serializer_class = CustomUserSerializer
    pagination_class = MyCustomPagination
    
    def list(self, request, *args, **kwargs):
        # Get the paginated queryset
        queryset = self.filter_queryset(self.get_queryset())
        # Paginate the queryset
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        queryset = get_user_model().objects.filter(is_active =True)

        search_query = self.request.query_params.get('name', None)
        tags = self.request.query_params.get('community', None)

        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        if tags:
            queryset = queryset.filter(community__name__icontains=tags)
            
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(pk=self.request.user.pk)
            
        return queryset
    
    
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.filter(is_active =True)
    serializer_class = CustomUserSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    
class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)

        if user is not None and user.is_active:
            user_serializer = UserLoginSerializer(user)
            token, created = Token.objects.get_or_create(user=user)
            response_data = {'id': user.id,'token': token.key }
            return Response(response_data, status=status.HTTP_200_OK)
        
        elif user is not None and not user.is_active:
            send_confirmation_email(user, request)
            return Response({'detail': 'Your account is not yet active. We have sent you a confirmation email. \n\n will expire in 5 mintues.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)
        
class ResendConfirmationEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResendConfirmationEmailSerializer
    def post(self, request):
        try:
            id = request.data.get('uid')
            serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
            data = serializer.loads(id, max_age=172800)
            uid = data['user_id']
        except:
            return Response({'message': 'User not found or already confirmed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        try:
            user = User.objects.get(id=uid, is_active=False)
            send_confirmation_email(user,request)
            return Response({'message': 'Confirmation email resent successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User not found or already confirmed.'}, status=status.HTTP_400_BAD_REQUEST)
        
class CommunityListView(generics.ListCreateAPIView):
    serializer_class = CommumitySerializer
    queryset = Community.objects.all()
    permission_classes = [IsStaffOrReadOnly]
    
    
    
class UserFollow(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUnfollowSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data['user_to']
            try:
                contact, created = Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user_id)
                print(user_id.id)
                if created:
                    create_action(request.user, 'followed', user_id,user_id)
                    response_data = { 'message': 'Followed'}
                else:
                    response_data = { 'message': 'Already following'}

                return Response(response_data,status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserUnfollow(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUnfollowSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data['user_to']

            try:
                Contact.objects.filter(
                    user_from=request.user,
                    user_to=user_id).delete()

                return Response({'message': 'Unfollowed'},status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)