from django.contrib.auth.models import User
from django.test import TestCase
from blog.models import Blog
from mock import Mock, patch
from tests import factory

class MyMock(object):
    def __init__(self, **kwargs):
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

class BaseTestBlogManagement(TestCase):
    def setUp(self):
        sprite = MyMock(title = 'Sprite')
        coke = MyMock(title = 'Coke')
        pepsi = MyMock(title = 'Pepsi')
        self.blogs = [sprite, coke, pepsi]
    
class TestBlogManagementUsingPatch(BaseTestBlogManagement):
    # Test only view function, model layer is mocked
    @patch('blog.models.Blog.objects.all')
    def test_simple_get(self, mocked_all):
        # Act
        mocked_all.return_value = self.blogs
        response = self.client.get('/blog/manage/')
        # Assert
        self.assertContains(response, 'Sprite')
        self.assertContains(response, 'Coke')
        self.assertContains(response, 'Pepsi')
 

class TestBlogManagementUsingMock(BaseTestBlogManagement):
    # Test only view function, model layer is mocked
    def setUp(self):
        super(TestBlogManagementUsingMock, self).setUp()
        self.mock_blog_manager()

    def tearDown(self):
        self.unmock_blog_manager()
        super(TestBlogManagementUsingMock, self).tearDown()
    
    def mock_blog_manager(self):
        self.original_manager = Blog.objects
        Blog.objects = self.mock_manager = Mock()
        Blog.objects.all = Mock(return_value = self.blogs)

    def unmock_blog_manager(self):
        Blog.objects = self.original_manager

    def test_simple_get(self):
        # Act
        response = self.client.get('/blog/manage/')
        # Assert
        self.assertContains(response, 'Sprite')
        self.assertContains(response, 'Coke')
        self.assertContains(response, 'Pepsi')

    def test_manage_blog__GET__parameters_passed_in_blog_manager(self):
        """
        Scenario: GET method to /blog/manage/
        Expected:
        - Blog.objects.all is called with no parameters
        """
        # Act
        response = self.client.get('/blog/manage/')
        # Assert
        Blog.objects.all.assert_called_once_with()

    
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
        
        
