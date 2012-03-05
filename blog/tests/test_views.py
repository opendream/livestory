from django.contrib.auth.models import User
from django.test import TestCase
from blog.models import Blog, Love
from blog.views import blog_bulk_update_private
from blog.views import blog_bulk_update_public
from mock import Mock, patch
from tests import factory
from bs4 import BeautifulSoup

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

    
class TestGetBlogManagementWithModel(TestCase):
    def setUp(self):
        user = factory.create_user()
        category = factory.create_category()
        location = factory.create_location()

        self.blogs = [
            factory.create_blog('Sprite', user, category, location, mood=1),
            factory.create_blog('Coke', user, category, location),
            factory.create_blog('Pepsi', user, category, location, mood=3)
        ]
        
        user1 = factory.create_user('testlove1', 'tester1@example.com', 'testuser1')
        user2 = factory.create_user('testlove2', 'tester2@example.com', 'testuser2')

        love1 = Love(user=user1, blog=self.blogs[0])
        love1.save()
        love2 = Love(user=user2, blog=self.blogs[0])
        love2.save()
        love3 = Love(user=user2, blog=self.blogs[1])
        love3.save()
        
        self.blogs[0].created = '2012-03-02'
        self.blogs[0].save()
        self.blogs[2].created = '2012-02-14'
        self.blogs[2].save()
    
    def test_names(self):
        response = self.client.get('/blog/manage/')
        self.assertContains(response, 'class="title">Sprite</')
        self.assertContains(response, 'class="title">Coke</')
        self.assertContains(response, 'class="title">Pepsi</')
        
    def test_loves(self):
        response = self.client.get('/blog/manage/')
        self.assertContains(response, 'class="loves">2</')
        self.assertContains(response, 'class="loves">1</')
        
    def test_mood(self):
        response = self.client.get('/blog/manage/')
        self.assertContains(response, 'class="mood-3">Happy</')
        self.assertContains(response, 'class="mood-1">Sad</')
        
    def test_created(self):
        response = self.client.get('/blog/manage/')
        self.assertContains(response, 'class="created">2012-03-02</')
        self.assertContains(response, 'class="created">2012-02-14</')
        
    def test_columns_order(self):
        response = self.client.get('/blog/manage/')
        soup = BeautifulSoup(response.content)
        tr = soup.find('tr')
        classes = [td.attrs['class'][0] for td in tr.find_all('td')]
        
        self.assertEqual(classes, ['blog_id', 'title', 'loves', 'mood', 'created'])

    def test_render_checkboxes(self):
        response = self.client.get('/blog/manage/')
        for blog in self.blogs:
            self.assertContains(response, '<input type="checkbox" name="blog_id" value="%s">' % blog.id)

    def test_operations_select_exists(self):
        response = self.client.get('/blog/manage/')
        self.assertContains(response, '<select name="op"><option value="set_private">Private</option><option value="set_public">Public</option></select>')

    def test_apply_button_exists(self):
        response = self.client.get('/blog/manage/')
        self.assertContains(response, '<input type="submit" value="Apply">')


class TestBlogUpdate(TestCase):
    def setUp(self):
        user = factory.create_user()
        category = factory.create_category()
        location = factory.create_location()
        self.blogs = [
            factory.create_blog('Sprite', user, category, location),
            factory.create_blog('Coke', user, category, location),
            factory.create_blog('Pepsi', user, category, location)
        ]
        self.blogs[0].private = True
        self.blogs[0].save()
        self.blogs[1].private = False
        self.blogs[1].save()
        self.blogs[2].private = True
        self.blogs[2].save()

    def test_simple_get(self):
        response = self.client.get('/blog/manage/')
        self.assertContains(response, 'Sprite')

    def test_post_bulk_private(self):
        blog_ids = [ blog.id for blog in self.blogs]
        response = self.client.post('/blog/manage/bulk/', {'blog_id': blog_ids, 'op': 'set_private'})
        self.assertEquals(302, response.status_code) # redirect code
        for blog in self.blogs:
            b = Blog.objects.get(id=blog.id)
            self.assertEquals(True, b.private)

    def test_post_bulk_public(self):
        blog_ids = [ blog.id for blog in self.blogs]
        response = self.client.post('/blog/manage/bulk/', {'blog_id': blog_ids, 'op': 'set_public'})
        self.assertEquals(302, response.status_code) # redirect code
        for blog in self.blogs:
            b = Blog.objects.get(id=blog.id)
            self.assertEquals(False, b.private)

    def test_blog_bulk_update_private(self):
        blog_bulk_update_private(self.blogs)
        for blog in self.blogs:
            b = Blog.objects.get(id=blog.id)
            self.assertEquals(True, b.private)

    def test_blog_bulk_update_public(self):
        blog_bulk_update_public(self.blogs)
        for blog in self.blogs:
            b = Blog.objects.get(id=blog.id)
            self.assertEquals(False, b.private)
