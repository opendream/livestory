import hashlib
from datetime import datetime

from django.contrib.auth.models import User
from django.core.files.base import File as DjangoFile

from account.models import UserProfile, UserInvitation
from blog.models import Blog, Category, Location, Love
from notification.models import Notification

def create_user(username='testuser', email='test@example.com', password='testuser', first_name='John', last_name='Doe', job_title='scrum master', office='opendream', has_image=False, timezone='Asia/Bangkok'):
    user = User.objects.create_user(username, email, password)
    account = UserProfile(first_name=first_name, last_name=last_name, user=user, job_title=job_title, office=office, timezone=timezone)
    if has_image:
        account.image = DjangoFile(open('static/tests/avatar.png'), 'avatar.png')
    account.save()

    return user

def create_category(name = 'Food', code = 'f'):
    category = Category(name=name, code=code)
    category.save()
    return category
    
def create_location(country='Thailand', city='Bangkok', lat='100.00', lng='13.00'):
    location = Location(country=country, city=city, lat=lat, lng=lng)
    location.save()
    return location

def create_blog(title='Icecream', user = None, category = None, location = None, mood=1, private=True, draft=False, tags='hastags,foo,bar', trash=False, allow_download=True):
    user = user or create_user()
    category = category or create_category()
    location = location or create_location()
    
    blog = Blog(title = title) 
    blog.user = user
    blog.category = category
    blog.location = location
    blog.mood = mood
    blog.private = private
    blog.draft = draft
    blog.trash = trash
    blog.allow_download = allow_download
    blog.save()
    blog.save_tags(tags)
    blog.image.save('blog_%s.jpg' % blog.id, DjangoFile(open('static/tests/blog.jpg'), 'blog.jpg'))
    blog.published = datetime.now()
    blog.save()
    
    return blog

def create_notification(subject, action, blog, dt):
    notification = Notification(subject=subject, action=action, blog=blog, datetime=dt)
    notification.save()
    return notification

def rm_user(id):
    try:
        user = User.objects.get(id=id)
        try:
            UserProfile.objects.get(user=user).delete()
        except UserProfile.DoesNotExist:
            pass
        user.delete()
    except User.DoesNotExist:
        pass

    try:
        shutil.rmtree('%sblog/%s' % (settings.IMAGE_ROOT, id))
    except:
        pass
    try:
        shutil.rmtree('%scache/images/blog/%s' % (settings.MEDIA_ROOT, id))
    except:
        pass
        
    try:
        shutil.rmtree('%saccount/%s' % (settings.IMAGE_ROOT, id))
    except:
        pass
    try:
        shutil.rmtree('%scache/images/account/%s' % (settings.MEDIA_ROOT, id))
    except:
        pass
