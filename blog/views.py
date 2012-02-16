from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse

from blog.models import *
from blog.forms import *

@login_required
def blog_create(request):
    action = reverse('blog_create')
    if request.method == 'POST':
        form = BlogCreateForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            image = handle_upload_file(request.FILES['image'], request)
            description = form.cleaned_data['description']
            mood = form.cleaned_data['mood']
            category = form.cleaned_data['category']
            location = Location.objects.get(pk=1) # hard code for test
            private = form.cleaned_data['private']
            draft = form.data['draft']
            blog = Blog(title=title, image=image, description=description, private=private, draft=draft, user=request.user, category=category, location=location)
            blog.save()
            return redirect('/blog/%s/view/' % blog.pk)
    else:
        form = BlogCreateForm()
        
    return render(request, 'blog/blog_form.html', locals())

@login_required
def blog_edit(request, blog_id):
    blog = Blog.objects.get(pk=blog_id)
    action = reverse('blog_edit', args=[blog_id])
    if request.method == 'POST':
        form = BlogCreateForm(request.POST, request.FILES)
        if form.is_valid():
            blog.title = form.cleaned_data['title']
            blog.description = form.cleaned_data['description']
            blog.mood = form.cleaned_data['mood']
            blog.category = form.cleaned_data['category']
            blog.location = Location.objects.get(pk=1) # hard code for test
            blog.private = form.cleaned_data['private']
            blog.draft = form.data['draft']
            blog.save()
            return redirect('/blog/%s/view/' % blog.pk)
    else:
        inst = blog.__dict__
        inst['private'] = int(inst['private'])
        inst['category'] = blog.category
        form = BlogCreateForm(inst)
        
    return render(request, 'blog/blog_form.html', locals())

def blog_view(request, blog_id):
    blog = Blog.objects.get(pk=blog_id)
    return render(request, 'blog/blog_view.html', locals())

def handle_upload_file(f, instance):
    filepath = blog_image_path(instance, f.name)
    destination = open(filepath, 'wd+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return blog_image_url(instance, f.name)