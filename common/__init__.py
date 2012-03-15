import shutil
from django.conf import settings

def rm_user(id):
    try:
        shutil.rmtree('%sblog/%s' % (settings.IMAGE_ROOT, id))
    except:
        pass
    try:
        shutil.rmtree('%scache/images/blog/%s' % (settings.MEDIA_ROOT, id))
    except:
        pass
        
    try:
        shutil.rmtree('%saccount/%s' % (settings.IMAGE_ROOT, id))
    except:
        pass
    try:
        shutil.rmtree('%scache/images/account/%s' % (settings.MEDIA_ROOT, id))
    except:
        pass
        
def ucwords(string):
    """ucwords -- Converts first letter of each word
    within a string into an uppercase all other to lowercase.

    (string) ucwords( (string) string )"""
    erg=[ item.capitalize() for item in string.split( ' ' ) ]
    return ' '.join( erg )