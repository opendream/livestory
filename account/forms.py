from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from account.models import Account

import pytz

class AccountInviteForm(forms.Form):
    invite = forms.CharField(widget=forms.Textarea)
    
class AccountProfileForm(forms.Form):
    firstname = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'input-xlarge'}), required=False)
    lastname = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'input-xlarge'}), required=False)
    
    just_update_password = forms.IntegerField(required=False)
    
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'input-xlarge'}, render_value=False), required=False)
    confirm_password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'input-xlarge'}, render_value=False), required=False)
    
    image = forms.ImageField(required=False)
    
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.common_timezones], required=False)
    
    class Meta:
		model = Account
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