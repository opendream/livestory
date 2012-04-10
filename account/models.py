from django.db import models
from django.contrib.auth.models import User

from common.templatetags.common_tags import *

import pytz

try :
    import Image
except ImportError:
    from PIL import Image

from django.conf import settings

def account_image_url(instance, filename):
    ext = filename.split('.')[-1]
    return './images/account/%s/avatar.%s' % (instance.user.id, ext)

class Account(models.Model):
    
    image     = models.ImageField(upload_to=account_image_url, null=True)
    firstname = models.CharField(max_length=200, null=True)
    lastname  = models.CharField(max_length=200, null=True)
    timezone  = models.CharField(max_length=200, default='UTC', choices=[(tz, tz) for tz in pytz.common_timezones])
    
    user      = models.OneToOneField(User)
    
    def get_fullname(self):
        return '%s %s' % (self.firstname, self.lastname)
    
    def get_image(self):
        try:
            self.image.file
            return self.image
        except ValueError:
            image  = {
                'url': '%s/static/img/default_user.png' % '.',
                'path': 'static/img/default_user.png'
            }
            image = type('imageobj', (object,), image)
            return image
            
    def get_image_url(self):
        try:
            self.image.file
            return path_to_url(self.image.path)
        except ValueError:
            return None
            
    def __unicode__(self):
        return '%s' % (self.get_fullname())

    def is_activated(self):
        return not AccountKey.objects.filter(user__email=email).exists()

    def status(self):
        if self.user.is_active:
            return 'active'
        else:
            if not self.user.last_login: 
                return 'not-activate'
            else:
                return 'block'

class AccountKey(models.Model):
    
    key           = models.CharField(max_length=200)
    view_notification = models.DateTimeField(auto_now_add=True)
    can_send_mail = models.NullBooleanField(null=True)
    modified      = models.DateTimeField(auto_now=True)
    
    user     = models.OneToOneField(User)
        
    def __unicode__(self):
        return '%s has key %s' % (self.user.username, self.key)

    def update_view_notification(self):
        self.view_notification = datetime.now()
        self.save()
        return self.view_notification
