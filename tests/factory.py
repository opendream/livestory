from blog.models import Blog, Category, Location, Love
from django.contrib.auth.models import User

def create_user(username=None, email=None, password=None):
    username = username or 'testuser'
    email = email or 'test@example.com'
    password = password or 'testuser'
    return User.objects.create_user(username, email, password)

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

def create_blog(title='Icecream', user = None, category = None, location = None, love=0):
    user = user or create_user()
    category = category or create_category()
    location = location or create_location()
    
    blog = Blog(title = title) 
    blog.user = user
    blog.category = category
    blog.location = location
    blog.save()
    
    return blog
    
