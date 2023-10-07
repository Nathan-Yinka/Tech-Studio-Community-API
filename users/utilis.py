from django.core.mail import send_mail
from .models import Community,EmailConfirmationToken
from django.core.mail import send_mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

def send_confirmation_email(user, request):
    
    try:
        existing_email_confirmation = EmailConfirmationToken.objects.filter(user=user).first()
    
    
        if existing_email_confirmation:
            existing_email_confirmation.delete()

        token = default_token_generator.make_token(user)
        
        serializer = URLSafeTimedSerializer('your-secret-key') 
        
        signed_token = serializer.dumps({'token': token})
        signed_user_id = serializer.dumps({'user_id': user.id})
        
        email_confirmation = EmailConfirmationToken(user=user, token=signed_token)
        email_confirmation.save()
        
        token_data = {
            'uid': signed_user_id,
            'token': signed_token,
        }
        confirmation_link = reverse('user:confirm-email', kwargs=token_data)
        confirmation_url = request.build_absolute_uri(confirmation_link)

        subject = "Confirm Your Email Address"
        message = f"Click the link below to confirm your email address:\n\n{confirmation_url}"
        from_email = "noreply@example.com"
        recipient_list = [user.email]
        
        send_mail(subject, message, from_email, recipient_list)
        
    except Exception as e:
        print(e)
        