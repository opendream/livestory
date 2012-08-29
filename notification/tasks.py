import datetime
from celery import task

# from account.models import UserProfile
from blog.models import Blog

@task()
def add(x, y):
    return x + y


@task()
def send_notification_email():
    # user_profile = UserProfile.objects.all()
    # for user in user_profile:
    #     print user.first_name
    # print "It's work! "
    pass

