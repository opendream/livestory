from account.models import Account, AccountKey
from blog.models import Blog, Category, Location, Love
from django.contrib.auth.models import User
from django.core.files.base import File as DjangoFile

import hashlib
from datetime import datetime

def create_user(username='testuser', email='test@example.com', password='testuser', firstname='John', lastname='Doe', has_image=False):
    user = User.objects.create_user(username, email, password)
    account = Account(firstname=firstname, lastname=lastname, user=user)
    if has_image:
        account.image = DjangoFile(open('static/tests/avatar.png'), 'avatar.png')
    account.save()
    
    key = hashlib.md5('key%s%s' % (user.email, str(datetime.now()))).hexdigest()[0:30]
    account_key = AccountKey(key=key, user=user)
    account_key.save()
        
    return user

def create_category(name = 'Food', code = 'f'):
    category = Category(name=name, code=code)
    category.save()
    return category
    
def create_location():
    location = Location(country = 'Thailand', city = 'Bangkok')
    location.lat = '100.00'
    location.lng = '13.00'
    location.save()
    return location

def create_blog(title='Icecream', user = None, category = None, location = None, mood=1):
    user = user or create_user()
    category = category or create_category()
    location = location or create_location()
    
    blog = Blog(title = title) 
    blog.user = user
    blog.category = category
    blog.location = location
    blog.mood = mood
    blog.save()
    
    return blog
    
