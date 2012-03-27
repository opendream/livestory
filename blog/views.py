import os
from django.conf import settings
import shutil

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.utils import simplejson as json
from django.db.models import Count, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from account.models import Account
from blog.models import *
from blog.forms import *
from statistic.models import History, ViewCount
from notification.models import Notification

from location.models import Location
from common.scour import Scour
from common.views import check_file_exists
from common.templatetags.common_tags import cache_path
from common import ucwords, get_page_range
from taggit.models import TaggedItem

def blog_home(request):
    if not request.user.is_authenticated() and settings.PRIVATE:
        return render(request, 'blog/blog_static.html')
    
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
        WHERE NOT blog_blog.draft AND NOT blog_blog.trash \
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
    
    context = {
        'scour_width': scour_width,
        'scour_height': scour_height,
        'blogs': blogs,
        'rects': rects,
    }
    
    return render(request, 'blog/blog_home.html', context)

def blog_manage(request, section=None):
    if not request.user.is_authenticated():
        return render(request, '403.html', status=403)

    blogs = Blog.objects.all().annotate(num_loves=Count('love'))

    if request.GET.get('sort') and request.GET.get('order'):
        sort = request.GET.get('sort')
        order = request.GET.get('order')
        if sort == 'num_views':
            sort = 'viewcount__totalcount'
        if order == 'desc':
            blogs = blogs.order_by('-%s' % sort)
        else:
            blogs = blogs.order_by('%s' % sort)
    else:
        order = 'desc'
        blogs = blogs.order_by('-created')

    if not request.user.is_staff:
        blogs = blogs.filter(user=request.user)

    blog_all = blogs.filter(trash=False)
    blog_published = blogs.filter(draft=False, trash=False)
    blog_draft = blogs.filter(draft=True, trash=False)
    blog_trash = blogs.filter(trash=True)

    if section == 'published':
        url = reverse('blog_manage_published')
    elif section == 'draft':
        url = reverse('blog_manage_draft')
    elif section == 'trash':
        url = reverse('blog_manage_trash')
    else:
        url = reverse('blog_manage')

    can_restore = False
    if section == 'published':
        blogs = blog_published
    elif section == 'draft':
        blogs = blog_draft
    elif section == 'trash':
        blogs = blog_trash
        can_restore = True
    else:
        blogs = blog_all

    pager = Paginator(blogs, 10)
    p = request.GET.get('page') or 1

    try:
        pagination = pager.page(p)
        blogs = pagination.object_list
    except (PageNotAnInteger, EmptyPage):
        raise Http404

    p = int(p)

    page_range = get_page_range(pagination)

    context = {
        'blogs': blogs,
        'can_restore': can_restore,
        'num_all': blog_all.count(),
        'num_published': blog_published.count(),
        'num_draft': blog_draft.count(),
        'num_trash': blog_trash.count(),
        'has_pager': len(page_range) > 1,
        'pagination': pagination,
        'page': p,
        'pager': pager,
        'page_range': page_range,
        'url': url,
        'order': order == 'desc' and 'asc' or 'desc',
        'section': section,
    }

    return render(request, 'blog/blog_manage.html', context)

def blog_manage_published(request):
    return blog_manage(request, 'published')

def blog_manage_draft(request):
    return blog_manage(request, 'draft')

def blog_manage_trash(request):
    return blog_manage(request, 'trash')

