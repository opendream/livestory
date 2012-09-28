from datetime import datetime, timedelta, date
from celery import task

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from account.models import UserProfile
from blog.models import Blog, Comment, Love
from notification.models import Notification

###### COMMAND run celery: python manage.py celeryd -B --loglevel=info

ACTIVITIES_EMAIL_TEMPLATE = 'notification/email/activities_notification_email'

def get_periodic_notify_users(today):
    return User.objects.filter(
        userprofile__notification_type__gt=0, 
        userprofile__next_notified=today
    )

def get_blog_love_events(user, str_date, end_date):
    return Love.objects.filter(
        blog__user      = user,
        datetime__range = [str_date, end_date]
    ).exclude(
        user = user
    )

def get_blog_comment_events(user, str_date, end_date):
    return Comment.objects.filter(
        blog__user      = user,
        post_date__range = [str_date, end_date]
    ).exclude(
        user = user
    ).values('user', 'blog').annotate(count_user_comments=Count('user'))

def create_notify_message(user, love_list, comment_list, start_date, end_date):
    period_type = user.get_profile().notification_type
    date = start_date.strftime('%B %d, %Y')
    if period_type == -1:
        subject = 'New activity.'
    elif period_type > 0:
        subject = '%s update.' % period_type
        if period_type == 7:
            date += str(' to ' + end_date.strftime('%B %d, %Y'))

    email_context = {
        'date': date if period_type > 0 else None,
        'loves': love_list,
        'comments': comment_list,
        'settings': settings,
    }
    text_email_body = render_to_string('%s.txt' % ACTIVITIES_EMAIL_TEMPLATE, email_context)
    html_email_body = render_to_string('%s.html' % ACTIVITIES_EMAIL_TEMPLATE, email_context)
    return {
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': [user.email],
        'subject': subject,
        'text_email_body': text_email_body,
        'html_email_body': html_email_body,
    }

def periodic_notify_blog_owner(day):
    msg_list = []
    usr_list = get_periodic_notify_users(today=day)
    for user in usr_list:
        profile = user.get_profile()
        period_days = int(profile.notification_type)
        str_date = day - timedelta(period_days)
        str_date = datetime(str_date.year, str_date.month, str_date.day, 0, 0, 0)
        end_date = day - timedelta(1)
        end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)

        love_list = get_blog_love_events(user, str_date, end_date)
        comment_list = get_blog_comment_events(user, str_date, end_date)
        if len(love_list) + len(comment_list) > 0:
            msg_list.append(
                create_notify_message(
                    user, love_list, comment_list, str_date, end_date
                )
            )
        profile.next_notified = day + timedelta(period_days)
        profile.save()
    return msg_list

def instant_notify_blog_owner(event):
    profile = event.blog.user.get_profile()
    notify_type = profile.notification_type
    if (event.user != event.blog.user) and notify_type == -1:
        if isinstance(event, Comment):
            return create_notify_message(event.blog.user, [], [event], event.post_date, None)
        elif isinstance(event, Love):
            return create_notify_message(event.blog.user, [event], [], event.datetime, None)

from requests import async

def _send_mail(message):
    async.map([
        async.post('%s/messages' % settings.MAILGUN_API_DOMAIN,
            auth=('api', settings.MAILGUN_API_KEY),
            data={
                'from'    : message['from'],
                'to'      : message['to'],
                'subject' : message['subject'],
                'text'    : message['text_email_body'],
                'html'    : message['html_email_body']
            }
        )
    ])

@task()
def send_periodic_notification_mail():
    messages = periodic_notify_blog_owner(date.today())
    for msg in messages:
        _send_mail(msg)
            
@task
def send_instant_notification_mail(event):
    _send_mail(instant_notify_blog_owner(event))
