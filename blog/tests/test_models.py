from blog.models import Blog
from django.test import TestCase
from tests import factory

class TestBlog(TestCase):
    def setUp(self):
        self.category = factory.create_category()
        self.user = factory.create_user()

        self.location = factory.create_location() 

    def test_unicode(self):
        blog = Blog(title='Icecream') 
        blog.user = self.user
        blog.category = self.category
        blog.location = self.location
        blog.save()
        printed_unicode = '(%s) Icecream' % blog.id
        self.assertEqual(printed_unicode, blog.__unicode__())


