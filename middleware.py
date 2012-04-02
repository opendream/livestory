from django.conf import settings
from django.shortcuts import render
from django.core.urlresolvers import reverse

from common import timezone

import pytz

class TimezoneMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated() and settings.PRIVATE:
            
            psplit = request.path.split('/')
            
            if request.path not in (reverse('account_login'), reverse('account_forgot'), reverse('blog_create_by_email')) and not (len(psplit) == 5 and psplit[1] == 'account' and psplit[2] == 'activate'):
                print psplit
                return render(request, 'blog/blog_static.html')
                
        tz = pytz.timezone('UTC')

        if request.user.is_authenticated():
            tz = pytz.timezone(request.user.get_profile().timezone)
        
        timezone.activate(tz)