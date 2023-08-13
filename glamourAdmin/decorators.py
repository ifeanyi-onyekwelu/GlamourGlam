from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, reverse

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
