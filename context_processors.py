from django.conf import settings
from notification.views import get_notifications

def site_information(request):
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_LOGO': settings.SITE_LOGO,
        'SITE_LOGO_EMAIL': settings.SITE_LOGO_EMAIL,
        'AVATAR_SIZE': settings.AVATAR_SIZE,
        'AVATAR_TOP_SIZE': settings.AVATAR_TOP_SIZE,
        'BLOG_PREVIEW_SIZE': settings.BLOG_PREVIEW_SIZE,
        'USE_TZ': settings.USE_TZ,
        'notifications': get_notifications(request.user)[:settings.NOTIFICATION_POPUP_NUM],
    }
