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
        self.TXT_TEMPLATE  = 'notification/email/loved_notification_email.txt'
        self.HTML_TEMPLATE = 'notification/email/loved_notification_email.html'
        self.LOG_FILE      = os.path.join(settings.BASE_PATH, "log/loves_notifier.log")
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        logger      = open(self.LOG_FILE, 'a+')
        target_date = datetime.now() - timedelta(days=1)
        loved_items = self.collect_love_nofications(target_date)
        receivers   = set([item.blog.user for item in loved_items])
        
        if len(receivers) > 0:
            notifications = []
            base_url = self.get_base_url()

            for receiver in receivers:
                email = self.prepare_notification_emails(
                    base_url, 
                    receiver, 
                    loved_items.filter(
                        blog__user=receiver
                    ),
                    target_date
                )
                notifications.append(email)

            async.map(notifications)

        logger.write("[%s] Sending %d notification emails.\n" % (datetime.now(), len(receivers)))
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

    def prepare_notification_emails(self, base_url, user, loved_items, target_date):
        activaty_date_str = target_date.strftime("%A, %b %Y")
        email_context = {
            'loved_items': loved_items,
            'base_url'   : base_url,
            'settings'   : settings, 
            'user'       : user,
            'date'       : activaty_date_str,
        }

        return async.post('%s/messages' % settings.MAILGUN_API_DOMAIN,
            auth=('api', settings.MAILGUN_API_KEY),
            data={
                'from'   : settings.DEFAULT_FROM_EMAIL,
                'to'     : user.email,
                'subject': 'Your Oxfam Live Stories activity for %s' % activaty_date_str,
                'text'   : render_to_string(self.TXT_TEMPLATE, email_context),
                'html'   : render_to_string(self.HTML_TEMPLATE, email_context),
            }
        )