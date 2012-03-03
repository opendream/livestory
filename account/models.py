from django.db import models
from django.contrib.auth.models import User

from common.templatetags.common_tags import *

try :
    import Image
except ImportError:
    from PIL import Image

import settings

def account_image_url(instance, filename):
    return '%saccount/%s/%s' % (settings.IMAGE_ROOT, instance.user.id, filename)

class Account(models.Model):
    
    image     = models.ImageField(upload_to=account_image_url, null=True)
    firstname = models.CharField(max_length=200, null=True)
    lastname  = models.CharField(max_length=200, null=True)
    
    user      = models.OneToOneField(User)
    
    def get_fullname(self):
        return '%s %s' % (self.firstname, self.lastname)
    
    def get_image(self):
        try:
            self.image.file
            return self.image
        except ValueError:
            image  = {
                'url': '%s/static/img/default_user.png' % settings.base_path,
                'path': 'static/img/default_user.png'
            }
            image = type('imageobj', (object,), image)
            return image
            
    def get_image_url(self):
        try:
            self.image.file
            return path_to_url(account_image_url(self, self.image.name))
        except ValueError:
            return None
            
    def __unicode__(self):
        return '%s' % (self.get_fullname())

class AccountKey(models.Model):
    
    key           = models.CharField(max_length=200)
    can_send_mail = models.NullBooleanField(null=True)
    modified      = models.DateTimeField(auto_now=True)
    
    user     = models.OneToOneField(User)
        
    def __unicode__(self):
        return '%s has key %s' % (self.user.username, self.key)
