from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import AllowedEmail
from django.http import HttpResponse
from django.contrib import messages

class SuperuserUploadForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    file = forms.FileField()

@user_passes_test(lambda u: u.is_superuser)
def superuser_upload_view(request):
    duplicate_email = []
    method = ""
    if request.method == 'POST':
        form = SuperuserUploadForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            file = request.FILES['file']

            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_superuser:
                AllowedEmail.objects.all().delete()
                try:
                    with file.open()  as file:
                        method = "POST"
                        for email in file:
                            try:
                                email = email.decode('utf-8').strip()  # Convert bytes to string and remove whitespace
                                allowed_mail = AllowedEmail.objects.create(email=email)
                                allowed_mail.save()
                            except Exception as e:
                                if "UNIQUE constraint failed" in str(e):
                                    duplicate_email.append(email)
                                else:
                                    messages.error(request, f"error uploading {email}")
                except Exception as e:
                    messages.error(request, f"Error loading the file")
                messages.success(request, "Emails successfully uploaded")    
            else:
                messages.error(request, "Invaild Login Credentials")
    else:
        form = SuperuserUploadForm()
    return render(request, 'user_upload_form.html', {'form': form, "duplicate_email":duplicate_email,"method":method })
