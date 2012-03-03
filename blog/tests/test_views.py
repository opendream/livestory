from django.contrib.auth.models import User
from django.test import TestCase
from blog.models import Blog

class TestBlogManagement(TestCase):
    def setUp(self):
        username = 'testuser'
        email = 'test@example.com'
        password = 'testuser'
        self.user = User.objects.create_user(username, email, password)

        
    
    def test_simple_get(self):
        response = self.client.get('/blog/manage/')
        self.assertEqual(200, response.status_code)
        
        
