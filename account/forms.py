from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.forms import fields
from django.utils.translation import ugettext_lazy as _

from account.models import UserProfile, UserInvitation

import pytz

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
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
            raise forms.ValidationError(_('Your Web browser doesn\'t appear to have cookies enabled. Cookies are required for logging in.'))

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class UserInvitationForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea)


class UserActivationForm(forms.Form):
    first_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span3'}))
    last_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span3'}))
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'span3'}))
    confirm_password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'span3'}))

    def clean_confirm_password(self):
        password1 = self.cleaned_data.get('password', '')
        password2 = self.cleaned_data['confirm_password']
        if password1 != password2:
            raise forms.ValidationError(_('The two password fields didn\'t match.'))
        return password2

class UserProfileForm(forms.Form):
    first_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span3'}))
    last_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span3'}))
    job_title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span3'}), required=False)
    office = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span3'}), required=False)
    
    just_update_password = forms.IntegerField(required=False)
    
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'span3'}, render_value=False), required=False)
    confirm_password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'span3'}, render_value=False), required=False)
    
    image = forms.ImageField(required=False)
    
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.common_timezones], required=False)
    
    is_active = forms.BooleanField(required=False)

    class Meta:
		model = UserProfile
		#exclude = ('user', 'location', 'draft')
    
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

class UserProfileCreationForm(forms.Form):
    email = forms.EmailField(max_length=254, widget=forms.TextInput(attrs={'class': 'span3'}))
    first_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span3'}))
    last_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span3'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'span3'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'span3'}))
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.common_timezones], required=False, initial='UTC')

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if UserInvitation.objects.filter(email=email).exists():
            raise forms.ValidationError('Create user invitation has already been sent to this email address.')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('There is another user already using this email.')

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError(_('The two password fields didn\'t match.'))
        return password2

class UserProfileForgotForm(forms.Form):
    email = forms.EmailField(max_length=255, widget=forms.TextInput(attrs={'class': 'span3'}))

    def __init__(self, *args, **kwargs):
        super(UserProfileForgotForm, self).__init__(*args, **kwargs)
        self.fields['email'].error_messages['required'] = 'Please enter email address.'

    def clean_email(self):
        req_email = self.cleaned_data['email']
        try:
            User.objects.get(username=req_email)
        except User.DoesNotExist:
            raise forms.ValidationError(_('Your email miss match.'))
        return req_email

class AccountSearchForm(forms.Form):
    account_keywords = forms.CharField(
                            required = True, 
                            max_length = 500, 
                            error_messages = {'required': 'Search keyword is required.'}
                        )
