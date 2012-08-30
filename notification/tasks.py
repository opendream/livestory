import datetime as datetime_imported
from celery import task

from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count
from django.template.loader import render_to_string

from account.models import UserProfile
from blog.models import Blog, Comment, Love
from notification.models import Notification


# ###### COMMAND: python manage.py celeryd -B --loglevel=info
@task()
def send_notification_email():
    user_profile = UserProfile.objects.exclude(user__is_superuser=True)

    for user in user_profile:
        if user.notification_type and user.next_notified == datetime_imported.date.today():
            send_to_emails = ['tarongpong@opendream.co.th'] if settings.DEBUG else [user.user.email]

            start_date = user.next_notified - datetime_imported.timedelta(days=int(user.notification_type))

            loves = Love.objects.filter(
                blog__user      = user.user,
                datetime__gt    = start_date,
                datetime__lt    = datetime_imported.date.today(),
            ).exclude(
                user         = user.user
            )

            comments = Comment.objects.filter(
                blog__user      = user.user,
                post_date__gt   = start_date,
                post_date__lt   = datetime_imported.date.today(),
            ).exclude(
                user            = user.user
            ).values('user', 'blog').annotate(count_user_comments=Count('user'))

            for comment in comments:
                user_profile = UserProfile.objects.get(id=comment['user'])
                comment.update({'user_fullname': user_profile.get_full_name()})
                comment.update({'avatar': user_profile.get_avatar()})

            if loves or comments:
                date = start_date.strftime('%B %d, %Y') if user.get_notification_type_display() == 'Daily' else str(start_date.strftime('%B %d, %Y')) + ' to ' + str((datetime_imported.date.today()-datetime_imported.timedelta(days=1)).strftime('%B %d, %Y'))

                email_context = {
                    'comments': comments,
                    'date': date,
                    'loves': loves,
                    'settings': settings,
                }
                text_email_body = render_to_string('notification/email/loved_notification_email.txt', email_context)
                html_email_body = render_to_string('notification/email/loved_notification_email.html', email_context)

                msg = EmailMultiAlternatives(
                    'Oxfam livestories notifications %s update.' % user.get_notification_type_display(), 
                    text_email_body, 
                    settings.EMAIL_HOST_USER, 
                    send_to_emails
                )
                msg.attach_alternative(html_email_body, "text/html")

                try:
                    msg.send()
                    print "send notification SUCCESS"
                except:
                    import sys
                    print sys.exc_info()
                    print "send notification FAILED"

            # #     # TODOLIST: Add date to next notify

