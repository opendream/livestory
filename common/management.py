from django.conf import settings
from django.contrib.sites import models as site_app
from django.contrib.sites.models import Site
from django.db.models import signals

def create_default_site(app, created_models, verbosity, **kwargs):
    if Site in created_models:
        try:
            site = Site.objects.get(id=settings.SITE_ID)
            site.delete()
        except:
            pass

        Site.objects.create(id=settings.SITE_ID, domain=settings.SITE_DOMAIN, name=settings.SITE_NAME)

    Site.objects.clear_cache()

signals.post_syncdb.connect(create_default_site, sender=site_app)