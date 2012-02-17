from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, redirect, render
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from account.forms import *
from account.models import *
from account.tasks import send_invite

from datetime import datetime

import hashlib

def account_login(request):
    from django.contrib.auth.views import login
    return login(request, authentication_form=EmailAuthenticationForm)

def account_invite(request):
    if request.method == 'POST':
        form = AccountInviteForm(request.POST)
        if form.is_valid():
            
            email_exist = [user.email for user in User.objects.all()]
            
            invite_dummy = form.cleaned_data['invite'].replace(' ', '').split(',')
            
            invite_list = []
            email_invalid_list = []
            email_joined_list = []
            for email in invite_dummy:
                try:
                    validate_email(email)
                    
                    key = hashlib.md5('key%s%s' % (email, str(datetime.now()))).hexdigest()[0:30]
                    activate_link = request.build_absolute_uri(reverse('account_activate', args=[key]))
                    
                    # Case first time invite user
                    if email not in email_exist:
                        
                        password = hashlib.md5('%s%s' % (email, str(datetime.now()))).hexdigest()[0:10]
                        
                        user = User.objects.create_user(email, email, password)
                        user.is_active = False
                        user.save()
                        
                        account = Account(user=user)
                        account.save()
                        
                        account_key = AccountKey(user=user, key=key)
                        account_key.save()
                        
                        invite_list.append({'email': user.email, 'activate_link': activate_link})
                    
                    # Case second or more time invite user
                    else:
                        account_key = AccountKey.objects.get(user__email=email)
                        
                        if not account_key.user.is_active:
                            user = account_key.user
                            
                            account_key.key = key
                            account_key.save()
                    
                            invite_list.append({'email': user.email, 'activate_link': activate_link})
                        # Case user joined
                        else:
                            email_joined_list.append(email)
                    
                except ValidationError:
                    email_invalid_list.append(email)
            
            # Send email backend with celery
            send_invite.delay(invite_list)
            
    else:
        form = AccountInviteForm()
        
    return render(request, 'account/account_invite.html', locals())
    
def account_activate(request, key):
    pass