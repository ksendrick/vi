from django.urls import reverse

from mainapp.models import Notification
from recipesapp.models import Category, Kitchen


def categories_and_kitchens(request):
    categories = Category.objects.all()
    kitchens = Kitchen.objects.all()
    return {
        'categories': categories,
        'kitchens': kitchens,
    }


def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        count = 0
    return {
        'unread_notifications_count': count,
    }

def staff_admin_url(request):
    if request.user.is_staff:
        return {
            'staff_admin_url': reverse('staffadmin:newsapp_news_changelist')
        }
    return {'staff_admin_url': None}