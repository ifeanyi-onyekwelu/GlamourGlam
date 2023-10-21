from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from .utils import custom_error_404, custom_error_500

handler404 = custom_error_404
handler500 = custom_error_500

urlpatterns = [
    path('default-admin/', admin.site.urls),
    path('admin/', include('glamourAdmin.urls', namespace="my_admin")),
    path('', include('glamourApp.urls', namespace='app')),
    path('', include('django.contrib.auth.urls')),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)