from django.conf import settings
from django.shortcuts import render
from django.core.urlresolvers import reverse

from common import timezone

import pytz

class TimezoneMiddleware(object):
    def process_request(self, request):
        tz = pytz.timezone('UTC')

        if request.user.is_authenticated():
            tz = pytz.timezone(request.user.get_profile().timezone)
        
        timezone.activate(tz)