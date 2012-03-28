# -*- encoding: utf-8 -*-
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.conf import settings

from celery.decorators import task
from smtplib import SMTPAuthenticationError

from account.models import AccountKey


from datetime import datetime

import hashlib

@task()
def send_invite(invite_list, base_url):
    subject = 'You are invited to %s' % settings.SITE_NAME
        
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

@task()
def send_forgot(email, base_url):
    subject = 'You have new activate link from %s' % settings.SITE_NAME
    
    key = hashlib.md5('key%s%s' % (email, str(datetime.now()))).hexdigest()[0:30]
    activate_link = '%s%s' % (base_url[0:-1], reverse('account_activate', args=[key]))
    
    body = render_to_string('account/account_send_forgot.html', {
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
        
        account_key.key = key
        account_key.save()
        return True
    except SMTPAuthenticationError:
        return False