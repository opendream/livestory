from django import forms
from blog.models import blog_image_url, Category

class BlogCreateForm(forms.Form):
    
    MOOD_CHOICES    = ((0, 'Happy'), (1, 'Love'), (2, 'Sad'), (3, 'Boring'))
    PRIVATE_CHOICES = ((False, 'No'), (True, 'Yes'))
    DRAFT_CHOICES   = ((False, 'No'), (True, 'Yes'))
    
    title       = forms.CharField(max_length=200)
    image       = forms.ImageField()
    description = forms.CharField(required=False)
    mood        = forms.IntegerField()
    private     = forms.IntegerField()
    category    = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label=None)