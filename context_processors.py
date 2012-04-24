from django.conf import settings
from notification.views import get_notifications
from blog.models import Category
from blog.forms import BlogPlaceFilterForm

def site_information(request):
    place_form = BlogPlaceFilterForm()
    if request.GET.get('country') or request.GET.get('city'):
         place_form = BlogPlaceFilterForm(request.GET)
         
    return {
        'settings':settings,
        'SITE_NAME': settings.SITE_NAME,
        'ORGANIZATION_NAME': settings.ORGANIZATION_NAME,
        'SITE_LOGO': settings.SITE_LOGO,
        'SITE_LOGO_EMAIL': settings.SITE_LOGO_EMAIL,
        'AVATAR_SIZE': settings.AVATAR_SIZE,
        'AVATAR_TOP_SIZE': settings.AVATAR_TOP_SIZE,
        'BLOG_PREVIEW_SIZE': settings.BLOG_PREVIEW_SIZE,
        'USE_TZ': settings.USE_TZ,
        'PRIVATE': settings.PRIVATE,
        'notifications': get_notifications(request.user)[:settings.NOTIFICATION_POPUP_NUM],
        'category_filter': Category.objects.all(),
        'place_form': place_form,
    }
