import shutil
import settings

def rm_user(id):
    try:
        shutil.rmtree('%sblog/%s' % (settings.IMAGE_ROOT, id))
    except:
        pass
    try:
        shutil.rmtree('%scache/images/blog/%s' % (settings.MEDIA_ROOT, id))
    except:
        pass