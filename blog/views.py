import os
import settings

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.utils import simplejson as json

try:
    from PIL import Image, ImageOps
except ImportError:
    import Image
    import ImageOps

from account.models import Account
from blog.models import *
from blog.forms import *

from location.models import Location

@login_required
def blog_create(request):
    action = reverse('blog_create')
    if request.method == 'POST':
        form = BlogCreateForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.description = form.cleaned_data.get('description')[:300]
            blog.user = request.user
            blog.draft = bool(int(form.data.get('draft')))
            blog.location = blog_save_location(form.cleaned_data.get('country'), form.cleaned_data.get('city'))
            blog.image.save('test.png', request.FILES['image'], save=False)
            # blog.image = handle_upload_file(request.FILES['image'], request)
            blog.save()
            return redirect('/blog/%s/edit' % blog.pk)
    else:
        form = BlogCreateForm()

    context = {
        'form': form,
        'moods': MOOD_CHOICES,
        'visibilities': PRIVATE_CHOICES,
        'is_draft': True
    }
    return render(request, 'blog/blog_form.html', context)

@login_required
def blog_edit(request, blog_id):
    blog = Blog.objects.get(pk=blog_id)
    location = Location.objects.get(pk=blog.location_id)
    action = reverse('blog_edit', args=[blog_id])
    if request.method == 'POST':
        form = BlogEditForm(request.POST, request.FILES)
        if form.is_valid():
            blog.title = form.cleaned_data.get('title')
            blog.description = form.cleaned_data.get('description')[:300]
            blog.mood = form.cleaned_data.get('mood')
            blog.category = form.cleaned_data.get('category')
            blog.location = blog_save_location(form.cleaned_data.get('country'), form.cleaned_data.get('city'))
            blog.private = form.cleaned_data.get('private')

            # If previous is draft, you can draft it again.
            if blog.draft:
                blog.draft = bool(int(form.data.get('draft')))
            
            # There is image uploaded.
            if request.FILES.get('image'):
                image = request.FILES.get('image')
                # Remove old image.
                if os.path.isfile(blog.image.path):
                    os.remove(blog.image.path)
                # Save new image.
                blog.image.save(image.name, image, save=False)
            
            blog.save()
            return redirect('/blog/%s/edit' % blog.pk)
    else:
        defaults = {
            'title': blog.title,
            'description': blog.description,
            'country': location.country,
            'city': location.city,
            'mood': str(blog.mood),
            'category': blog.category,
            'private': str(int(blog.private))
        }
        form = BlogEditForm(defaults)

    context = {
        'form': form,
        'moods': MOOD_CHOICES,
        'visibilities': PRIVATE_CHOICES,
        'image_path': blog.get_image_url(),
        'is_draft': blog.draft,
        'blog': blog
    }
        
    return render(request, 'blog/blog_form.html', context)

def blog_view(request, blog_id):
    blog = Blog.objects.get(pk=blog_id)
    if blog.private:
        # TODO redirect to access denied
        pass
    love_path = '/blog/%s/love/'
    love_class = 'love'
    try:
        love = Love.objects.get(user=request.user, blog=blog)
        love_path = '/blog/%s/unlove/'
        love_class = 'unlove'
    except Love.DoesNotExist:
        pass

    context = {
        'blog': blog,
        'profile': request.user.get_profile(),
        'love_path': love_path % blog_id,
        'love_class': love_class,
        'love_count': Love.objects.filter(blog=blog).count()
    }
    return render(request, 'blog/blog_view.html', context)

@login_required
def blog_love(request, blog_id):
    data = {'love': 0}
    try:
        Love.objects.get(user=request.user, blog__id=blog_id)
    except Love.DoesNotExist:
        try:
            blog = Blog.objects.get(pk=blog_id)
            love = Love(user=request.user, blog=blog)
            love.save()
            data['love'] = 1
        except Blog.DoesNotExist:
            # TODO page not found
            pass
    if request.is_ajax():
        return HttpResponse(json.dumps(data), mimetype="application/json")
    else:
        return redirect('/blog/%s/view' % blog_id)

@login_required
def blog_unlove(request, blog_id):
    data = {'love': 0}
    try:
        love = Love.objects.get(user=request.user, blog__id=blog_id)
        love.delete()
        data['love'] = -1
    except Love.DoesNotExist:
        pass
    if request.is_ajax():
        return HttpResponse(json.dumps(data), mimetype="application/json")
    else:
        return redirect('/blog/%s/view' % blog_id)

def blog_save_location(country, city):
    try:
        location = Location.objects.get(country=country, city=city)
    except Location.DoesNotExist:
        location = Location(country=country, city=city, lat=0, lng=0)
        location.save()
    return location

def handle_upload_file(f, instance):
    filepath = blog_image_path(instance, f.name)
    destination = open(filepath, 'wd+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return blog_image_url(instance, f.name)