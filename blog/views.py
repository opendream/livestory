import datetime
import os
import shutil
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.utils import simplejson as json
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.servers.basehttp import FileWrapper
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import UploadedFile
from django.views.decorators.cache import cache_page
from django.db.models import Count

from blog.models import *
from blog.forms import *
from statistic.models import BlogViewHit, BlogViewSummary
from notification.models import Notification

from functions import remove_temporary_blog_image, remove_blog_image

from location.models import Location
from common.scour import Scour
from common import ucwords, get_page_range
from taggit.models import TaggedItem


def blog_home(request):
    if request.user.is_authenticated():
        return redirect(reverse('blog_popular'))
    else:
        return render(request, 'blog/blog_static.html')

@login_required
def blog_popular(request):
    _width = 960
    _height = 660
    scour = Scour(nx=10, ny=9, width=_width, height=_height, gap=10)
    
    borders = scour.get_rect()
    
    blogs = list(Blog.objects.filter(
                            draft=False, 
                            trash=False
                        ).annotate(
                            love_count=Count('love')
                        ).select_related(
                            depth=1
                        ).order_by(
                            '-love_count', 
                            '-view_summary__totalcount'
                        )[:len(borders)])

    for i, blog in enumerate(blogs):
        blog.position = borders[i]

    return render(request, 'blog/blog_home.html', { 'blogs': blogs,
                                                    'scour_width': _width, 
                                                    'scour_height': _height })

@login_required
def blog_manage(request, section):
    blogs = Blog.objects.filter(user=request.user).annotate(num_loves=Count('love'))

    if request.GET.get('sort') and request.GET.get('order'):
        sort = request.GET.get('sort')
        order = request.GET.get('order')
        if sort == 'num_views':
            sort = 'view_summary__totalcount'
        if order == 'desc':
            blogs = blogs.order_by('-%s' % sort)
        else:
            blogs = blogs.order_by('%s' % sort)
    else:
        order = 'desc'
        blogs = blogs.order_by('-published')

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

    pager = Paginator(blogs, 20)
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


