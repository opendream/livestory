from django import forms
from blog.models import Category
from taggit.forms import TagField

from functions import check_temporary_blog_image, check_blog_image

class ModifyBlogForm(forms.Form):
    image_file_name = forms.CharField(max_length=500, widget=forms.HiddenInput(), required=False)

    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span4'}))
    description = forms.CharField(max_length=300, required=False, widget=forms.Textarea(attrs={'rows': 7, 'class': 'textcounter span4'}))
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

    def clean(self):
        #self.city
        #self.country
        pass

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

class BlogPlaceFilterForm(forms.Form):
    country = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off', 'class':'span2', 'placeHolder': 'Country'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'span2', 'placeHolder': 'City'}))