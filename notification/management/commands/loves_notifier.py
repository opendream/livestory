from django.contrib.sites.models import Site
from django.core.management.base import NoArgsCommand
from django.template.loader import render_to_string
from django.conf import settings
from requests import async
from datetime import datetime, timedelta
from notification.models import Notification
import os

class Command(NoArgsCommand):
    
    def __init__(self, *args, **kwargs):
        self.TXT_TEMPLATE = 'notification/email/loved_notification_email.txt'
        self.HTML_TEMPLATE = 'notification/email/loved_notification_email.html'
        self.LOG_FILE = os.path.join(settings.BASE_PATH, "log/loves_notifier.log")
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        logger = open(self.LOG_FILE, 'a+')
        now = datetime.now()
        loved_items = self.collect_love_nofications(now - timedelta(days=1))
        receivers = set([item.blog.user for item in loved_items])
        
        if len(receivers) > 0:
            notifications = []
            base_url = self.get_base_url()

            for receiver in receivers:
                receiver_items = loved_items.filter(blog__user=receiver)
                notifications.append(self.prepare_notification_emails(base_url, receiver, receiver_items))

            async.map(notifications)

        logger.write("[%s] Sending %d notification emails.\n" % (now, len(receivers)))
        logger.close()

    def collect_love_nofications(self, for_date):
        return Notification.objects.filter(
            action          = 1, #loved
            datetime__year  = for_date.year,
            datetime__month = for_date.month,
            datetime__day   = for_date.day
        )

    def get_base_url(self):
        site = Site.objects.get(id=settings.SITE_ID)
        return site.domain if site else None

    def prepare_notification_emails(self, base_url, user, loved_items):
        email_context = {
            'loved_items': loved_items,
            'base_url'   : base_url,
            'settings'   : settings, 
            'user'       : user
        }

        return async.post('%s/messages' % settings.MAILGUN_API_DOMAIN,
            auth=('api', settings.MAILGUN_API_KEY),
            data={
                'from'   : settings.DEFAULT_FROM_EMAIL,
                'to'     : user.email,
                'subject': 'Someone loves your blog.',
                'text'   : render_to_string(self.TXT_TEMPLATE, email_context),
                'html'   : render_to_string(self.HTML_TEMPLATE, email_context),
            }
        )