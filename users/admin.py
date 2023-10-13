from django.contrib import admin
from .models import User,Community,EmailConfirmationToken,PasswordResetConfirmationToken,Contact
from django.contrib.auth.admin import UserAdmin

# Register your models here.
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active',)  # This line is important to filter by is_active
    ordering = ('email',)


admin.site.register(Community)
admin.site.register(EmailConfirmationToken)
admin.site.register(PasswordResetConfirmationToken)
admin.site.register(Contact)

