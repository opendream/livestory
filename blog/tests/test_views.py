from django.contrib.auth.models import User
from django.test import TestCase
from blog.models import Blog
from tests import factory

class TestBlogManagement(TestCase):
    def setUp(self):
        self.user = factory.create_user()

        
    
    def test_simple_get(self):
        response = self.client.get('/blog/manage/')
        self.assertEqual(200, response.status_code)
        
        
