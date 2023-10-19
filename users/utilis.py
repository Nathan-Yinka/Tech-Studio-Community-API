from django.core.mail import send_mail
from .models import Community,EmailConfirmationToken,PasswordResetConfirmationToken
from django.core.mail import send_mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings

def send_confirmation_email(user, request):
    
    try:
        existing_email_confirmation = EmailConfirmationToken.objects.filter(user=user).first()
    
    
        if existing_email_confirmation:
            existing_email_confirmation.delete()

        token = default_token_generator.make_token(user)
        
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY) 
        
        signed_token = serializer.dumps({'token': token})
        signed_user_id = serializer.dumps({'user_id': user.id})
        
        email_confirmation = EmailConfirmationToken(user=user, token=signed_token)
        email_confirmation.save()
        
        token_data = {
            'uid': signed_user_id,
            'token': signed_token,
        }
        confirmation_link = reverse('auth:confirm-email')
        confirmation_link = "https://tech-studio-community-frontend-ngf7-nathan-yinka.vercel.app/email-confimation/"
        # confirmation_url = request.build_absolute_uri(confirmation_link)
        confirmation_url = f'{confirmation_link}{signed_user_id}/{signed_token}/'

        # subject = "Confirm Your Email Address"
        # message = f"Click the link below to confirm your email address:\n\n{confirmation_url}"
        # from_email = "techstudioacademy@technologynathan.com"
        # recipient_list = [user.email]
        
        subject = "Confirm Your Email Address"
        context = {'confirmation_link': confirmation_url}

        # Load and render the HTML template
        html_message = render_to_string('confirmation_email.html', context)

        from_email = "techstudioacademy@technologynathan.com"
        recipient_list = [user.email]

        send_mail(subject, '', from_email, recipient_list, html_message=html_message, fail_silently=False)
        
        # send_mail(subject, message, from_email, recipient_list,fail_silently=False)
        
    except Exception as e:
        print(e)
        
        
        
def send_password_reset_email(user, request):
    
    try:
        existing_email_confirmation = PasswordResetConfirmationToken.objects.filter(user=user).first()
    
    
        if existing_email_confirmation:
            existing_email_confirmation.delete()

        token = default_token_generator.make_token(user)
        
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY) 
        
        signed_token = serializer.dumps({'token': token})
        signed_user_id = serializer.dumps({'user_id': user.id})
        
        email_confirmation = PasswordResetConfirmationToken(user=user, token=signed_token)
        email_confirmation.save()
        
        token_data = {
            'uid': signed_user_id,
            'token': signed_token,
        }
        password_reset_link = reverse('auth:confirm-password-reset')
        password_reset_link = request.build_absolute_uri(password_reset_link)
        password_reset_link = f'{password_reset_link}{signed_user_id}/{signed_token}/'

        # subject = "Confirm Your Email Address"
        # message = f"Click the link below to confirm your email address:\n\n{confirmation_url}"
        # from_email = "techstudioacademy@technologynathan.com"
        # recipient_list = [user.email]
        
        subject = "Password Reset Request"
        context = {'password_reset_link': password_reset_link}

        html_message = render_to_string('password_reset.html', context)

        from_email = "techstudioacademy@technologynathan.com"
        recipient_list = [user.email]

        send_mail(subject, '', from_email, recipient_list, html_message=html_message, fail_silently=False)
        
        # send_mail(subject, message, from_email, recipient_list,fail_silently=False)
        
    except Exception as e:
        print(e)
        