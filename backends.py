import re
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain

class EmailAuthenticationBackend(ModelBackend):
    """Authenticate using email only"""
    def authenticate(self, email=None, password=None):
        if email_re.search(email):
            user = User.objects.filter(email__iexact=email)
            if user.count() > 0:
                user = user[0]

                if user.check_password(password):
                    return user

        return None