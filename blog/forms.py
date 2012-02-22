from django import forms
from blog.models import Blog, Category

class BlogCreateForm(forms.ModelForm):
	title = forms.CharField(max_length=200, 
					widget=forms.TextInput(attrs={'class': 'input-xlarge'}))
	
	description = forms.CharField(required=False,
					widget=forms.Textarea(attrs={'rows': 5, 'class': 'input-xlarge'}))
	
	country = forms.CharField(widget=forms.TextInput(attrs={'class': 'span2', 'placeHolder': 'Country'}))

	city = forms.CharField(widget=forms.TextInput(attrs={'class': 'span2', 'placeHolder': 'City'}))

	mood = forms.IntegerField()
	private = forms.IntegerField()
	category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label=None)

	class Meta:
		model = Blog
		exclude = ('user', 'location', 'draft')

class BlogEditForm(forms.ModelForm):
	title = forms.CharField(max_length=200, 
					widget=forms.TextInput(attrs={'class': 'input-xlarge'}))

	image = forms.ImageField(required=False)
	
	description = forms.CharField(required=False,
					widget=forms.Textarea(attrs={'rows': 5, 'class': 'input-xlarge'}))
	
	country = forms.CharField(widget=forms.TextInput(attrs={'class': 'span2', 'placeHolder': 'Country'}))

	city = forms.CharField(widget=forms.TextInput(attrs={'class': 'span2', 'placeHolder': 'City'}))

	mood = forms.IntegerField()
	private = forms.IntegerField()
	category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label=None)

	class Meta:
		model = Blog
		exclude = ('user', 'location', 'draft')