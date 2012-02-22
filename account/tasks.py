from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.core.mail import send_mail

from celery.decorators import task
from smtplib import SMTPAuthenticationError

from account.models import AccountKey

import settings

@task()
def send_invite(invite_list):
    subject = 'Invite join %s' % settings.SITE_NAME
        
    for invite in invite_list:
        
        email = invite['email']
        activate_link = invite['activate_link']
        
        
        body = render_to_string('account/account_send_invite.html', {'site_name': settings.SITE_NAME, 'activate_link': activate_link})
        
        account_key = AccountKey.objects.get(user__email=email)
        try:
            send_mail(subject, body, settings.EMAIL_HOST_USER, [email], fail_silently=False)
            account_key.can_send_mail = True
            account_key.save()
        except SMTPAuthenticationError:
            account_key.can_send_mail = False
            account_key.save()