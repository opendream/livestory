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
        subject = '[Oxfam Livestories] New activity on your photo.'
    elif period_type > 0:
        subject = 'Oxfam Livestories notifications %s update.' % period_type
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
    msg = EmailMultiAlternatives(
        subject, text_email_body, settings.EMAIL_HOST_USER, [user.email]
    )
    msg.attach_alternative(html_email_body, "text/html")
    return msg

def notify_blog_owner(day):
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

def comment_notify_blog_owner(comment):
    profile = comment.blog.user.get_profile()
    notify_type = profile.notification_type
    if (comment.user != comment.blog.user) and notify_type == -1:
        return create_notify_message(comment.blog.user, [], [comment,], comment.post_date, None)

def _send_mail(message):
    try:
        message.send()
        print "send notification SUCCESS"
    except:
        import sys
        print sys.exc_info()
        print "send notification FAILED"

@task()
def send_periodic_notification_mail():
    messages = notify_blog_owner(date.today())
    for msg in messages:
        _send_mail(msg)
            
@task
def send_comment_notification_mail(comment):
    _send_mail(comment_notify_blog_owner(comment))
