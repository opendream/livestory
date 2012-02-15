from django.db import models

from django.contrib.auth.models import User

import settings

def account_image_url(instance, filename):
    return '%saccount/%s/%s' % (settings.IMAGE_ROOT, instance.user.id, filename)

class Account(models.Model):
    
    image     = models.ImageField(upload_to=account_image_url)
    firstname = models.CharField(max_length=200)
    lastname  = models.CharField(max_length=200)
    
    user      = models.OneToOneField(User)
    
    def get_fullname(self):
        return '%s %s' % (self.firstname, self,lastname)
        
    def __unicode__(self):
        return '%s' % (self.get_fullname())

class AccountKey(models.Model):
    
    key      = models.CharField(max_length=200)
    modified = models.DateTimeField(auto_now=True)
    
    user     = models.OneToOneField(User)
        
    def __unicode__(self):
        return '%s has key %s' % (self.user.username, self.key)