from django.shortcuts import render
import os
from dotenv import load_dotenv


load_dotenv()


def custom_error_404(request, exception):
    APP_NAME = os.getenv("APP_NAME")
    context = {
        "APP_NAME": APP_NAME,
    }
    return render(request, "404.html", context, status=404)


def custom_error_500(request):
    APP_NAME = os.getenv("APP_NAME")
    context = {
        "APP_NAME": APP_NAME,
    }
    return render(request, "500.html", context, status=500)
