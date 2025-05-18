from django.urls import path
import mainapp.views as mainapp

app_name = 'mainapp'
urlpatterns = [
    path('', mainapp.index, name='index'),

    path('upload/', mainapp.upload_image, name='upload_image'),

    path('profile/', mainapp.profile, name='profile'),
    path('profile_author/<int:user_id>/', mainapp.profile_author, name='profile_author'),

    path('notifications/', mainapp.notifications, name='notifications'),
    path('notifications/<int:notification_id>/', mainapp.notification_detail, name='notification_detail'),

    path('edit_profile/', mainapp.edit_profile, name = 'edit_profile'),

    path('notifications/mark_all_read/', mainapp.mark_all_as_read, name='mark_all_as_read'),

]
