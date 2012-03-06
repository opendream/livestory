from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.forms.models import model_to_dict

from account.forms import *
from account.models import *
from account.tasks import send_invite

from datetime import datetime

import hashlib
import os

import settings

# def account_login(request):
#     print 'xxx' , request.user.is_authenticated()
#     if request.user.is_authenticated():
#         return redirect(reverse('blog_home'))
#     from django.contrib.auth.views import login
#     return login(request, authentication_form=EmailAuthenticationForm)

@staff_member_required
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
            send_invite.delay(invite_list, request.build_absolute_uri('/'))
            
            # Set message
            if len(invite_list):
                messages.success(request, 'Sending email invite. you can see list of user invited in user managment.')
            if len(email_joined_list):
                messages.warning(request, 'Email user has joined : %s' % ', '.join(email_invalid_list))
            if len(email_invalid_list):
                messages.error(request, 'Email format incorect : %s' % ', '.join(email_invalid_list))

            
    else:
        form = AccountInviteForm()
        
    return render(request, 'account/account_invite.html', locals())
    
def account_activate(request, key):
    try:
        account_key = AccountKey.objects.get(key=key)
    except AccountKey.DoesNotExist:
        return render(request, 'account/account_key_error.html', locals())
    
    # Activate and login to user and redirect to update user profile chang password and orther
    # When user forgot password can go to this method and force login
    user = account_key.user
    param = {0: '?first=1', 1: '?forgot=1'}[int(user.is_active)]
    user.is_active = True
    
    password = hashlib.md5('%s%s' % (user.username, str(datetime.now()))).hexdigest()[0:10]
    user.set_password(password)
    
    user.save()
    
    user = authenticate(username=user.username, password=password)
    login(request, user)
    
    return redirect(reverse('account_profile_edit') + param)
    
@login_required 
def account_profile_edit(request):
    user = request.user
    account = user.get_profile()
    
    inst = model_to_dict(user)
    inst.update(model_to_dict(account))
    inst['password'] = ''
    param = request.GET.get('forgot') or request.GET.get('first')
    if param:
        inst['just_update_password'] = 1
    
    if request.method == 'POST':
        form = AccountProfileForm(request.POST)

        if form.is_valid():			
			password = form.cleaned_data.get('password')
			if password:
			    user.set_password(password)
			    user.save()
			    
			account.firstname = form.cleaned_data.get('firstname')
			account.lastname  = form.cleaned_data.get('lastname')
			# TODO: save avatar
			account.save()
						
			messages.success(request, 'Your profile has been save.')
			
    else:
        form = AccountProfileForm(inst)

    
    return render(request, 'account/account_profile_edit.html', locals())
