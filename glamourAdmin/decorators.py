from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, reverse
from users.models import CustomUser

def admin_only_login(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('my_admin:login'))
        elif not request.user.is_superuser:
            return redirect(reverse('my_admin:login'))
        else:
            return f(request, *args, **kwargs)
    return wrapper

def prevent_authenticated_access(redirect_url_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                redirect_url = reverse(redirect_url_name)
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def single_admin_registration(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if there is an admin user in the system
        if CustomUser.objects.filter(is_superuser=True).exists():
            return redirect('my_admin:login')

        return view_func(request, *args, **kwargs)

    return _wrapped_view