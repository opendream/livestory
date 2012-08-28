import os
import private_files
import shutil

try :
    import Image
except ImportError:
    from PIL import Image

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify

from common.utilities import split_filepath

from location.models import Location
from taggit.managers import TaggableManager
from taggit.models import TaggedItem


MOOD_CHOICES = (
    (1, 'Fun'         ), 
    (2, 'Amazed'      ), 
    (3, 'Happy'       ), 
    (4, 'Motivated'   ),
    (5, 'Proud'       ),
    (6, 'Excited'     ),
    (7, 'Inspired'    ),
    (8, 'Frustrated'  ),
    (9, 'Angry'       ),
    (10,'Sad'         ),
    (99, 'Moodless'   ), 
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
    name = models.CharField(max_length=200, db_index=True)
    code = models.SlugField()
    
    def __unicode__(self):
        return '%s' % (self.name)

    def save(self, *args, **kwargs):
        self.code = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
class Blog(models.Model):
    title          = models.CharField(max_length=200, db_index=True)
    image          = private_files.PrivateFileField(upload_to=blog_image_url, max_length=500, attachment=False)
    description    = models.TextField(null=True, db_index=True)
    related_url    = models.URLField(blank=True)
    download_url   = models.URLField(blank=True)
    mood           = models.IntegerField(default=0, choices=MOOD_CHOICES)
    private        = models.BooleanField(default=settings.PRIVATE, choices=PRIVATE_CHOICES)
    draft          = models.BooleanField(default=False, choices=DRAFT_CHOICES)
    trash          = models.BooleanField(default=False)
    allow_download = models.BooleanField(default=True)
    published      = models.DateTimeField(null=True, blank=True)
    modified       = models.DateTimeField(auto_now=True)
                   
    user           = models.ForeignKey(User)
    category       = models.ForeignKey(Category)
    location       = models.ForeignKey(Location)
    tags           = TaggableManager()
    
    image_captured_date   = models.DateTimeField(null=True, blank=True)
    image_captured_device = models.CharField(max_length=200)
    
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
        else:
            if self.id:
                self.tags.clear()
        return True

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

    def get_image_file_name(self):
        (root, name ,ext) = split_filepath(self.image.path)
        return '%s.%s' % (name, ext)

    def get_image_size(self):
        if self.image and os.path.exists(self.image.path):
            img = Image.open(self.image.path)
            return str(img.size[0]) + 'x' + str(img.size[1])

    def downloadable(self, req_user=None):
        is_owner = self.user == req_user if req_user else False
        is_admin = req_user.is_superuser if req_user else False
        download_allow = getattr(settings, 'ALLOW_USER_TO_DOWNLOAD_PHOTO', False)

        if is_owner or is_admin:
            return True
        elif self.draft:
            return False
        else:
            return self.allow_download if download_allow else False

    def get_absolute_url(self):
        return reverse('blog_view', args=[self.id])

class Love(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    
    user     = models.ForeignKey(User)
    blog     = models.ForeignKey(Blog)
    
    def __unicode__(self):
        return '%s love %s' % (self.user.username, self.blog.title)

class Comment(models.Model):
    user = models.ForeignKey(User)
    blog = models.ForeignKey(Blog)
    comment = models.TextField(max_length=500)
    post_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s comment on blog(%d) - %s' % (user.username, blog.id, comment)

# Schema Migration Rules for South
from private_files import PrivateFileField
from south.modelsinspector import add_introspection_rules

rules = [((PrivateFileField,), [], {"attachment" : ["attachment", {"default": True}],},)]
add_introspection_rules(rules, ["^private_files\.models\.fields\.PrivateFileField"])