from django.contrib.auth.models import User
from django.test import TestCase
from blog.models import Blog
from tests import factory

class TestBlogManagement(TestCase):
    def setUp(self):
        user = factory.create_user()
        category = factory.create_category()
        location = factory.create_location()
        factory.create_blog('Sprite', user, category, location)
        factory.create_blog('Coke', user, category, location)
        factory.create_blog('Pepsi', user, category, location)
    
    def test_simple_get(self):
        response = self.client.get('/blog/manage/')
        self.assertContains(response, 'Sprite')
        self.assertContains(response, 'Coke')
        self.assertContains(response, 'Pepsi')
        
        
