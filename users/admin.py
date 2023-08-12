from django.contrib import admin
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = CustomUser
    form = CustomUserChangeForm
    list_display = ['first_name', 'last_name', 'email', 'username', 'date_joined', 'last_login', 'is_active']


admin.site.register(CustomUser, CustomUserAdmin)