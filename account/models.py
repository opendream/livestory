import datetime
import pytz
import random
import re

try :
    import Image
except ImportError:
    from PIL import Image

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor

from common.utilities import generate_md5_base64, path_to_url

from blog.models import Blog

SHA1_RE = re.compile('^[a-f0-9]{40}$')


def account_avatar_url(instance, filename):
    ext = filename.split('.')[-1]
    return './images/account/%s/avatar.%s' % (instance.user.id, ext)

class UserProfileManager(models.Manager):

    def create_profile(self, email, first_name, last_name, password, timezone='UTC'):
        username = generate_md5_base64(email)

        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        email_posting_key = sha_constructor(salt + email).hexdigest()
        mailbox_password = sha_constructor(salt + password).hexdigest()[:32]

        user = User.objects.create_user(username, email, password)
        UserProfile.objects.create(user=user, first_name=first_name, last_name=last_name, timezone=timezone, email_posting_key=email_posting_key, mailbox_password=mailbox_password)

        # Creating a mailbox
        if settings.CREATE_MAILBOX_AFTER_CREATE_USER:
            import requests

            r = requests.post('%s/mailboxes' % settings.MAILGUN_API_DOMAIN,
                auth=('api', settings.MAILGUN_API_KEY),
                data={
                    'mailbox': 'post-%s' % email_posting_key,
                    'password': mailbox_password
                }
            )

        return user


class UserProfile(models.Model):
    NOTIFICATION_FREQUENCY_CHOICES = (
        (0, 'None'  ),
        (-1, 'Immediately'), 
        (1, 'Daily' ), 
        (7, 'Weekly'), 
    )

    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200, blank=True, null=True, default='')
    office = models.CharField(max_length=200, blank=True, null=True, default='')
    avatar = models.ImageField(upload_to=account_avatar_url, null=True)

    email_posting_key = models.CharField(max_length=200, db_index=True, blank=True, null=True)
    mailbox_password = models.CharField(max_length=200, blank=True, null=True)

    timezone = models.CharField(max_length=200, default='UTC', choices=[(tz, tz) for tz in pytz.common_timezones])
    notification_viewed = models.DateTimeField(auto_now_add=True)
    
    notification_type = models.IntegerField(default=1, choices=NOTIFICATION_FREQUENCY_CHOICES)
    next_notified = models.DateField(null=True, default=datetime.datetime.now()+datetime.timedelta(days=1))

    def __unicode__(self):
        return '%s' % (self.get_full_name())

    class Meta:
        ordering = ['first_name', 'last_name']

    objects = UserProfileManager()

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_posting_email(self):
        return 'post-%s@%s' % (self.email_posting_key, settings.MAILGUN_EMAIL_DOMAIN) if self.email_posting_key else ''

    def get_avatar(self):
        if self.avatar:
            return self.avatar
        else:
            default_avatar = {
                'url': '%s/static/img/default_user.png' % '.',
                'path': 'static/img/default_user.png'
            }
            avatar = type('imageobj', (object,), default_avatar)
            return avatar

    def get_avatar_url(self):
        if self.avatar:
            return path_to_url(self.avatar.path)
        else:
            return None

    def status(self):
        if self.user.is_active:
            return 'active'
        else:
            if not self.user.last_login:
                return 'not-activate'
            else:
                return 'block'

    def update_view_notification(self):
        self.notification_viewed = datetime.now()
        self.save()

    def get_total_blog_loved(self):
        blogs_love_count = 0
        for blog in Blog.objects.filter(user=self.user):
            blogs_love_count += blog.love_set.count()

        return blogs_love_count


class UserInvitationManager(models.Manager):

    def create_invitation(self, email, invited_by):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        if isinstance(email, unicode):
            email = email.encode('utf-8')
        invitation_key = sha_constructor(salt + email).hexdigest()

        return self.create(email=email, invitation_key=invitation_key, invited_by=invited_by)

    def validate_invitation(self, invitation_key):
        if SHA1_RE.search(invitation_key):
            try:
                return self.get(invitation_key=invitation_key)
            except UserInvitation.DoesNotExist:
                return None
        else:
            return None

    def claim_invitation(self, invitation, first_name, last_name, password):
        user = UserProfile.objects.create_profile(invitation.email, first_name, last_name, password)
        invitation.delete()
        return user

class UserInvitation(models.Model):
    email = models.CharField(max_length=254)
    invitation_key = models.CharField(max_length=200, unique=True, db_index=True)
    invited = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(User)

    objects = UserInvitationManager()

    def create_invitation_request(self, base_url):
        email_context = {'settings':settings, 'base_url':base_url, 'invitation':self}

        text_email_body = render_to_string('account/email/invitation_email.txt', email_context)
        html_email_body = render_to_string('account/email/invitation_email.html', email_context)

        from requests import async

        return async.post('%s/messages' % settings.MAILGUN_API_DOMAIN,
            auth=('api', settings.MAILGUN_API_KEY),
            data={
                'from': settings.INVITATION_EMAIL_FROM,
                'to': self.email,
                'subject': 'You are invited to %s' % settings.SITE_NAME,
                'text':text_email_body,
                'html':html_email_body
            }
        )

    def __unicode__(self):
        return '%s has key %s' % (self.email, self.invitation_key)

"""
class UserResetPasswordManager(models.Manager):

    def create_reset_data(self, email):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        if isinstance(email, unicode):
            email = email.encode('utf-8')
        reset_key = sha_constructor(salt + email).hexdigest()

        return self.create(email=email, reset_key=reset_key)

    def validate_key(self, reset_key):
        if SHA1_RE.search(reset_key):
            try:
                return self.get(reset_key=reset_key)
            except UserResetPassword.DoesNotExist:
                return None
        else:
            return None

class UserResetPassword(models.Model):
    email = models.CharField(max_length=254)
    reset_key = models.CharField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = UserResetPasswordManager()

    def create_reset_request(self, base_url):
        email_context = {'settings':settings, 'base_url':base_url, 'reset_data':self}

        text_email_body = render_to_string('account/email/user_reset_email.txt', email_context)
        html_email_body = render_to_string('account/email/user_reset_email.html', email_context)

        from requests import async

        return async.post('%s/messages' % settings.MAILGUN_API_DOMAIN,
                          auth=('api', settings.MAILGUN_API_KEY),
                          data={
                              'from': settings.USER_RESET_EMAIL_FROM,
                              'to': self.email,
                              'subject': 'You have requested to reset your password in %s' % settings.SITE_NAME,
                              'text':text_email_body,
                              'html':html_email_body
                          }
        )
"""