def blog_trash(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        if not request.user.is_authenticated() or (blog.user.id != request.user.id and not request.user.is_staff):
            return render(request, '403.html', status=403)

        blog.trash = True
        blog.save()

        section = request.GET.get('section')
        if section:
            if section == 'published':
                return redirect(reverse('blog_manage_published'))
            elif section == 'draft':
                return redirect(reverse('blog_manage_draft'))
        return redirect(reverse('blog_manage'))
    except Blog.DoesNotExist:
        raise Http404

def blog_restore(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        if not request.user.is_authenticated() or (blog.user != request.user and not request.user.is_staff):
            return render(request, '403.html', status=403)

        blog.trash = False
        blog.save()
        return redirect(reverse('blog_manage_trash'))
    except Blog.DoesNotExist:
        raise Http404


def blog_create(request):
    if not request.user.is_authenticated():
        return render(request, '403.html', status=403)
    
    action = reverse('blog_create')
    image_path = ''
    imagefield_error = False
    location_error = False

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
            try:
                blog.location = blog_save_location(form.cleaned_data.get('country'), form.cleaned_data.get('city'))
                blog.save()
                
                blog.save_tags(form.data.get('tags'))
                
                blog.image = blog_save_image(image_path, blog)
                blog.save()

                ViewCount.objects.create(blog=blog)
                
                # There is image uploaded.
                if image_path.split('/')[-2] == 'temp':
                    cpath = cache_path(blog.image.path)
                    if os.path.exists(cpath):
                        shutil.rmtree(cpath)
            
                messages.success(request, 'Blog post created. <a href="%s">View post</a>' % reverse('blog_view', args=[blog.id]))
                return redirect(reverse('blog_edit', args=[blog.id]))
            except Location.DoesNotExist:
                location_error = True
                
    else:
        form = BlogCreateForm()

    context = {
        'page_title': 'Add New Blog',
        'form': form,
        'moods': MOOD_CHOICES,
        'visibilities': PRIVATE_CHOICES,
        'is_draft': True,
        'image_path': image_path,
        'imagefield_error': imagefield_error,
        'location_error': location_error
    }
    return render(request, 'blog/blog_form.html', context)

def blog_edit(request, blog_id):
    try:
        blog = Blog.objects.get(pk=blog_id)
        
        if not request.user.is_staff and (not request.user.is_authenticated() or request.user.id != blog.user.id):
            return render(request, '403.html', status=403)
        elif blog.trash:
            return render(request, '403.html', status=403)
        
        location = Location.objects.get(pk=blog.location_id)
        action = reverse('blog_edit', args=[blog_id])
        image_path = blog.image.path
        imagefield_error = False
        location_error = False

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
                blog.save_tags(form.data.get('tags'))
                try:
                    blog.location = blog_save_location(form.cleaned_data.get('country'), form.cleaned_data.get('city'))
                    blog.private = form.cleaned_data.get('private')

                    # If previous is draft, you can draft it again.
                    if blog.draft:
                        blog.draft = bool(int(form.data.get('draft')))
                
                    # There is image uploaded.
                    if image_path.split('/')[-2] == 'temp':
                        cpath = cache_path(blog.image.path)
                        blog.image.delete()
                        if os.path.exists(cpath):
                            shutil.rmtree(cpath)
                        # Save new image.
                        blog.image = blog_save_image(image_path, blog)
                
                    blog.save()
                    messages.success(request, 'Blog post updated. <a href="%s">View post</a>' % reverse('blog_view', args=[blog.id]))
                    return redirect(reverse('blog_edit', args=[blog.id]))
                    
                except Location.DoesNotExist:
                    location_error = True
        else:
            defaults = {
                'title': blog.title,
                'description': blog.description,
                'country': location.country,
                'city': location.city,
                'mood': str(blog.mood),
                'category': blog.category,
                'private': str(int(blog.private)),
                'tags': blog.get_tags()
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
            'imagefield_error': imagefield_error,
            'location_error': location_error,
        }
        return render(request, 'blog/blog_form.html', context)
    except Blog.DoesNotExist:
        raise Http404

def blog_view(request, blog_id):
    try:
        blog = Blog.objects.get(pk=blog_id)
        blog.viewcount.update()
        if not request.user.is_staff and ((not request.user.is_authenticated() and blog.private) or (blog.draft and blog.user.id != request.user.id)):
            return render(request, '403.html', status=403)

        # History.objects.create(user=request.user, blog=blog)
            
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
        
        love_set = blog.love_set.all().order_by('-datetime', '-id')
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
            'max_items': 7,
            'CAN_SHARE_SN': settings.CAN_SHARE_SN,
        }
        return render(request, 'blog/blog_view.html', context)
    except Blog.DoesNotExist:
        raise Http404

def blog_love(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        if not request.user.is_authenticated() or (blog.user.id != request.user.id and blog.draft):
            return render(request, '403.html', status=403)
        
        data = {'love': 0, 'type': 'love', 'status': 200}
        try:
            # Check if this user has ever loved this blog post.
            Love.objects.get(user=request.user, blog__id=blog_id)
            data['love'] = 1
            data['type'] = 'unlove'
        except Love.DoesNotExist:
            # Add new love
            love = Love(user=request.user, blog=blog)
            love.save()
            data['love'] = 1
            data['type'] = 'unlove'
            # Nofify
            if request.user != blog.user:
                Notification(subject=request.user, action=1, blog=blog).save()
        
        if request.is_ajax():
            return HttpResponse(json.dumps(data), mimetype="application/json")
        else:
            return redirect('/blog/%s/view' % blog_id)
    except Blog.DoesNotExist:
        if request.is_ajax():
            return HttpResponse(json.dumps({'status': 404}), mimetype="application/json")
        else:
            raise Http404

def blog_unlove(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        if not request.user.is_authenticated() or (blog.user.id != request.user.id and blog.draft):
            return render(request, '403.html', status=403)
        
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
    except Blog.DoesNotExist:
        if request.is_ajax():
            return HttpResponse(json.dumps({'status': 404}), mimetype="application/json")
        else:
            raise Http404
            
def blog_all(request, title='Latest Stories', filter={}, filter_text={}, url=None, param='', color='blue'):
    items = Blog.objects.filter(draft=False, trash=False)
    if not request.user.is_authenticated():
        items = items.filter(private=False)
    
    items = items.filter(**filter)
    items = items.order_by('-created')
    
    pager = Paginator(items, 8)
    p = request.GET.get('page') or 1
    
    try:
        pagination = pager.page(p)
        blogs = pagination.object_list
    except (PageNotAnInteger, EmptyPage):
        raise Http404
    
    p = int(p)
    
    filter = filter_text if filter_text else filter
    
    if not url:
        url = reverse('blog_all')
    
    page_range = get_page_range(pagination)
    context = {
        'title': title,
        'blogs': blogs,
        'has_pager': len(page_range) > 1,
        'pagination': pagination,
        'page': p,
        'pager': pager,
        'page_range': page_range,
        'filter': filter,
        'url': url,
        'param': param,
        'color': color,
    }
    
    return render(request, 'blog/blog_list.html', context)
    
def blog_mood(request, mood):
    title = ucwords(mood)
    try: 
        fmood = dict([(m[1], m[0]) for m in MOOD_CHOICES])[title]
    except KeyError:
        raise Http404
    return blog_all(request, title, {'mood': fmood}, {'mood': mood}, reverse('blog_mood', args=[mood]), color='purple')
    
def blog_category(request, category):
    try: 
        fcategory = Category.objects.get(code=category)
    except Category.DoesNotExist:
        raise Http404
        
    title = fcategory.name
    
    return blog_all(request, title, {'category': fcategory}, {'category': category}, reverse('blog_category', args=[category]), color='pink')
    
def blog_place(request):
    country = request.GET.get('country') or ''
    city = request.GET.get('city') or ''
        
    country = ucwords(country)
    city = ucwords(city)
    
    title_country = country if country else 'All Countries'
    title_city = city if city else 'All Cities'
    title = '%s, %s' % (title_country, title_city)
    
    locations = Location.objects.all()
    if country and city:
        locations = locations.filter(country=country, city=city)
    elif country:
        locations = locations.filter(country=country)
    elif city:
        locations = locations.filter(city=city)
        
    filter = {}
    if (country or city) and locations.count():
        filter = {'location__in': locations}
    elif (country or city) and not locations.count():
        title = '%s (Miss match)'% title
        filter = {'location__in': locations}
    
    param = 'country=%s&city=%s' % (country, city)
        
    return blog_all(request, title, filter, {'location': {'country': country, 'city': city}}, reverse('blog_place'), param, color='yellow')
    
def blog_tags(request):
    tags = request.GET.get('tags')
    if not tags or not Blog.objects.filter(tags__name=tags).count():
        raise Http404
        
    title = 'Tagged with "%s"' % tags
    
    return blog_all(request, title, {'tags__name': tags}, {'tags': tags}, reverse('blog_tags'), color='grey')

def blog_save_location(country, city):
    try:
        location = Location.objects.get(country=ucwords(country), city=ucwords(city))
    except Location.DoesNotExist:
        location = Location(country=country, city=city)
        location.save()
    # For unittest maybe create duplicate location
    except Location.MultipleObjectsReturned:
        location = Location.objects.filter(country=ucwords(country), city=ucwords(city)).order_by('-id')[0]
        
    return location

def blog_manage_bulk(request):
    if not request.user.is_authenticated() or request.method == 'GET':
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        blog_ids = request.POST.getlist('blog_id')
        operation = request.POST.get('op')
        section = request.GET.get('section')
        for blog_id in blog_ids:
            blog = Blog.objects.get(id=blog_id)
            if blog.user == request.user or request.user.is_staff:
                if operation == 'trash':
                    blog.trash = True
                    blog.save()
                elif operation == 'restore':
                    blog.trash = False
                    blog.save()
                elif operation == 'delete' and blog.trash:
                    blog.delete()
        if section == 'published':
            return redirect(reverse('blog_manage_published'))
        elif section == 'draft':
            return redirect(reverse('blog_manage_draft'))
        elif section == 'trash':
            return redirect(reverse('blog_manage_trash'))
        return redirect(reverse('blog_manage'))

def blog_save_image(image_path, blog):
    directory, name = os.path.split(image_path)
    real_path = blog_image_url(blog, 'blog_%s.jpg' % blog.id)
    directory, name = os.path.split(real_path)
    if not os.path.exists(directory.replace('./', settings.MEDIA_ROOT, 1)):
        os.makedirs(directory.replace('./', settings.MEDIA_ROOT, 1))
    final_path = real_path.replace('./', settings.MEDIA_ROOT, 1)
        
    shutil.copy2(image_path, final_path)
    return real_path
