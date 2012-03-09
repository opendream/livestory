import os
import settings
import shutil

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.utils import simplejson as json
from django.db.models import Count, Sum

from account.models import Account
from blog.models import *
from blog.forms import *

from location.models import Location
from common.scour import Scour
from common.views import check_file_exists
from common.templatetags.common_tags import cache_path

def blog_home(request):
    scour_width = 960
    scour_height = 660
    scour = Scour(10, 9, scour_width, scour_height, 10)
    
    borders = scour.get_rect()
    
    # Ask crosalot when you has question with long query.
    blogs = Blog.objects.raw(
    "SELECT tmp.bid AS id, SUM(tmp.rate) AS love_rate \
     FROM ( \
        SELECT blog_blog.id AS bid, COALESCE(blog_love.id, 0) AS rate \
        FROM blog_blog \
        LEFT JOIN blog_love \
        ON blog_blog.id = blog_love.blog_id \
    ) AS tmp \
    GROUP BY tmp.bid \
    ORDER BY love_rate DESC")[0: len(borders)]
    
    blogs = list(blogs)
    
    rects = []
    for i, rect in enumerate(borders):
        try:
            blog = blogs[i]
        except IndexError:
            blog = None
                
        rects.append({
            'blog': blog, 
            'rect': rect, 
            'widthxheight': '%sx%s' % (rect['width'], rect['height']),
            'placement': 'right' if rect['left'] <= scour_width/2 else 'left'
        })

    return render(request, 'blog/blog_home.html', locals())

def blog_manage(request):
    blogs = Blog.objects.all()
    context = {
        'blogs': blogs
    }
    return render(request, 'blog/blog_manage.html', context)

def blog_create(request):
    if not request.user.is_authenticated():
        return render(request, '403.html', status=403)
    
    action = reverse('blog_create')
    image_path = ''
    imagefield_error = False

    if request.method == 'POST':
        form = BlogCreateForm(request.POST, request.FILES)

        # Check image field upload.
        image_path = form.data.get('image_path')
        if not image_path or not os.path.exists(image_path):
            image_path = ''
            imagefield_error = True

        if form.is_valid() and not imagefield_error:
            blog = form.save(commit=False)
            blog.description = form.cleaned_data.get('description')[:300]
            blog.user = request.user
            blog.draft = bool(int(form.data.get('draft')))
            blog.location = blog_save_location(form.cleaned_data.get('country'), form.cleaned_data.get('city'))
            blog.save()
            
            blog.image = blog_save_image(image_path, blog)
            blog.save()
            
            messages.success(request, 'Blog post created. <a href="/blog/%s/view/">View post</a>' % blog.id)
            return redirect('/blog/%s/edit' % blog.pk)
    else:
        form = BlogCreateForm()

    context = {
        'page_title': 'Add New Blog',
        'form': form,
        'moods': MOOD_CHOICES,
        'visibilities': PRIVATE_CHOICES,
        'is_draft': True,
        'image_path': image_path,
        'imagefield_error': imagefield_error
    }
    return render(request, 'blog/blog_form.html', context)

@login_required
def blog_edit(request, blog_id):
    try:
        blog = Blog.objects.get(pk=blog_id)
        location = Location.objects.get(pk=blog.location_id)
        action = reverse('blog_edit', args=[blog_id])
        image_path = blog.image.path
        imagefield_error = False

        if request.method == 'POST':
            form = BlogCreateForm(request.POST, request.FILES)

            # Check image field upload.
            image_path = form.data.get('image_path')
            if not image_path or not os.path.exists(image_path):
                imagefield_error = True

            if form.is_valid() and not imagefield_error:
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
                if image_path.split('/')[-2] == 'temp':
                    cpath = cache_path(blog.image.path)
                    blog.image.delete()
                    shutil.rmtree(cpath)

                # Save new image.
                blog.image = blog_save_image(image_path, blog)
                
                blog.save()
                messages.success(request, 'Blog post updated. <a href="/blog/%s/view/">View post</a>' % blog.id)
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
            form = BlogCreateForm(defaults)

        context = {
            'page_title': 'Edit Post',
            'form': form,
            'moods': MOOD_CHOICES,
            'visibilities': PRIVATE_CHOICES,
            'is_draft': blog.draft,
            'blog': blog,
            'image_path': image_path,
            'imagefield_error': imagefield_error
        }
        return render(request, 'blog/blog_form.html', context)
    except Blog.DoesNotExist:
        # TODO handle blog not found
        pass

def blog_view(request, blog_id):
    try:
        blog = Blog.objects.get(pk=blog_id)
        if blog.private:
            # TODO redirect to access denied
            pass
        love_path = '/blog/%s/love/'
        button_type = 'love'
        try:
            # If this blog is already loved by current logged in user
            love = Love.objects.get(user=request.user, blog=blog)
            love_path = '/blog/%s/unlove/'
            button_type = 'unlove'
        except (Love.DoesNotExist, TypeError):
            # Do nothing. Use default love_path and button_type.
            pass
        
        love_set = blog.love_set.all().order_by('-datetime')
        loved_users = []
        for l in love_set:
            loved_users.append(l.user.get_profile())

        context = {
            'blog': blog,
            'profile': blog.user.get_profile(),
            'love_path': love_path % blog_id,
            'button_type': button_type,
            'love_count': Love.objects.filter(blog=blog).count(),
            'loved_users': loved_users,
            'max_items': 7
        }
        return render(request, 'blog/blog_view.html', context)
    except Blog.DoesNotExist:
        # Page not found
        # TODO
        return HttpResponse('blog post not found')

@login_required
def blog_love(request, blog_id):
    data = {'love': 0, 'type': 'love', 'status': 200}
    try:
        # Check if this user has ever loved this blog post.
        Love.objects.get(user=request.user, blog__id=blog_id)
        data['love'] = 1
        data['type'] = 'unlove'
    except Love.DoesNotExist:
        try:
            # Add new love
            blog = Blog.objects.get(pk=blog_id)
            love = Love(user=request.user, blog=blog)
            love.save()
            data['love'] = 1
            data['type'] = 'unlove'
        except Blog.DoesNotExist:
            # Blog post not found
            # TODO
            pass
    
    if request.is_ajax():
        return HttpResponse(json.dumps(data), mimetype="application/json")
    else:
        return redirect('/blog/%s/view' % blog_id)

@login_required
def blog_unlove(request, blog_id):
    data = {'love': 0, 'type': 'unlove', 'status': 200}
    try:
        # Remove love if exists.
        love = Love.objects.get(user=request.user, blog__id=blog_id)
        love.delete()
        data['love'] = -1
        data['type'] = 'love'
    except Love.DoesNotExist:
        # Never love this blog post before.
        data['love'] = -1
        data['type'] = 'love'
    
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
    # For unittest maybe create duplicate location
    except Location.MultipleObjectsReturned:
        location = Location.objects.filter(country=country, city=city).order_by('-id')[0]
        
    return location

def blog_save_image(image_path, blog):
    directory, name = os.path.split(image_path)
    real_path = blog_image_url(blog, 'blog_%s.jpg' % blog.id)
    directory, name = os.path.split(real_path)
    if not os.path.exists(directory.replace('./', settings.MEDIA_ROOT, 1)):
        os.makedirs(directory.replace('./', settings.MEDIA_ROOT, 1))
    final_path = real_path.replace('./', settings.MEDIA_ROOT, 1)
        
    shutil.copy2(image_path, final_path)
    return real_path
