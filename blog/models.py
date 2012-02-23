import os

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from location.models import Location

import settings

MOOD_CHOICES = (
    (1, 'Sad'), 
    (2, 'Confused'), 
    (3, 'Happy'), 
    (4, 'Laughing'),
    (5, 'Love')
)

PRIVATE_CHOICES = (
    (False, 'Public to everyone'),
    (True, 'Only %s group' % settings.ORGANIZATION_NAME)
)

DRAFT_CHOICES = (
    (False, 'No'), 
    (True, 'Yes')
)

def blog_image_path(instance, filename):
    filepath = '%sblog/%s' % (settings.IMAGE_ROOT, instance.user.id)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    return '%s/%s' % (filepath, filename)

def blog_image_url(instance, filename):
    return '%simages/blog/%s/%s' % (settings.MEDIA_URL, instance.user.id, filename)

class Category(models.Model):
    name = models.CharField(max_length=200)
    code = models.SlugField()
    
    def __unicode__(self):
        return '%s' % (self.name)

    def save(self, *args, **kwargs):
        self.code = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
class Blog(models.Model):
    title       = models.CharField(max_length=200)
    image       = models.ImageField(upload_to=blog_image_path)
    description = models.TextField(null=True)
    mood        = models.IntegerField(default=0, choices=MOOD_CHOICES)
    private     = models.BooleanField(default=False, choices=PRIVATE_CHOICES)
    draft       = models.BooleanField(default=False, choices=DRAFT_CHOICES)
    created     = models.DateTimeField(auto_now_add=True)
    modified    = models.DateTimeField(auto_now=True)
                
    user        = models.ForeignKey(User)
    category    = models.ForeignKey(Category)
    location    = models.ForeignKey(Location)
    
    def __unicode__(self):
        return '%s' % (self.title)
    
    def get_image_url(self):
        (folder, filename) = os.path.split(self.image.name)
        return blog_image_url(self, filename)
        
    def get_thumbnail(self, point):
        # TODO
        pass
    
    def get_mood_text(self):
        return MOOD_CHOICES[self.mood-1][1]
    
    def get_loved_users(self):
        return self.love_set()

class Love(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    
    user     = models.ForeignKey(User)
    blog     = models.ForeignKey(Blog)
    
    def __unicode__(self):
        return '%s love %s' % (self.user.username, self.blog.detail)

        
        