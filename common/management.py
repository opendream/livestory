from django.conf import settings
from django.contrib.sites.models import Site

def after_syncdb(sender, **kwargs):
    Site.objects.get_or_create(domain=settings.SITE_DOMAIN, name=settings.SITE_NAME)

from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="common.management")