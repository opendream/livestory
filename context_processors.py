def site_information(request):
    import settings
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_LOGO': settings.SITE_LOGO,
        'SITE_LOGO_EMAIL': settings.SITE_LOGO_EMAIL,
        'AVATAR_SIZE': settings.AVATAR_SIZE,
        'AVATAR_TOP_SIZE': settings.AVATAR_TOP_SIZE
    }
