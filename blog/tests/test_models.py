from django.contrib.auth.models import User
from django.test import TestCase
from blog.models import Blog, Category, Location

class TestBlog(TestCase):
    def setUp(self):
        self.category = Category(name = 'Food', code = 'f')
        self.category.save()

        username = 'testuser'
        email = 'test@example.com'
        password = 'testuser'
        self.user = User.objects.create_user(username, email, password)

        self.location = Location(country = 'Thailand', city = 'Bangkok')
        self.location.lat = '100.00'
        self.location.lng = '13.00'
        self.location.save()

    def test_unicode(self):
        blog = Blog(title='Icecream') 
        blog.user = self.user
        blog.category = self.category
        blog.location = self.location
        blog.save()
        printed_unicode = '(%s) Icecream' % blog.id
        self.assertEqual(printed_unicode, blog.__unicode__())


