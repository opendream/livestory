from django import forms
from blog.models import Blog, Category
from blog.models import Location

class BlogCreateForm(forms.ModelForm):
	image = forms.ImageField(required=False)

	title = forms.CharField(max_length=200, 
					widget=forms.TextInput(attrs={'class': 'input-xlarge'}))
	
	description = forms.CharField(max_length=300, required=False,
					widget=forms.Textarea(attrs={'rows': 7, 'class': 'textcounter input-xlarge'}))
	
	country = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off', 'class':'span2', 'placeHolder': 'Country'}))

	city = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'span2', 'placeHolder': 'City'}))

	mood = forms.IntegerField()
	private = forms.IntegerField()
	category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label=None)

	class Meta:
		model = Blog
		exclude = ('user', 'location', 'draft')
