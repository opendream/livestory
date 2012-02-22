def site_information(request):
    import settings
    return {'SITE_NAME': settings.SITE_NAME}
