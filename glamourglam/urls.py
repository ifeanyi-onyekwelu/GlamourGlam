from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('default_admin/', admin.site.urls),
    path('admin/', include('glamourAdmin.urls', namespace="my_admin")),
    path('', include('glamourApp.urls', namespace='app'))
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)