@login_required
def blog_trash(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if blog.user.id != request.user.id and not request.user.is_staff:
        return render(request, '403.html', status=403)

    blog.trash = True
    blog.save()

    from_section = request.GET.get('from')

    if from_section == 'published':
        redirect_url_name ='blog_manage_published'
    elif from_section == 'draft':
        redirect_url_name = 'blog_manage_draft'
    else:
        redirect_url_name = 'blog_manage'

    messages.success(request, 'Moved blog to trash successfully. [ <a href="%s?redirect=%s">Undo</a> ]' % (reverse('blog_restore', args=[blog.id]), reverse(redirect_url_name)))
    return redirect(redirect_url_name)


@login_required
def blog_restore(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if blog.user.id != request.user.id and not request.user.is_staff:
        return render(request, '403.html', status=403)

    blog.trash = False
    blog.save()

    redirect_to = request.GET.get('redirect')
    if redirect_to:
        return redirect(redirect_to)

    return redirect('blog_manage_trash')


@login_required
def blog_create(request):
    blog_image_file = None

    if request.method == 'POST':
        form = ModifyBlogForm(None, request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            location, created = Location.objects.get_or_create(city__iexact=city,
                                                               country__iexact=country, 
                                                               defaults = {'country': country,'city': city})
            from django.core.files import File

            blog = Blog(
                title = form.cleaned_data['title'],
                description = form.cleaned_data['description'],
                user = request.user,
                location = location,
                draft = bool(int(request.POST.get('draft'))),
                allow_download = form.cleaned_data['allow_download'],
                image = File(open('%s%s' % (settings.TEMP_BLOG_IMAGE_ROOT, form.cleaned_data['image_file_name']))),
                category = form.cleaned_data['category'],
                mood = form.cleaned_data['mood'],
            )

            publish = bool(int(request.POST.get('publish')))
            if publish:
                blog.published = datetime.datetime.now()

            blog.save()
            blog.save_tags(form.cleaned_data['tags'])

            remove_temporary_blog_image(form.cleaned_data['image_file_name'])

            messages.success(request, 'Blog post created. <a class="btn btn-success" href="%s">View post</a>' % reverse('blog_view', args=[blog.id]))
            return redirect(reverse('blog_edit', args=[blog.id]))

        else:
            file_name = request.POST.get('image_file_name')
            if file_name:
                blog_image_file = '%s%s' % (settings.TEMP_BLOG_IMAGE_ROOT, file_name)

    else:
        form = ModifyBlogForm(None, initial={'allow_download': True})

    context = {
        'page_title': 'Add New Story',
        'form': form,
        'moods': MOOD_CHOICES,
        'visibilities': PRIVATE_CHOICES,
        'is_draft': True,
        'blog_image_file': blog_image_file,
    }

    return render(request, 'blog/blog_form.html', context)


@csrf_exempt
def blog_create_by_email(request):
    if request.method == 'POST':
        prefix, separator, therest = request.POST.get('sender').partition('-')
        posting_key, separator, email_domain = therest.rpartition('@')

        try:
            user_profile = UserProfile.objects.get(email_posting_key=posting_key)
            user = user_profile.user
        except UserProfile.DoesNotExist:
            return HttpResponse('Sender not found')

        title = request.POST.get('Subject')
        description = request.POST.get('stripped-text') # Text without signature

        if not title or not description:
            return HttpResponse('Email subject or body is empty')

        if request.FILES:
            keys = request.FILES.keys()
            key_with_max_size = keys[0]
            max_size = request.FILES[keys[0]].size
            for key in keys[1:]:
                if request.FILES[key].size > max_size:
                    key_with_max_size = key
                    max_size = request.FILES[key].size

            image_file = request.FILES[key_with_max_size]
        
            if not image_file:
                return HttpResponse('Image attachment not found')

            (root, file_name, file_ext) = split_filepath(image_file.name)
            if not file_ext.lower() in ('jpg', 'jpeg', 'png', 'gif'):
                return HttpResponse('Image format is not supported')

        else:
            return HttpResponse('Image attachment not found')

        form_data = {
            'title':title,
            'description':description,
            'country':'England',
            'city':'Oxford',
            'mood':99, # Moodless
            'private':0,
            'category':22, # No category
            'tags':None
        }

        form = BlogCreateForm(form_data, request.FILES)

        if not form.is_valid():
            return HttpResponse('Server error')

        blog = form.save(commit=False)
        blog.user = user
        blog.draft = False
        blog.allow_download = False
        blog.location = blog_save_location(form.cleaned_data.get('country'), form.cleaned_data.get('city'))
        blog.published = datetime.datetime.now()
        blog.save()

        BlogViewSummary.objects.get_or_create(blog=blog)

        uploading_file = UploadedFile(image_file)

        (root, file_name, file_ext) = split_filepath(image_file.name)
        blog.image.save('%s.%s' % (uuid.uuid4(), file_ext), uploading_file.file)
        blog.save()

    return HttpResponse('')


@login_required
def blog_edit(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    (root, name ,ext) = split_filepath(blog.image.path)
    image_file_name = '%s.%s' % (name, ext)

    if not request.user.is_staff and not request.user.id == blog.user.id:
        return render(request, '403.html', status=403)
    elif blog.trash:
        raise Http404

    if request.method == 'POST':
        form = ModifyBlogForm(blog, request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            location, created = Location.objects.get_or_create(city__iexact=city,
                                                               country__iexact=country, 
                                                               defaults = {'country': country,'city': city})
            from django.core.files import File

            blog.title = form.cleaned_data['title']
            blog.description = form.cleaned_data['description']
            blog.location = location
            blog.draft = bool(int(request.POST.get('draft', 0)))
            blog.allow_download = form.cleaned_data['allow_download']
            blog.category = form.cleaned_data['category']
            blog.mood = form.cleaned_data['mood']
            blog.trash = bool(int(request.POST.get('trash', 0)))
            #stamp a published date
            publish = bool(int(request.POST.get('publish', 0)))
            if publish:
                blog.published = datetime.datetime.now()

            new_image_file = form.cleaned_data['image_file_name']
            if new_image_file and (new_image_file != image_file_name):
                remove_blog_image(blog)
                blog.image = File(open('%s%s' % (settings.TEMP_BLOG_IMAGE_ROOT, form.cleaned_data['image_file_name'])))

            blog.save()
            blog.save_tags(form.cleaned_data['tags'])

            messages.success(request, 'Blog post updated. <a class="btn btn-success" href="%s">View post</a>' % reverse('blog_view', args=[blog.id]))

            if blog.trash:
                return redirect('blog_view', blog_id=blog.id)

            return redirect(reverse('blog_edit', args=[blog.id]))

    else:

        form = ModifyBlogForm(blog, initial={
            'title': blog.title,
            'description': blog.description,
            'country': blog.location.country,
            'city': blog.location.city,
            'mood': blog.mood,
            'image_file_name':image_file_name,
            'category': blog.category,
            'private': str(int(blog.private)),
            'allow_download': blog.allow_download,
            'tags': blog.get_tags()
        })

    context = {
        'page_title': 'Edit Blog',
        'blog': blog,
        'form': form,
        'is_draft': blog.draft,
        'moods': MOOD_CHOICES,
        'visibilities': PRIVATE_CHOICES,
        'blog_image_file':blog.image.path,
    }

    return render(request, 'blog/blog_form.html', context)


@login_required
def blog_view(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    
    if not request.user.is_staff and ((not request.user.is_authenticated() and blog.private) or (blog.draft and blog.user.id != request.user.id)):
        return render(request, '403.html', status=403)
    elif blog.trash and not request.user.is_staff and not request.user == blog.user:
        raise Http404

    # Save view hit and update stat summary
    session_key = request.session.session_key
    if not blog.hit_stat.filter(sessionkey=session_key):
        blog.hit_stat.create(sessionkey=session_key)

    love_path = '/blog/%s/love/'
    button_type = 'love'
    if blog.love_set.filter(user=request.user):
        love_path = '/blog/%s/unlove/'
        button_type = 'unlove'

    love_set = blog.love_set.all().order_by('-datetime', '-id')
    loved_users = []
    for l in love_set:
        loved_users.append(l.user.get_profile())
    
    comments = Comment.objects.select_related('user__profile', 'blog').filter(blog=blog).order_by('post_date');
    context = {
        'blog': blog,
        'comments': comments,
        'profile': blog.user.get_profile(),
        'love_path': love_path % blog_id,
        'button_type': button_type,
        'love_count': blog.love_set.count(),
        'loved_users': loved_users,

        'max_items': 7,
        'CAN_SHARE_SN': settings.CAN_SHARE_SN,
    }
    return render(request, 'blog/blog_view.html', context)

@login_required
def blog_download(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if (blog.draft and request.user != blog.user) or not blog.allow_download or (blog.private and not request.user.is_authenticated()):
        return render(request, '403.html', status=403)
    
    response = HttpResponse(FileWrapper(blog.image.file), mimetype='application/force-download')    
    response['Content-Disposition'] = 'attachment; filename=%s-%s.%s' % (blog.published.strftime('%Y%m%d') , blog.id, blog.image.name.split('.')[-1])
    
    # Nofify
    if request.user.is_authenticated() and request.user != blog.user:
        Notification(subject=request.user, action=2, blog=blog).save()
    
    return response


@login_required
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
            return HttpResponse(json.dumps(data))
        else:
            return redirect('/blog/%s/view' % blog_id)
    except Blog.DoesNotExist:
        if request.is_ajax():
            return HttpResponse(json.dumps({'status': 404}))
        else:
            raise Http404


@login_required
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
            return HttpResponse(json.dumps(data))
        else:
            return redirect('/blog/%s/view' % blog_id)
    except Blog.DoesNotExist:
        if request.is_ajax():
            return HttpResponse(json.dumps({'status': 404}))
        else:
            raise Http404


@login_required
def blog_all(request, title='Latest Stories', filter={}, filter_text={}, url=None, param='', color='blue'):
    items = Blog.objects.filter(draft=False, 
                                trash=False
                            ).select_related(
                                depth=1
                            ).filter(
                                **filter
                            ).order_by('-published')
    
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


@login_required
def blog_mood(request, mood):
    title = ucwords(mood)
    try: 
        fmood = dict([(m[1], m[0]) for m in MOOD_CHOICES])[title]
    except KeyError:
        #render empty page
        return render(request, 'blog/blog_list_empty.html', {'filter': {'mood': mood}})

    return blog_all(request, title, 
        {'mood': fmood}, 
        {'mood': mood}, 
        reverse('blog_mood', args=[mood]), 
        color='purple')


@login_required
def blog_category(request, category):
    try: 
        fcategory = Category.objects.get(code=category)
    except Category.DoesNotExist:
        #render empty page
        return render(request, 'blog/blog_list_empty.html', {'filter': {'category': category}})
        
    title = fcategory.name

    return blog_all(request, title, 
        {'category': fcategory}, 
        {'category': category}, 
        reverse('blog_category', args=[category]), 
        color='pink')

@login_required
def blog_place_empty(request):
    return render(request, 'blog/blog_list_empty.html', {'filter': {'location': '-'}})

@login_required
def blog_place(request):
    country = request.GET.get('country') or ''
    city = request.GET.get('city') or ''
        
    country = ' '.join(country.split())
    city = ' '.join(city.split())
    
    title_country = country if country else 'All Countries'
    title_city = city if city else 'All Cities'
    title = '%s, %s' % (title_country, title_city)
    
    locations = Location.objects.all()
    if country:
        locations = locations.filter(country__icontains=country)
    if city:
        locations = locations.filter(city__icontains=city)

    filter = {'location__in': locations}
    if not locations.count():
        title = '%s (Miss match)'% title
        
    param = 'country=%s&city=%s' % (country, city)
        
    return blog_all(request, title, filter, 
                        {'location': {'country': country, 'city': city}}, 
                        reverse('blog_place'), param, color='yellow')


@login_required
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


@login_required
def blog_manage_bulk(request):
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
    else:
        raise Http404


def blog_save_image(image_path, blog):
    directory, name = os.path.split(image_path)
    real_path = blog_image_url(blog, 'blog_%s.jpg' % blog.id)
    directory, name = os.path.split(real_path)
    if not os.path.exists(directory.replace('./', settings.MEDIA_ROOT, 1)):
        os.makedirs(directory.replace('./', settings.MEDIA_ROOT, 1))
    final_path = real_path.replace('./', settings.MEDIA_ROOT, 1)
        
    shutil.copy2(image_path, final_path)
    return real_path


@login_required
def blog_search(request):
    """Search blogs by title and description"""
    keyword = request.REQUEST.get("keyword", '')

    context = {'title': 'keyword: %s' % keyword,
               'keyword': keyword,
               'param': 'keyword=%s' % keyword}

    keyword = keyword.strip()
    if keyword:

        blogs = Blog.objects.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword)
        ).order_by('-published')

        pager = Paginator(blogs, 8)
        p = request.GET.get('page') or 1

        try:
            pagination = pager.page(p)
            blogs = pagination.object_list
        except (PageNotAnInteger, EmptyPage):
            raise Http404

        p = int(p)

        page_range = get_page_range(pagination)

        context.update({'blogs': blogs,
                        'has_pager': len(page_range) > 1,
                        'pagination': pagination,
                        'page': p,
                        'pager': pager,
                        'page_range': page_range,})

    return render(request, 'blog/blog_search.html', context)

def list_blog_comment(request, blog_id):
    b = get_object_or_404(Blog, id=blog_id)
    return render(request, 'blog/blo')

def add_blog_comment(request, blog_id):
    b = get_object_or_404(Blog, id=blog_id)
    if request.method == 'POST':
        f = BlogCommentForm(request.POST)
        if f.is_valid():
            b.comment_set.create(
                comment=f.cleaned_data['comment'],
                user=request.user,
                blog=b
            )
    return redirect('blog_view', blog_id)

# Static page
def blog_about(request):
    return render(request, 'about.html')

def blog_term(request):
    return render(request, 'term.html')

def blog_howto(request):
    return render(request, 'howto.html')
