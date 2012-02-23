from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _


class AccountInviteForm(forms.Form):
    invite = forms.CharField(widget=forms.Textarea)
    
class AccountProfileForm(forms.Form):
    firstname = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'input-xlarge'}), required=False)
    lastname = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'input-xlarge'}), required=False)
    
    just_update_password = forms.IntegerField(required=False)
    
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'input-xlarge'}, render_value=False), required=False)
    confirm_password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'input-xlarge'}, render_value=False), required=False)
    
    
    
    def clean_password(self):
        if self.cleaned_data.get('just_update_password'):
            raise forms.ValidationError(_("Password must be update"))
            
        return self.cleaned_data['password']
        
    def clean_confirm_password(self):
        if self.cleaned_data.get('just_update_password'):
            raise forms.ValidationError(_("Password must be confirm"))
            
        password         = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        
        if password != confirm_password:
            raise forms.ValidationError(_("Password not match"))
        return confirm_password

class EmailAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    email/password logins.
    """
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_('Please enter a correct username and password. Note that both fields are case-sensitive.'))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_('This account is inactive.'))
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(
                _('Your Web browser doesn\'t appear to have cookies enabled. '
                  'Cookies are required for logging in.'))

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache