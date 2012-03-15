import hashlib
import os
import settings

from django import template
from datetime import datetime

FMT = 'JPEG'
EXT = 'jpg'
QUAL = 75

register = template.Library()

@register.filter()
def path_to_url(path):
	return path.replace(settings.BASE_PATH, '')

def cache_path(path):
    directory, name = os.path.split(path)
    directory = directory.replace(settings.MEDIA_ROOT, '')
    return '%scache/%s' % (settings.MEDIA_ROOT, directory)

def resized_path(path, size, method):
    "Returns the path for the resized image."
    directory, name = os.path.split(path)
    directory = cache_path(path)
    
    image_name, ext = name.rsplit('.', 1)
    return os.path.join(directory, '%s_%s_%s.%s' % (image_name, method, size, EXT))



@register.filter()
def scale(imagefield, size, method='scale'):
    """ 
    Template filter used to scale an image
    that will fit inside the defined area.

    Returns the url of the resized image.

    {% load image_tags %}
    {{ profile.picture|scale:"48x48" }}
    """

    # imagefield can be a dict with "path" and "url" keys
    if imagefield.__class__.__name__ == 'dict':
        imagefield = type('imageobj', (object,), imagefield)
    
    original_path = ''
    # Support filepath
    if type(imagefield) is unicode:
        original_path = imagefield
        image_path = resized_path(original_path, size, method)
        image_url = imagefield
        try:
            format = imagefield.split('.')[-1].upper()
            if format == 'JPG':
                format = 'JPEG'
        except IndexError:
            format = 'JPEG'
    else:
        original_path = imagefield.path
        image_path = resized_path(original_path, size, method)
        image_url = imagefield.url
        try:
            format = imagefield.path.split('.')[-1].upper()
            if format == 'JPG':
                format = 'JPEG'
        except IndexError:
            format = 'JPEG'
    
    directory, name = os.path.split(image_path)
                
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    if not os.path.exists(image_path):
        try:
            import Image
        except ImportError:
            try:
                from PIL import Image
            except ImportError:
                raise ImportError('Cannot import the Python Image Library.')

        if type(imagefield) is unicode:
            image = Image.open(imagefield)
        else:
            image = Image.open(imagefield.path)

        # normalize image mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        if format == 'PNG':
            pixdata = image.load()
            for y in xrange(image.size[1]):
                for x in xrange(image.size[0]):
                    if pixdata[x, y] == (0, 0, 0, 0):
                        pixdata[x, y] = (255, 255, 255, 0)
        
        # parse size string 'WIDTHxHEIGHT'
        width, height = [int(i) for i in size.split('x')]
        # use PIL methods to edit images
        if method == 'scale':
            image.thumbnail((width, height), Image.ANTIALIAS)
            image.save(image_path, format)

        elif method == 'crop':
            try:
                import ImageOps
            except ImportError:
                from PIL import ImageOps

            ImageOps.fit(image, (width, height), Image.ANTIALIAS
                        ).save(image_path, format, quality=QUAL)
    
    path = resized_path(original_path, size, method)
    return '%s?r=%s' % (path_to_url(path), hashlib.md5(str(datetime.now())).hexdigest()[0:5])

@register.filter()
def crop(imagefield, size):
    """
    Template filter used to crop an image
    to make it fill the defined area.

    {% load image_tags %}
    {{ profile.picture|crop:"48x48" }}

    """
    
    return scale(imagefield, size, 'crop')
    

