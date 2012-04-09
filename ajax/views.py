from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from account.models import User

from common.templatetags.common_tags import *
from common.views import file_save_upload

import os
import shutil
from django.conf import settings

@login_required
def ajax_profile_image_upload(request, user_id):
    print 'debug', user_id
    user = get_object_or_404(User, pk=user_id)
    account = user.get_profile()
    image = request.FILES['image']
    print 'good'
    try:
        account.image.file
        account.image.delete()
    except:
        pass
        
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
    print 'url>>', data['url']
    print 'thumb>>', data['thumbnail_url']
    return HttpResponse(json.dumps(data), mimetype="application/json")


@login_required
def ajax_account_image_upload(request):
    account = request.user.get_profile()
    image = request.FILES['image']
    try:
        account.image.file
        account.image.delete()
    except:
        pass
        
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

@login_required
def ajax_blog_image_upload(request):
    f = request.FILES['image']
    file_data = file_save_upload(request.FILES['image'])
    data = {
        'name': f.name,
        'size': f.size,
        'url': file_data['url'],
        'filepath': file_data['filepath'],
        'thumbnail_url': scale(file_data['filepath'], settings.BLOG_PREVIEW_SIZE)
    }
    return HttpResponse(json.dumps(data), mimetype="application/json")

@login_required    
def ajax_blog_image_delete(request):
    data = {'result': 'complete', 'isTemp': False}
    try:
        image_path = request.GET.get('image_path')
        if image_path:
            if image_path.find(settings.TEMP_ROOT) == 0 and os.path.exists(image_path):
                os.unlink(image_path)
                data['isTemp'] = True
    except:
        pass
    return HttpResponse(json.dumps(data), mimetype="application/json")