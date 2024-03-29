import datetime

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
from django.db.models import Q, Count
from django.forms.models import model_to_dict
from django.http import HttpResponseForbidden

from common.decorators import user_is_staff
from common.templatetags.common_tags import *
from common.utilities import get_page_range

from account.forms import *
from account.models import *


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
@user_is_staff
def account_invite(request):
    if request.method == 'POST':
        form = UserInvitationForm(request.POST)

        if form.is_valid():
            invitation_requests = []
            invalid_emails = []
            exist_emails = []

            for email in form.cleaned_data['emails'].split(','):
                email = email.strip()

                if not email:
                    continue

                try:
                    validate_email(email)
                except ValidationError:
                    invalid_emails.append(email)
                    continue

                # check user that already exists
                try:
                    User.objects.get(email=email)
                except User.DoesNotExist:
                    pass
                else:
                    exist_emails.append(email)
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
            if exist_emails:
                messages.warning(request, 'Email user has joined : %s' % ', '.join(exist_emails))
            return redirect('account_invite')

    else:
        form = UserInvitationForm()

    return render(request, 'account/account_invite.html', locals())


@login_required
def account_profile_create(request):
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        form = UserProfileCreationForm(request.POST)
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
        form = UserProfileCreationForm()

    return render(request, 'account/account_profile_create.html', {'form': form})

@login_required
def account_profile_edit(request):
    user = request.user
    account = user.get_profile()

    inst = model_to_dict(user)
    inst.update(model_to_dict(account))
    inst['password'] = ''
    param = request.GET.get('forgot') or request.GET.get('activate')
    if param:
        inst['just_update_password'] = 1

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():         
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
                user.save()
            
            account.first_name = form.cleaned_data.get('first_name')
            account.last_name = form.cleaned_data.get('last_name')
            account.job_title = form.cleaned_data.get('job_title')
            account.office = form.cleaned_data.get('office')
            account.timezone = form.cleaned_data.get('timezone')
            if account.notification_type != int(form.cleaned_data.get('notification_type')):
                account.notification_type = form.cleaned_data.get('notification_type')
                if int(account.notification_type) > 0:
                    account.next_notified = datetime.date.today() + datetime.timedelta(days=int(account.notification_type))
                else:
                    account.next_notified = None

            #save avatar
            image = form.cleaned_data.get('image')
            if (image):
                account.avatar.save(image.name, image, save=False)
                            
            account.save()
                        
            messages.success(request, 'Your profile has been saved.')

    else:
        form = UserProfileForm(inst)

    return render(request, 'account/account_profile_edit.html', locals())

@login_required
@user_is_staff
def user_profile_edit(request, pk):
    """ 
    Provide edit user profile method for staff level user 
    """
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    usr = get_object_or_404(User, pk=pk)
    account = usr.get_profile()

    if request.method == 'POST':
        form = UserProfileForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data.get('password')
            active = form.cleaned_data.get('is_active')
            if password:
                usr.set_password(password)
            usr.is_active = active
            usr.save()

            account.first_name = form.cleaned_data.get('first_name')
            account.last_name = form.cleaned_data.get('last_name')
            account.job_title = form.cleaned_data.get('job_title')
            account.office = form.cleaned_data.get('office')
            account.timezone = form.cleaned_data.get('timezone')
            # TODO: save avatar
            account.save()

            messages.success(request, 'User profile has been updated.')

    else:
        user_data = model_to_dict(usr)
        user_data.update(model_to_dict(account))
        user_data['password'] = ''
        form = UserProfileForm(user_data)

    return render(request, 'account/user_profile_edit.html', locals())

@login_required
@user_is_staff
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
            sort = ['first_name', 'last_name']
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

@login_required
def account_profile_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    blogs = user.blog_set.filter(draft=False, trash=False).select_related(depth=1)
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

@login_required
@user_is_staff
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

@login_required
def account_profile_search(request):
    form = AccountSearchForm(request.GET) if 'account_keywords' in request.GET else AccountSearchForm()

    keyword = request.GET.get('account_keywords', '').strip()
    if keyword and form.is_valid():
        accounts_list = UserProfile.objects.filter(Q(first_name__icontains=keyword) |
                                                  Q(last_name__icontains=keyword) |
                                                  Q(office__icontains=keyword))
    else:
        accounts_list = UserProfile.objects.all()

    ordering = request.GET.get('ordering')
    if ordering == 'country':
        accounts_list = accounts_list.order_by('office')
    elif ordering == 'most_photos':
        accounts_list = accounts_list.annotate(total_blog=Count('user__blog')).order_by('-total_blog')
    elif ordering == 'most_loves':
        accounts_list = accounts_list.annotate(total_love=Count('user__blog__love')).order_by('-total_love')
    else:
        ordering == None

    paginator = Paginator(accounts_list, 8)
    page = request.GET.get('page') or 1
    try:
        accounts = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        raise Http404

    context = {
        'accounts'  : accounts,
        'form'      : form,
        'keyword'   : keyword,
        'ordering'  : ordering,
        'paginator' : paginator,
        'page'      : page,
    }

    return render(request, 'account/account_profile_search.html', context)
