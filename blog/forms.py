import urllib

from django import forms
from django.conf import settings
from django.utils import simplejson as json

from functions import check_temporary_blog_image, check_blog_image

from blog.models import Category
from taggit.forms import TagField


class ModifyBlogForm(forms.Form):
    image_file_name = forms.CharField(max_length=500, widget=forms.HiddenInput())

    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span4'}))
    description = forms.CharField(max_length=300, required=False, widget=forms.Textarea(attrs={'rows': 7, 'class': 'textcounter span4'}))
    related_url = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': 'span4'}))
    download_url = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': 'span4'}))
    country = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off', 'class':'span2', 'placeHolder': 'Country'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'span2', 'placeHolder': 'City'}))

    mood = forms.IntegerField()
    private = forms.IntegerField()
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label=None)
    allow_download = forms.BooleanField(required=False)
    tags = TagField(required=False)

    def __init__(self, blog=None, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.blog = blog

    def clean_image_file_name(self):
        image_file_name = self.cleaned_data.get('image_file_name')

        if not self.blog:
            if not check_temporary_blog_image(image_file_name):
                raise forms.ValidationError('Uploading image is missing, please upload it again.')

            return image_file_name
        else:
            if not check_blog_image(self.blog):
                raise forms.ValidationError('Uploaded image is missing, please upload it again.')
            return image_file_name

    def clean_allow_download(self):
        return self.cleaned_data.get('allow_downlod') if self.is_allow_user_to_download_photo else False

    @property
    def is_allow_user_to_download_photo(self):
        return getattr(settings, 'ALLOW_USER_TO_DOWNLOAD_PHOTO', False)

class BlogPlaceFilterForm(forms.Form):
    country = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off', 'class':'span2', 'placeHolder': 'Country'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'span2', 'placeHolder': 'City'}))

class BlogCommentForm(forms.Form):
    comment = forms.CharField(
        max_length = 300, 
        required   = True, 
        widget     = forms.Textarea(attrs={'rows': 7, 'class': 'span4'})
    )