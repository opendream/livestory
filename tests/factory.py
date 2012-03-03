from blog.models import Blog, Category, Location
from django.contrib.auth.models import User

def create_user():
    username = 'testuser'
    email = 'test@example.com'
    password = 'testuser'
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

