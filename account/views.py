from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import model_to_dict
from django.http import HttpResponseForbidden

from common import get_page_range
from common.templatetags.common_tags import *

from account.forms import *
from account.models import *
from account.tasks import send_invite, send_forgot

from datetime import datetime

import hashlib
import os

from django.conf import settings

# def account_login(request):
#     print 'xxx' , request.user.is_authenticated()
#     if request.user.is_authenticated():
#         return redirect(reverse('blog_home'))
#     from django.contrib.auth.views import login
#     return login(request, authentication_form=EmailAuthenticationForm)

def auth_login(request):
    from django.contrib.auth.views import login
    return login(request, authentication_form=EmailAuthenticationForm)


def account_activate(request, key):
    invitation = UserInvitation.objects.validate_invitation(key)

    if request.method == 'POST':
        form = UserActivationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password']
            user = UserInvitation.objects.claim_invitation(invitation, first_name, last_name, password)

            user = authenticate(email=user.email, password=password)
            login(request, user)

            return redirect('blog_home')

    else:
        form = UserActivationForm()

    return render(request, 'account/account_activate.html', {'form':form, 'invitation':invitation})


@login_required
def account_invite(request):
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        form = UserInvitationForm(request.POST)

        if form.is_valid():
            invitation_requests = []
            invalid_emails = []

            for email in form.cleaned_data['emails'].split(','):
                email = email.strip()

                if not email:
                    continue

                try:
                    validate_email(email)
                except ValidationError:
                    invalid_emails.append(email)
                    continue

                try:
                    invitation = UserInvitation.objects.get(email=email)
                except UserInvitation.DoesNotExist:
                    if not User.objects.filter(email=email).exists():
                        invitation = UserInvitation.objects.create_invitation(email, request.user)
                    else:
                        invitation = None

                if invitation:
                    invitation_requests.append(invitation.create_invitation_request(request.build_absolute_uri('/')[:-1]))

            from requests import async
            responses = async.map(invitation_requests)

            # Set message
            if invitation_requests:
                messages.success(request, 'Sending invitation email(s).')
            if invalid_emails:
                messages.warning(request, 'The following email(s) is invalid and has not been sent: %s' % ', '.join(invalid_emails))

            return redirect('account_invite')

    else:
        form = UserInvitationForm()

    return render(request, 'account/account_invite.html', locals())


@login_required
def account_profile_create(request):
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        form = ProfileCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password1']
            timezone = form.cleaned_data['timezone']

            user = UserProfile.objects.create_profile(email, first_name, last_name, password, timezone)

            messages.success(request, "New profile created.")
            return redirect('account_manage_users')

        else:
            messages.error(request, "Please correct error(s) below.")
    else:
        form = ProfileCreationForm()

    return render(request, 'account/account_profile_create.html', {'form': form})


def account_profile_edit(request):
    if not request.user.is_authenticated():
        return render(request, '403.html', status=403)

    user = request.user
    account = user.get_profile()

    inst = model_to_dict(user)
    inst.update(model_to_dict(account))
    inst['password'] = ''
    param = request.GET.get('forgot') or request.GET.get('activate')
    if param:
        inst['just_update_password'] = 1

    if request.method == 'POST':
        form = AccountProfileForm(request.POST, request.FILES)

        if form.is_valid():         
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
                user.save()
            
            account.firstname = form.cleaned_data.get('firstname')
            account.lastname  = form.cleaned_data.get('lastname')
            account.timezone  = form.cleaned_data.get('timezone')

            #save avatar
            image = form.cleaned_data.get('image')
            if (image):
                account.image.save(image.name, image, save=False)
                            
            account.save()
                        
            messages.success(request, 'Your profile has been save.')

    else:
        form = AccountProfileForm(inst)

    return render(request, 'account/account_profile_edit.html', locals())


def user_profile_edit(request, pk):
    """ 
    Provide edit user profile method for staff level user 
    """
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    usr = get_object_or_404(User, pk=pk)
    account = usr.get_profile()

    if request.method == 'POST':
        form = AccountProfileForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data.get('password')
            active = form.cleaned_data.get('is_active')
            if password:
                usr.set_password(password)
            usr.is_active = active
            usr.save()

            account.firstname = form.cleaned_data.get('firstname')
            account.lastname = form.cleaned_data.get('lastname')
            account.timezone = form.cleaned_data.get('timezone')
            # TODO: save avatar
            account.save()

            messages.success(request, 'User profile has been updated.')

    else:
        user_data = model_to_dict(usr)
        user_data.update(model_to_dict(account))
        user_data['password'] = ''
        form = AccountProfileForm(user_data)

    return render(request, 'account/user_profile_edit.html', locals())


def account_forgot(request):

    if request.method == 'POST':
        pass
    else:
        pass

    return render(request, 'registration/password_')
    form = AccountForgotForm()
    email_error = False
    success = False

    if request.POST:
        form = AccountForgotForm(request.POST)
        if form.is_valid():
            request_email = form.cleaned_data.get('email')
            if send_forgot(request_email, request.build_absolute_uri('/')):
                success = 'Check your email and click the activate link for join us again.'
            else:
                email_error = 'Send email error. Please, try again later.'

    context = {
        'form': form,
        'email_error': email_error,
        'success': success,
        }
    return render(request, 'account/account_forgot.html', context)


def account_manage_users(request):
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    users = User.objects.all()

    if request.GET.get('sort') and request.GET.get('order'):
        sort = request.GET.get('sort')
        order = request.GET.get('order')

        if sort == 'role':
            sort = ['is_staff']
        elif sort == 'name':
            sort = ['userprofile__first_name', 'userprofile_last_name']
        else:
            sort = [sort]

        if order == 'desc':
            users = users.order_by(*['-%s' % sort_col for sort_col in sort])
        else:
            users = users.order_by(*['%s' % sort_col for sort_col in sort])
    else:
        order = 'desc'
        users = users.order_by('-date_joined')

    pager = Paginator(users, 20)
    p = request.GET.get('page') or 1

    try:
        pagination = pager.page(p)
        users = pagination.object_list
    except (PageNotAnInteger, EmptyPage):
        raise Http404

    p = int(p)

    page_range = get_page_range(pagination)

    context = {
        'users': users,
        'has_pager': len(page_range) > 1,
        'pagination': pagination,
        'page': p,
        'pager': pager,
        'page_range': page_range,
        'order': order == 'desc' and 'asc' or 'desc',
        }

    return render(request, 'account/account_manage_users.html', context)


def account_profile_view(request, pk):
    if not request.user.is_authenticated():
        return render(request, '403.html', status=403)

    user = get_object_or_404(User, pk=pk)
    blogs = user.blog_set.all()
    blog_count = blogs.count()

    pager = Paginator(blogs, 8)
    p = request.GET.get('page') or 1

    try:
        pagination = pager.page(p)
        blogs = pagination.object_list
    except (PageNotAnInteger, EmptyPage):
        raise Http404

    p = int(p)

    page_range = get_page_range(pagination)

    context = {'blogs': blogs,
               'has_pager': len(page_range) > 1,
               'pagination': pagination,
               'page': p,
               'pager': pager,
               'page_range': page_range,
               'viewed_user': user,
               'blog_count': blog_count}

    return render(request, 'account/account_profile_view.html', context)


def account_manage_bulk(request):
    if not request.user.is_staff or request.method == 'GET':
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        user_ids = request.POST.getlist('user_id')
        operation = request.POST.get('op')
        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            if operation == 'block':
                user.is_active = False
                user.save()
            elif operation == 'unblock':
                user.is_active = True
                user.save()
        return redirect(reverse('account_manage_users'))

