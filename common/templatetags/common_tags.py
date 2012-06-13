import hashlib
import os
from django.conf import settings

from django import template
from datetime import datetime, timedelta

from django.utils.timesince import timesince
from common.templatetags.tz import localtime
from django.template.defaultfilters import date as dateformat

from common.utilities import scale_image, split_filepath

register = template.Library()

@register.filter()
def timeago(d, format='M d, Y f a'):
    now = localtime(datetime.now())
    delta = now - (d - timedelta(0, 0, d.microsecond))
    if delta.days > 0:
        return dateformat(d, format)
    else:
        return '%s ago' %timesince(d) 


@register.filter()
def path_to_url(path):
	return path.replace(settings.BASE_PATH, '')

@register.filter()
def scale_blog_image(image, size):
    size = size.split('x')
    image_path = image.path
    (root, name, ext) = split_filepath(image_path)
    filename = scale_image(image_path, (int(size[0]), int(size[1])))
    image_url = image.url.split('/')
    image_url[-1] = filename
    return '/'.join(image_url)

@register.filter()
def crop(image, size):
    """
    Template filter used to crop an image
    to make it fill the defined area.

    {% load image_tags %}
    {{ profile.picture|crop:"48x48" }}

    """
    size = size.split('x')
    (root, name, ext) = split_filepath(image.path)
    filename = scale_image(image.path, (int(size[0]), int(size[1])), 'crop')
    return '/%s/%s' % (os.path.abspath(root).replace('%s/' % os.path.abspath(settings.BASE_PATH), ''), filename)

@register.filter('ucwords')
def ucwords_tag(string):
    """ucwords -- Converts first letter of each word
    within a string into an uppercase all other to lowercase.

    (string) ucwords( (string) string )"""
    erg=[ item.capitalize() for item in string.split( ' ' ) ]
    return ' '.join( erg )

@register.simple_tag
def active(request, pattern, text=' active'):
    pattern = pattern.split('/')[1:-1]
    path = request.path.split('/')[1:-1]
    
    if len(pattern) < len(path):        
        for i, v in enumerate(pattern):
            if v != path[i]:
                return ''
        
        return text
        
    else:
        for i, v in enumerate(pattern):
            try:
                if v != 'arg' and v != '0' and v != path[i]:
                    return ''
            except:
                return ''
  
        return text
