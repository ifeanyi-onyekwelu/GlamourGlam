from django.shortcuts import redirect
from functools import wraps
from django.urls import reverse
from .models import CartItem

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


def cart_not_empty(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            cart = CartItem.objects.filter(cart__user=request.user)

        if not cart:
            return redirect("app:cart_page") 

        return view_func(request, *args, **kwargs)

    return _wrapped_view
