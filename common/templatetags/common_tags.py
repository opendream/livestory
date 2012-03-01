import os
import settings

from django import template

FMT = 'JPEG'
EXT = 'jpg'
QUAL = 75

register = template.Library()

@register.filter()
def path_to_url(path):
	return path.replace(settings.base_path, '')

def cache_path(path):
    directory, name = os.path.split(path)
    directory = directory.replace(settings.IMAGE_ROOT, '')
    return '%scache/%s' % (settings.IMAGE_ROOT, directory)

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

    image_path = resized_path(imagefield.path, size, method)
    
    directory, name = os.path.split(image_path)
    
    try:
        format = imagefield.path.split('.')[-1].upper()
        if format == 'JPG':
            format = 'JPEG'
    except IndexError:
        format = 'JPEG'
                
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
    
    print imagefield.url
    path = resized_path(imagefield.url, size, method)
    return path_to_url(path)

@register.filter()
def crop(imagefield, size):
    """
    Template filter used to crop an image
    to make it fill the defined area.

    {% load image_tags %}
    {{ profile.picture|crop:"48x48" }}

    """
    
    return scale(imagefield, size, 'crop')
    

