from django.contrib.auth import authenticate, login

from account.forms import *
from account.models import *

def account_login(request):
    from django.contrib.auth.views import login
    return login(request, authentication_form=EmailAuthenticationForm)

def account_invite(request):
    pass