# -*- encoding: utf-8 -*-
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from celery.decorators import task
from smtplib import SMTPAuthenticationError

from account.models import AccountKey

from django.conf import settings

@task()
def send_invite(invite_list, base_url):
    subject = 'Invite join %s' % settings.SITE_NAME
        
    for invite in invite_list:
        
        email = invite['email']
        activate_link = invite['activate_link']
        
        body = render_to_string('account/account_send_invite.html', {
            'site_name': settings.SITE_NAME,
            'site_logo': settings.SITE_LOGO,
            'site_logo_email': settings.SITE_LOGO_EMAIL,
            'organization_name': settings.ORGANIZATION_NAME,
            'contact_email': settings.CONTACT_EMAIL,
            'base_url': base_url,
            'activate_link': activate_link
        })
                
        account_key = AccountKey.objects.get(user__email=email)
        try:            
            msg = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [email])
            msg.content_subtype = 'html'
            msg.send()
            
            account_key.can_send_mail = True
            account_key.save()
        except SMTPAuthenticationError:
            account_key.can_send_mail = False
            account_key.save()