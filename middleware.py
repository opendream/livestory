from common import timezone
import pytz

class TimezoneMiddleware(object):
    def process_request(self, request):
        tz = pytz.timezone('UTC')

        if request.user.is_authenticated():
            print 'yyyyyyy'
            print request.user.get_profile().timezone
            tz = pytz.timezone(request.user.get_profile().timezone)
        
        timezone.activate(tz)