from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import simplejson as json

from functions import save_temporary_blog_image

@login_required
def ajax_blog_image_upload(request):
    (file_name, thumbnail_url) = save_temporary_blog_image(request.FILES['image'])

    data = {
        'name': file_name,
        'thumbnail_url': thumbnail_url
    }

    return HttpResponse(json.dumps(data))
