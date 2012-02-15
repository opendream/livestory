from django.db import models
from django.contrib.auth.models import User

from localtion.models import Location

import settings

def blog_image_url(instance, filename):
    return '%sblog/%s/%s' % (settings.IMAGE_ROOT, instance.user.id, filename)

class Category(models.Model):
    name = models.CharField(max_length=200)
    code = models.SlugField()
    
    def __unicode__(self):
        return '%s' % (self.name)

    def save(self, *args, **kwargs):
        self.code = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
class Blog(models.Model):
    MOOD_CHOICES    = ((0, 'Happy'), (1, 'Love'), (2, 'Sad'), (3, 'Boring'))
    PRIVATE_CHOICES = ((False, 'No'), (True, 'Yes'))
    DRAFT_CHOICES   = ((False, 'No'), (True, 'Yes'))
    
    image    = models.ImageField(upload_to=blog_image_url)
    detail   = models.CharField(max_length=1000, null=True)
    mood     = models.IntegerField(default=0, choices=MOOD_CHOICES)
    private  = models.BooleanField(default=False, choices=PRIVATE_CHOICES)
    draft    = models.BooleanField(default=False, choices=DRAFT_CHOICES)
    created  = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    user     = models.ForeignKey(User)
    category = models.ForeignKey(Location)
    location = models.ForeignKey(Location)
    
    def __unicode__(self):
        return '%s' % (self.detail)
        
    def get_thumbnail(self, point):
        # TODO
        pass

class Love(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    
    user     = models.ForeignKey(User)
    blog     = models.ForeignKey(Blog)
    
    def __unicode__(self):
        return '%s love %s' % (self.user.username, self.blog.detail)

        
        