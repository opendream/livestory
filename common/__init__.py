from account.models import UserProfile, UserInvitation
from common.templatetags.common_tags import ucwords_tag
from django.conf import settings
from django.contrib.auth.models import User
import shutil

def rm_user(id):
    try:
        user = User.objects.get(id=id)
        try:
            UserInvitation.objects.get(user=user).delete()
        except UserInvitation.DoesNotExist:
            pass
        try:
            UserProfile.objects.get(user=user).delete()
        except UserProfile.DoesNotExist:
            pass
        user.delete()
    except User.DoesNotExist:
        pass

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
    return ucwords_tag(string)
    
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
