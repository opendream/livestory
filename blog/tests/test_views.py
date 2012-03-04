from django.contrib.auth.models import User
from django.test import TestCase
from blog.models import Blog
from mock import Mock
from tests import factory

class MyMock(object):
    def __init__(self, **kwargs):
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

class TestBlogManagement(TestCase):
    def setUp(self):
        self.mock_blog_manager()

    def tearDown(self):
        self.unmock_blog_manager()
    
    def mock_blog_manager(self):
        sprite = MyMock(title = 'Sprite')
        coke = MyMock(title = 'Coke')
        pepsi = MyMock(title = 'Pepsi')
        blogs = [sprite, coke, pepsi]

        self.original_manager = Blog.objects
        Blog.objects = self.mock_manager = Mock()
        Blog.objects.all = Mock(return_value = blogs)

    def unmock_blog_manager(self):
        Blog.objects = self.original_manager

    # Test only view function, model layer is mocked
    def test_simple_get(self):
        # Act
        response = self.client.get('/blog/manage/')
        # Assert
        print 'content = ', response.content
        self.assertContains(response, 'Sprite')
        self.assertContains(response, 'Coke')
        self.assertContains(response, 'Pepsi')
    
class TestBlogManagementWithModel(TestCase):
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
        
        
