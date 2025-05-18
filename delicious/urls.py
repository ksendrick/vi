from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from delicious import settings
from mainapp.admin import staff_admin_site

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('mainapp.urls', namespace='mainapp')),

    path('accounts/', include('authapp.urls', namespace='authapp')),

    path('recipes/', include('recipesapp.urls', namespace='recipesapp')),
    path('news/', include('newsapp.urls', namespace='newsapp')),

    path('tinymce/', include('tinymce.urls')),
    path('staff-admin/', staff_admin_site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
