from django.contrib.auth import authenticate, login

from forms import *
from models import *

def account_login(request):
    from django.contrib.auth.views import login
    return login(request, authentication_form=EmailAuthenticationForm)