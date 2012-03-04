from django.contrib.auth.models import User
from django.test import TestCase
from blog.models import Blog, Love
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
        blog1 = factory.create_blog('Sprite', user, category, location, mood=1)
        blog2 = factory.create_blog('Coke', user, category, location)
        blog3 = factory.create_blog('Pepsi', user, category, location, mood=3)
        
        user1 = factory.create_user('testlove1', 'tester1@example.com', 'testuser1')
        user2 = factory.create_user('testlove2', 'tester2@example.com', 'testuser2')

        love1 = Love(user=user1, blog=blog1)
        love1.save()
        love2 = Love(user=user2, blog=blog1)
        love2.save()
        love3 = Love(user=user2, blog=blog2)
        love3.save()
    
    def test_simple_get(self):
        response = self.client.get('/blog/manage/')
        # test names
        self.assertContains(response, 'Sprite')
        self.assertContains(response, 'Coke')
        self.assertContains(response, 'Pepsi')
        
        # test loves after names
        self.assertContains(response, '<td>Sprite</td><td>2</td>')
        self.assertContains(response, '<td>Coke</td><td>1</td>')
        
        # test mood
        self.assertContains(response, '<td>Pepsi</td><td>0</td><td><div class="mood-3">Happy</div></td>')
        self.assertContains(response, '<td>Sprite</td><td>2</td><td><div class="mood-1">Sad</div></td>')
