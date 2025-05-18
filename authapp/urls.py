from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
import authapp.views as authapp

app_name = 'authapp'

urlpatterns = [
    path('login/', authapp.login, name='login'),
    path('register/', authapp.register, name='register'),
    path('logout/', authapp.logout, name='logout'),
    path('confirm_email/', authapp.confirm_email, name='confirm_email'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
