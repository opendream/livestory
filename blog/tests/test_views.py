from django.contrib.auth.models import User
from django.core.files.base import File as DjangoFile
from django.test import TestCase
from blog.models import Blog, Love
from mock import Mock, patch
from tests import factory
from bs4 import BeautifulSoup

import settings
import shutil
import xpath

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
        
        blog1.created = '2012-03-02'
        blog1.save()
        blog3.created = '2012-02-14'
        blog3.save()
    
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
        
        self.assertEqual(classes, ['title', 'loves', 'mood', 'created'])
        
class TestBlogCreate(TestCase):
    def setUp(self):
        self.user = factory.create_user('test@example.com', 'test@example.com', 'test')
        self.category = factory.create_category('Animal', 'animal')
        self.location = factory.create_location('Japan', 'Tokyo')
        
    def test_blog_create_get(self):
        response = self.client.get('/blog/create/')
        self.assertEquals(403, response.status_code)
        
        self.client.login(username='test@example.com', password='test')
        response = self.client.get('/blog/create/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        self.client.logout()
    
    def test_blog_create_post_empty(self):
        params = {
            'title': '',
            'image_path': '',
            'description': '',
            'mood': '',
            'country': '',
            'city': '',
            'private': '',
            'draft': '',
        }
        response = self.client.post('/blog/create/', params)
        self.assertEquals(403, response.status_code)
        
        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/create/', params)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        
        self.assertEquals(True, response.context['imagefield_error'])
        self.assertFormError(response, 'form', 'title', ['This field is required.'])
        self.assertFormError(response, 'form', 'mood', ['This field is required.'])
        self.assertFormError(response, 'form', 'private', ['This field is required.'])
        self.assertFormError(response, 'form', 'country', ['This field is required.'])
        self.assertFormError(response, 'form', 'city', ['This field is required.'])
        self.client.logout()
        
    def test_blog_create_post_publish(self):
        src = '%s/static/tests/blog.jpg' % settings.base_path
        dst = '%stemp/test_create_post.jpg' % settings.MEDIA_ROOT
        shutil.copy2(src, dst)
        params = {
            'title': 'Hello world',
            'image_path': dst,
            'description': 'lorem ipsum',
            'mood': '4',
            'country': 'Japan',
            'city': 'Tokyo',
            'private': '1',
            'draft': '0',
            'category': str(self.category.id)
        }
        response = self.client.post('/blog/create/', params)
        self.assertEquals(403, response.status_code)
        
        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/create/', params, follow=True)
        blog = response.context['blog']
        user_id = self.client.session.get('_auth_user_id')
        
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        self.assertEquals('Edit Post', response.context['page_title'])
        self.assertEquals(False, response.context['imagefield_error'])
        self.assertEquals(False, response.context['is_draft'])
        self.assertEquals('%simages/blog/%s/%s/blog_%s.jpg' % (settings.MEDIA_ROOT, user_id, blog.id, blog.id), response.context['image_path'])
        self.assertEquals('%simages/blog/%s/%s/blog_%s.jpg' % (settings.MEDIA_ROOT, user_id, blog.id, blog.id), blog.image.path)
        self.assertEquals('Hello world', blog.title)
        self.assertEquals('lorem ipsum', blog.description)
        self.assertEquals(4, blog.mood)
        self.assertEquals(True, blog.private)
        self.assertEquals(False, blog.draft)
        self.assertEquals(self.category, blog.category)
        self.assertEquals(self.location, blog.location)
    
    def test_blog_create_post_draft(self):
        src = '%s/static/tests/blog.jpg' % settings.base_path
        dst = '%stemp/test_create_post.jpg' % settings.MEDIA_ROOT
        shutil.copy2(src, dst)
        params = {
            'title': 'Hello world (Draft)',
            'image_path': dst,
            'description': 'lorem ipsum (Draft)',
            'mood': '3',
            'country': 'Uganda',
            'city': 'Capital Uganda',
            'private': '0',
            'draft': '1',
            'category': str(self.category.id)
        }
        response = self.client.post('/blog/create/', params)
        self.assertEquals(403, response.status_code)

        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/create/', params, follow=True)
        blog = response.context['blog']
        user_id = self.client.session.get('_auth_user_id')

        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        self.assertEquals('Edit Post', response.context['page_title'])
        self.assertEquals(False, response.context['imagefield_error'])
        self.assertEquals(True, response.context['is_draft'])
        self.assertEquals('%simages/blog/%s/%s/blog_%s.jpg' % (settings.MEDIA_ROOT, user_id, blog.id, blog.id), response.context['image_path'])
        self.assertEquals('%simages/blog/%s/%s/blog_%s.jpg' % (settings.MEDIA_ROOT, user_id, blog.id, blog.id), blog.image.path)
        self.assertEquals('Hello world (Draft)', blog.title)
        self.assertEquals('lorem ipsum (Draft)', blog.description)
        self.assertEquals(3, blog.mood)
        self.assertEquals(False, blog.private)
        self.assertEquals(True, blog.draft)
        self.assertEquals(self.category, blog.category)
        self.assertEquals('Uganda', blog.location.country)
        self.assertEquals('Capital Uganda', blog.location.city)
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
