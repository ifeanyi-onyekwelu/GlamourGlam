from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from glamourApp import views as app_views
from glamourAdmin import views as admin_views


urlpatterns = [
    path('default_admin/', admin.site.urls),
    path('admin/', include('glamourAdmin.urls', namespace="my_admin")),
    path('', include('glamourApp.urls', namespace='app'))
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# App error handling
handler404 = app_views.error404
handler500 = app_views.error500

# Admin error handling
handler404 = app_views.error404
handler500 = app_views.error500