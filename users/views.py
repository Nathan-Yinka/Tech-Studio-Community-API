from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from api.permissions import IsOwnerOrReadOnly,IsStaffOrReadOnly
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model,authenticate
from .serializers import CustomUserSerializer,UserLoginSerializer,CommumitySerializer
from .models import Community,EmailConfirmationToken,AllowedEmail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.core import signing
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from django.http import Http404
from .utilis import send_confirmation_email

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        email = request.data.get("email")
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
    def get(self, request, uid, token):
        try:
            
            serializer = URLSafeTimedSerializer('your-secret-key')
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
        
class UserListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = get_user_model().objects.filter(is_active =True)
    serializer_class = CustomUserSerializer
    
    
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
        
class ResendConfirmationEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            id = request.data.get('uid')
            serializer = URLSafeTimedSerializer('your-secret-key')
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
    
    
