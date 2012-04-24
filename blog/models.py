import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify

#from common.templatetags.common_tags import cache_path
from location.models import Location
from taggit.managers import TaggableManager
from taggit.models import TaggedItem

from common.utilities import split_filepath

import shutil

MOOD_CHOICES = (
    (99, 'Moodless' ), 
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

def blog_image_url(instance, filename):
    (root, name, ext) = split_filepath(filename)
    return './images/blog/%s/%s.%s' % (instance.user.id, name, ext)

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
    image          = models.ImageField(upload_to=blog_image_url, max_length=500)
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
            from functions import remove_blog_image
            remove_blog_image(self)
        super(Blog, self).delete()


class Love(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    
    user     = models.ForeignKey(User)
    blog     = models.ForeignKey(Blog)
    
    def __unicode__(self):
        return '%s love %s' % (self.user.username, self.blog.title)
