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
    
def get_page_range(pagination, padding=3):
    page_range = pagination.paginator.page_range
    p = pagination.number
    l = 1+padding
    r = padding
    lp = p+r-page_range[-1] if p+r > page_range[-1] else 0
    rp = l-p if p-l < 0 else 0
    lr = p-l-lp if p-l-lp >= 0 else 0
    rr = p+r + rp
    
    return page_range[lr:rr]
