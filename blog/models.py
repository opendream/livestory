import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify

from common.templatetags.common_tags import cache_path
from location.models import Location
from taggit.managers import TaggableManager
from taggit.models import TaggedItem

import shutil

MOOD_CHOICES = (
    (1, 'Happy'     ), 
    (2, 'Sad'       ), 
    (3, 'Excited'   ), 
    (4, 'Inspired'  ),
    (5, 'Frustrated'),
    (6, 'Angry'     ),
    (7, 'Fun'       ),
    (8, 'Proud'     ),
    (9, 'Amazed'    ),
    (10,'Motivated' )
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
    filepath = '%sblog/%s/%s' % (settings.IMAGE_ROOT, instance.user.id, instance.id)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    return '%s/blog_%d.jpg' % (filepath, instance.id)

def blog_image_url(instance, filename):
    return './images/blog/%s/%s/%s' % (instance.user.id, instance.id, filename)

class Category(models.Model):
    name = models.CharField(max_length=200)
    code = models.SlugField()
    
    def __unicode__(self):
        return '%s' % (self.name)

    def save(self, *args, **kwargs):
        self.code = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
class Blog(models.Model):
    title          = models.CharField(max_length=200)
    image          = models.ImageField(upload_to=blog_image_url)
    description    = models.TextField(null=True)
    mood           = models.IntegerField(default=0, choices=MOOD_CHOICES)
    private        = models.BooleanField(default=settings.PRIVATE, choices=PRIVATE_CHOICES)
    draft          = models.BooleanField(default=False, choices=DRAFT_CHOICES)
    trash          = models.BooleanField(default=False)
    allow_download = models.BooleanField(default=True)
    created        = models.DateTimeField(auto_now_add=True)
    modified       = models.DateTimeField(auto_now=True)
                   
    user           = models.ForeignKey(User)
    category       = models.ForeignKey(Category)
    location       = models.ForeignKey(Location)
    tags           = TaggableManager()
    
    def __unicode__(self):
        return '(%d) %s' % (self.id, self.title)
    
    def get_mood_text(self):
        moods = dict(MOOD_CHOICES)
        return moods[self.mood]

    def save_tags(self, tags):
        if tags:
            if type(tags) is unicode or type(tags) is str:
                tags = tags.split(',')

            if self.id:
                self.tags.clear()
                for tag in tags:
                    self.tags.add(tag.strip())
                return True
        return False

    def get_tags(self):
        tags = []
        for item in TaggedItem.objects.filter(object_id=self.id).order_by('id'):
            tags.append(item.tag.name)
        return ", ".join(tags)

    def delete(self, **kwargs):
        if not 'with_file' in kwargs:
            with_file = True
        else:
            with_file = kwargs['with_file']

        if with_file:
            blog_image_path = '%sblog/%s/%s' % (settings.IMAGE_ROOT, self.user.id, self.id)
            if os.path.exists(blog_image_path):
                shutil.rmtree(blog_image_path)
            cache_image_path = cache_path(blog_image_path)
            if os.path.exists(cache_image_path):
                shutil.rmtree(cache_image_path)
        super(Blog, self).delete()


class Love(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    
    user     = models.ForeignKey(User)
    blog     = models.ForeignKey(Blog)
    
    def __unicode__(self):
        return '%s love %s' % (self.user.username, self.blog.title)
