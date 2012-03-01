from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from django.http import HttpResponse

from common.templatetags.common_tags import *

import os
import shutil
import settings

@login_required
def ajax_account_image_upload(request):
    account = request.user.get_profile()
    image = request.FILES['image']
    account.image.save(image.name, request.FILES['image'], save=False)
    account.save()
    
    data = {
        'name': image.name,
        'size': image.size,
        'url': account.get_image_url(),
        'thumbnail_url': crop(account.image, settings.AVATAR_SIZE),
        'delete_url': reverse('ajax_account_image_delete'),
        'delete_type': 'DELETE'
    }
    
    return HttpResponse(json.dumps(data), mimetype="application/json")

@login_required    
def ajax_account_image_delete(request):
    account = request.user.get_profile()
    
    #shutil.rmtree('/path/to/folder')
    
    
    try:
        account.image.file
        
        # Delete cache images
        shutil.rmtree(cache_path(account.image.path))
        
        # Delete all old image
        directory, name = os.path.split(account.image.path)
        shutil.rmtree(directory)
        
        account.image.delete()
        data = {'result': 'complete'}
    except:
        data = {'result': 'nofile'}
        
    return HttpResponse(json.dumps(data), mimetype="application/json")