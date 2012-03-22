from django.contrib.auth.models import User
from django.core.files.base import File as DjangoFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson as json

from blog.models import Blog, Love
from location.models import Location
from mock import Mock, patch
from tests import factory
from bs4 import BeautifulSoup

from common import rm_user
from django.conf import settings
from override_settings import override_settings
import shutil

        
class TestBlogCreate(TestCase):
    def setUp(self):
        self.user = factory.create_user('test@example.com', 'test@example.com', 'test')
        self.category = factory.create_category('Animal', 'animal')
        self.location = factory.create_location('Japan', 'Tokyo')
    
    def tearDown(self):
        rm_user(self.user.id)
        
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
            'category': ''
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
        self.assertFormError(response, 'form', 'category', ['This field is required.'])
        self.client.logout()
        
    def test_blog_create_post_publish(self, again=True):
        src = '%s/static/tests/blog.jpg' % settings.BASE_PATH
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
        
        self.client.logout()
    
    def test_blog_create_post_draft(self, country='thailand', city='suratthanee', again=True):
        src = '%s/static/tests/blog.jpg' % settings.BASE_PATH
        dst = '%stemp/test_create_post.jpg' % settings.MEDIA_ROOT
        shutil.copy2(src, dst)
        params = {
            'title': 'Hello world (Draft)',
            'image_path': dst,
            'description': 'lorem ipsum (Draft)',
            'mood': '3',
            'country': country,
            'city': city,
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
        self.assertEquals('Thailand', blog.location.country)
        self.assertEquals('Surat Thani', blog.location.city)
        self.assertEquals('8.9034051', blog.location.lat)
        self.assertEquals('99.0128926', blog.location.lng)
        self.client.logout()
        
        if again:
            self.test_blog_create_post_draft(country='thailand', city='surat thani', again=False)
            same = Location.objects.filter(country='Thailand', city='Surat Thani').count()
            self.assertEquals(1, same)
            
    def test_blog_create_post_miss_match_location(self):
        src = '%s/static/tests/blog.jpg' % settings.BASE_PATH
        dst = '%stemp/test_create_post.jpg' % settings.MEDIA_ROOT
        shutil.copy2(src, dst)
        params = {
            'title': 'Hello world (Draft)',
            'image_path': dst,
            'description': 'lorem ipsum (Draft)',
            'mood': '3',
            'country': 'ljkljkljlkjlkjlkj',
            'city': 'asdfdasffdffad',
            'private': '0',
            'draft': '1',
            'category': str(self.category.id)
        }
        response = self.client.post('/blog/create/', params)
        self.assertEquals(403, response.status_code)

        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/create/', params, follow=True)

        self.assertEquals(True, response.context['location_error'])
        self.client.logout()


class TestBlogEdit(TestCase):
    def setUp(self):
        self.user = factory.create_user('test@example.com', 'test@example.com', 'test')
        self.other_user = factory.create_user('othertest@example.com', 'othertest@example.com', 'test')
        self.staff = factory.create_user('staff@example.com', 'staff@example.com', 'test')
        self.staff.is_staff = True
        self.staff.save()
        self.category = factory.create_category('Animal', 'animal')
        self.location = factory.create_location('Japan', 'Tokyo')
        self.cat_travel = factory.create_category('Travel', 'travel')
        self.loc_korea = factory.create_location('Korea', 'Sol')
        self.blog = factory.create_blog('Animal in Tokyo', self.user, self.category, self.location)
        self.blog_draft = factory.create_blog('Animal in Tokyo', self.user, self.category, self.location)
        self.blog_draft.draft = True
        self.blog_draft.save()
        
    def tearDown(self):
        rm_user(self.user.id      )
        rm_user(self.other_user.id)
        rm_user(self.staff.id     )
        
    def test_blog_edit_get(self):
        response = self.client.get('/blog/%s/edit/' % self.blog.id)
        self.assertEquals(403, response.status_code)
        
        self.client.login(username='othertest@example.com', password='test')
        response = self.client.get('/blog/%s/edit/' % self.blog.id)
        self.assertEquals(403, response.status_code)
        self.client.logout()
        
        self.client.login(username='test@example.com', password='test')
        response = self.client.get('/blog/%s/edit/' % self.blog.id)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        self.client.logout()
        
        self.client.login(username='staff@example.com', password='test')
        response = self.client.get('/blog/%s/edit/' % self.blog.id)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        self.client.logout()
        
        self.client.login(username='staff@example.com', password='test')
        response = self.client.get('/blog/0/edit/')
        self.assertEquals(404, response.status_code)
        self.client.logout()
    
    def test_blog_edit_post_empty(self):
        params = {
            'title': '',
            'image_path': '',
            'description': '',
            'mood': '',
            'country': '',
            'city': '',
            'private': '',
            'draft': '',
            'category': '',
        }
        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/%s/edit/' % self.blog.id, params)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        
        self.assertEquals(True, response.context['imagefield_error'])
        self.assertFormError(response, 'form', 'title', ['This field is required.'])
        self.assertFormError(response, 'form', 'mood', ['This field is required.'])
        self.assertFormError(response, 'form', 'private', ['This field is required.'])
        self.assertFormError(response, 'form', 'country', ['This field is required.'])
        self.assertFormError(response, 'form', 'city', ['This field is required.'])
        self.assertFormError(response, 'form', 'category', ['This field is required.'])
        self.client.logout()

    def test_blog_edit_post_publish(self):
        src = '%s/static/tests/blog.jpg' % settings.BASE_PATH
        dst = '%stemp/test_edit_post.jpg' % settings.MEDIA_ROOT
        shutil.copy2(src, dst)
        params = {
            'title': 'Hello world Edited',
            'image_path': dst,
            'description': 'lorem ipsum Edited',
            'mood': '2',
            'country': 'Korea',
            'city': 'Sol',
            'private': '1',
            'draft': '0',
            'category': str(self.cat_travel.id)
        }
        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/%s/edit/' % self.blog.id, params, follow=True)
        blog = response.context['blog']
        user_id = self.client.session.get('_auth_user_id')

        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        self.assertEquals('Edit Post', response.context['page_title'])
        self.assertEquals(False, response.context['imagefield_error'])
        self.assertEquals(False, response.context['is_draft'])
        self.assertEquals('%simages/blog/%s/%s/blog_%s.jpg' % (settings.MEDIA_ROOT, user_id, blog.id, blog.id), response.context['image_path'])
        self.assertEquals('%simages/blog/%s/%s/blog_%s.jpg' % (settings.MEDIA_ROOT, user_id, blog.id, blog.id), blog.image.path)
        self.assertEquals('Hello world Edited', blog.title)
        self.assertEquals('lorem ipsum Edited', blog.description)
        self.assertEquals(2, blog.mood)
        self.assertEquals(True, blog.private)
        self.assertEquals(False, blog.draft)
        self.assertEquals(self.cat_travel, blog.category)
        self.assertEquals(self.loc_korea, blog.location)

    def test_blog_edit_post_draft_publish_post(self, again=True):
        src = '%s/static/tests/blog.jpg' % settings.BASE_PATH
        dst = '%stemp/test_edit_post.jpg' % settings.MEDIA_ROOT
        shutil.copy2(src, dst)
        params = {
            'title': 'Hello world Edited',
            'image_path': dst,
            'description': 'lorem ipsum Edited',
            'mood': '2',
            'country': 'Korea',
            'city': 'Sol',
            'private': '1',
            'draft': '1',
            'category': str(self.cat_travel.id)
        }
        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/%s/edit/' % self.blog.id, params, follow=True)
        blog = response.context['blog']
        user_id = self.client.session.get('_auth_user_id')

        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        self.assertEquals('Edit Post', response.context['page_title'])
        self.assertEquals(False, response.context['imagefield_error'])
        self.assertEquals(False, response.context['is_draft'])
        self.assertEquals('%simages/blog/%s/%s/blog_%s.jpg' % (settings.MEDIA_ROOT, user_id, blog.id, blog.id), response.context['image_path'])
        self.assertEquals('%simages/blog/%s/%s/blog_%s.jpg' % (settings.MEDIA_ROOT, user_id, blog.id, blog.id), blog.image.path)
        self.assertEquals('Hello world Edited', blog.title)
        self.assertEquals('lorem ipsum Edited', blog.description)
        self.assertEquals(2, blog.mood)
        self.assertEquals(True, blog.private)
        self.assertEquals(False, blog.draft)
        self.assertEquals(self.cat_travel, blog.category)
        self.assertEquals(self.loc_korea, blog.location)
        
        # For image directory exist (duplicate from above)
        if again:
            self.test_blog_edit_post_draft_publish_post(False)
    
    def test_blog_edit_post_draft_on_draft_post(self):
        src = '%s/static/tests/blog.jpg' % settings.BASE_PATH
        dst = '%stemp/test_edit_post.jpg' % settings.MEDIA_ROOT
        shutil.copy2(src, dst)
        params = {
            'title': 'Hello world Edited',
            'image_path': dst,
            'description': 'lorem ipsum Edited',
            'mood': '2',
            'country': 'Korea',
            'city': 'Sol',
            'private': '1',
            'draft': '1',
            'category': str(self.cat_travel.id)
        }
        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/%s/edit/' % self.blog_draft.id, params, follow=True)
        blog = response.context['blog']
        user_id = self.client.session.get('_auth_user_id')

        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        self.assertEquals('Edit Post', response.context['page_title'])
        self.assertEquals(False, response.context['imagefield_error'])
        self.assertEquals(True, response.context['is_draft'])
        self.assertEquals('%simages/blog/%s/%s/blog_%s.jpg' % (settings.MEDIA_ROOT, user_id, blog.id, blog.id), response.context['image_path'])
        self.assertEquals('%simages/blog/%s/%s/blog_%s.jpg' % (settings.MEDIA_ROOT, user_id, blog.id, blog.id), blog.image.path)
        self.assertEquals('Hello world Edited', blog.title)
        self.assertEquals('lorem ipsum Edited', blog.description)
        self.assertEquals(2, blog.mood)
        self.assertEquals(True, blog.private)
        self.assertEquals(True, blog.draft)
        self.assertEquals(self.cat_travel, blog.category)
        self.assertEquals(self.loc_korea, blog.location)
    
    def test_blog_edit_post_miss_match_location(self):
        src = '%s/static/tests/blog.jpg' % settings.BASE_PATH
        dst = '%stemp/test_edit_post.jpg' % settings.MEDIA_ROOT
        shutil.copy2(src, dst)
        params = {
            'title': 'Hello world Edited',
            'image_path': dst,
            'description': 'lorem ipsum Edited',
            'mood': '2',
            'country': 'fdasdffafaf',
            'city': 'tryeryrtytry',
            'private': '1',
            'draft': '1',
            'category': str(self.cat_travel.id)
        }
        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/%s/edit/' % self.blog_draft.id, params, follow=True)

        self.assertEquals(True, response.context['location_error'])
        self.client.logout()


class TestBlogView(TestCase):
    def setUp(self):
        self.user = factory.create_user('test@example.com', 'test@example.com', 'test')
        self.user2 = factory.create_user('test2@example.com', 'test2@example.com', 'test')
        self.user3 = factory.create_user('test3@example.com', 'test3@example.com', 'test')
        self.otheruser = factory.create_user('othertest@example.com', 'othertest@example.com', 'test')
        self.staff = factory.create_user('staff@example.com', 'staff@example.com', 'test')
        self.staff.is_staff = True
        self.staff.save()
        self.category = factory.create_category('Animal', 'animal')
        self.location = factory.create_location('Japan', 'Tokyo')
        
        self.blog = factory.create_blog('Animal in Tokyo', self.user, self.category, self.location)
        self.blog.private = False
        self.blog.save()

        self.blog_private = factory.create_blog('Animal in Tokyo', self.user, self.category, self.location)
        self.blog_private.private = True
        self.blog_private.save()
        
        self.blog_draft = factory.create_blog('Animal in Tokyo', self.user, self.category, self.location)
        self.blog_draft.draft = True
        self.blog_draft.save()
        self.blog_unlove = factory.create_blog('Animal in Tokyo Unlove', self.user, self.category, self.location)
        
        Love(blog=self.blog_private, user=self.user).save()
        Love(blog=self.blog_private, user=self.otheruser).save()
        Love(blog=self.blog_private, user=self.staff).save()
        Love(blog=self.blog_unlove, user=self.user3).save()
    
    def tearDown(self):
        rm_user(self.user.id     )
        rm_user(self.user2.id    )
        rm_user(self.user3.id    )
        rm_user(self.otheruser.id)
        rm_user(self.staff.id    )
    
    def test_blog_view_get(self):    
        response = self.client.get('/blog/%s/view/' % self.blog.id)
        self.assertEquals(200, response.status_code)
        
        response = self.client.get('/blog/%s/view/' % self.blog_private.id)
        self.assertEquals(403, response.status_code)
        
        self.client.login(username='test@example.com', password='test')
        response = self.client.get('/blog/%s/view/' % self.blog_private.id)
        self.assertEquals(200, response.status_code)
        response = self.client.get('/blog/%s/view/' % self.blog_draft.id)
        self.assertEquals(200, response.status_code)
        self.assertNotContains(response, 'class="love-button')
        self.client.logout()
        
        self.client.login(username='othertest@example.com', password='test')
        response = self.client.get('/blog/%s/view/' % self.blog_draft.id)
        self.assertEquals(403, response.status_code)
        self.client.logout()
        
        self.client.login(username='staff@example.com', password='test')
        response = self.client.get('/blog/%s/view/' % self.blog_draft.id)
        self.assertEquals(200, response.status_code)
        self.client.logout()
        
        response = self.client.get('/blog/0/view/')
        self.assertEquals(404, response.status_code)

    def test_blog_view_love(self):
        self.client.login(username='test@example.com', password='test')
        response = self.client.get('/blog/%s/view/' % self.blog_private.id)
        self.assertEquals(3, response.context['love_count'])
        self.assertEquals('/blog/%s/unlove/' % self.blog_private.id, response.context['love_path'])
        self.assertEquals('unlove', response.context['button_type'])
        self.assertEquals([self.staff.get_profile(), self.otheruser.get_profile(), self.user.get_profile()], response.context['loved_users'])
        self.client.logout()
        
        self.client.login(username='test2@example.com', password='test')
        response = self.client.get('/blog/%s/view/' % self.blog_private.id)
        
        self.assertEquals('/blog/%s/love/' % self.blog_private.id, response.context['love_path'])
        self.assertEquals('love', response.context['button_type'])
        self.client.logout()
    
    def test_blog_love_blog(self):
        # user is not logged in
        response = self.client.get('/blog/%s/love/' % self.blog_private.id)
        self.assertEquals(403, response.status_code)
        
        # user is not logged in, blog does not exists
        response = self.client.get('/blog/0/love/')
        self.assertEquals(404, response.status_code)
        
        # login
        self.client.login(username='test2@example.com', password='test')
        
        # user is logged in, blog does not exists, ajax
        response = self.client.get('/blog/0/love/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(json.dumps({'status': 404}), response.content)

        # user is logged in, blog exists, not ajax
        response = self.client.get('/blog/%s/love/' % self.blog_private.id, follow=True)
        self.assertRedirects(response, '/blog/%s/view/' % self.blog_private.id)
        self.assertEquals(4, self.blog_private.love_set.count())
        
        response = self.client.get('/blog/%s/love/' % self.blog_private.id, follow=True)
        self.assertRedirects(response, '/blog/%s/view/' % self.blog_private.id)
        self.assertEquals(4, self.blog_private.love_set.count())
        
        # user is logged in, blog exists, ajax
        response = self.client.get('/blog/%s/love/' % self.blog.id,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps({'love': 1, 'type': 'unlove', 'status': 200}), response.content)
        self.assertEquals(1, self.blog.love_set.count())
        
        # user is logged in, blog exists, ajax, user has already loved
        response = self.client.get('/blog/%s/love/' % self.blog.id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps({'love': 1, 'type': 'unlove', 'status': 200}), response.content)
        self.assertEquals(1, self.blog.love_set.count())

        # user is logged in, blog exists, blog is draft
        response = self.client.get('/blog/%s/love/' % self.blog_draft.id)
        self.assertEquals(403, response.status_code)
        self.client.logout()
    
    def test_blog_unlove_blog(self):
        # user is not logged in
        response = self.client.get('/blog/%s/unlove/' % self.blog_private.id)
        self.assertEquals(403, response.status_code)
        
        # user is not logged in, blog does not exists
        response = self.client.get('/blog/0/unlove/')
        self.assertEquals(404, response.status_code)
        
        # login
        self.client.login(username='test3@example.com', password='test')
        
        # user is logged in, blog does not exists, ajax
        response = self.client.get('/blog/0/unlove/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(json.dumps({'status': 404}), response.content)

        # user is logged in, blog exists, not ajax
        response = self.client.get('/blog/%s/unlove/' % self.blog_unlove.id, follow=True)
        self.assertRedirects(response, '/blog/%s/view/' % self.blog_unlove.id)
        self.assertEquals(0, self.blog_unlove.love_set.count())
        
        response = self.client.get('/blog/%s/unlove/' % self.blog_unlove.id, follow=True)
        self.assertRedirects(response, '/blog/%s/view/' % self.blog_unlove.id)
        self.assertEquals(0, self.blog_unlove.love_set.count())
        
        # user is logged in, blog exists, ajax
        self.client.get('/blog/%s/love/' % self.blog_unlove.id)
        response = self.client.get('/blog/%s/unlove/' % self.blog.id,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps({'love': -1, 'type': 'love', 'status': 200}), response.content)
        self.assertEquals(0, self.blog.love_set.count())
        
        # user is logged in, blog exists, ajax, user has already loved
        response = self.client.get('/blog/%s/unlove/' % self.blog.id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps({'love': -1, 'type': 'love', 'status': 200}), response.content)
        self.assertEquals(0, self.blog.love_set.count())

        # user is logged in, blog exists, blog is draft
        response = self.client.get('/blog/%s/unlove/' % self.blog_draft.id)
        self.assertEquals(403, response.status_code)
        self.client.logout()

    @override_settings(CAN_SHARE_SN=False)
    def test_blog_display_social_network(self):
        self.client.login(username='test3@example.com', password='test')
        response = self.client.get('/blog/%s/view/' % self.blog.id)
        self.assertNotContains(response, '<!-- AddThis Button BEGIN -->')
        self.client.logout()

    @override_settings(CAN_SHARE_SN=True)
    def test_blog_display_social_network(self):
        self.client.login(username='test3@example.com', password='test')
        response = self.client.get('/blog/%s/view/' % self.blog.id)
        self.assertContains(response, '<!-- AddThis Button BEGIN -->')
        self.client.logout()
        
        
class TestHomePage(TestCase):
    def setUp(self):
        self.user = factory.create_user('testuser@example.com', 'testuser@example.com', 'password', 'John', 'Doe', True)

    def tearDown(self):
        rm_user(self.user.id)

    def test_anonymous_user_get(self):
        response = self.client.get(reverse('blog_home'))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_static.html')

    def test_authenticated_user_get(self):
        self.client.login(username='testuser@example.com', password='password')
        response = self.client.get(reverse('blog_home'))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_home.html')
        self.client.logout()

class TestAllPage(TestCase):
    def setUp(self):
        self.user1 = factory.create_user('testuser1@example.com', 'testuser1@example.com', 'password', 'John', 'Doe 1', True)
        self.user2 = factory.create_user('testuser2@example.com', 'testuser2@example.com', 'password', 'John', 'Doe 2', True)
        self.category1 = factory.create_category('Animal', 'animal')
        self.category2 = factory.create_category('Food', 'food')
        self.location1 = factory.create_location('Japan', 'Tokyo', '0', '0')
        self.location2 = factory.create_location('Thailand', 'Bangkok', '0', '0')
        
        blogs = Blog.objects.all()
        for blog in blogs:
            blog.delete(with_file=False)
        
        self.blogs = [
            factory.create_blog('Blog 1', self.user1, self.category1, self.location1, private=True ), 
            factory.create_blog('Blog 2', self.user1, self.category1, self.location2, private=True ), 
            factory.create_blog('Blog 3', self.user1, self.category1, self.location1, private=True ), 
            factory.create_blog('Blog 4', self.user1, self.category2, self.location2, private=False), 
            factory.create_blog('Blog 5', self.user1, self.category2, self.location1, private=False), 
            factory.create_blog('Blog 6', self.user1, self.category2, self.location2, private=False), 
            factory.create_blog('Blog 7', self.user2, self.category1, self.location1, private=False), 
            factory.create_blog('Blog 8', self.user2, self.category1, self.location2, private=False), 
            factory.create_blog('Blog 9', self.user2, self.category1, self.location1, private=False), 
            factory.create_blog('Blog10', self.user2, self.category2, self.location2, private=True ), 
            factory.create_blog('Blog11', self.user2, self.category2, self.location1, private=True ), 
            factory.create_blog('Blog12', self.user2, self.category2, self.location2, private=True , draft=True)
        ]

    def tearDown(self):
        rm_user(self.user1.id)
        rm_user(self.user2.id)
        
    def test_blog_all_get(self):
        # Anonymous =====================
        response = self.client.get('/blog/all/')
        context = response.context
        
        blogs = [ blog.id for blog in self.blogs[3:9]]
        blogs.reverse()
                
        self.assertTemplateUsed(response, 'blog/blog_all.html')
        self.assertEquals(200, response.status_code)
        self.assertEquals(6, context['blogs'].count())
        self.assertEquals(blogs, [ blog.id for blog in context['blogs']])
        self.assertEquals(1, context['pager'].num_pages)
        self.assertEquals(1, context['page'])
        
        # Authenticated =================
        self.client.login(username='testuser1@example.com', password='password')
        response = self.client.get('/blog/all/')
        context = response.context
        
        blogs = [ blog.id for blog in self.blogs[3:11]]
        blogs.reverse()
        
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_all.html')
        self.assertEquals(8, context['blogs'].count())
        self.assertEquals(blogs, [ blog.id for blog in context['blogs']])
        self.assertEquals(2, context['pager'].num_pages)
        self.assertEquals(1, context['page'])
        self.client.logout()
        
    def test_blog_all_get_with_page(self):
        self.client.login(username='testuser1@example.com', password='password')
        response = self.client.get('/blog/all/?page=2')
        context = response.context
        
        blogs = [ blog.id for blog in self.blogs[0:3]]
        blogs.reverse()
        
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/blog_all.html')
        self.assertEquals(3, context['blogs'].count())
        self.assertEquals(blogs, [ blog.id for blog in context['blogs']])
        self.assertEquals(2, context['pager'].num_pages)
        self.assertEquals(2, context['page'])
        
        response = self.client.get('/blog/all/?page=3')
        self.assertEquals(404, response.status_code)
        
        response = self.client.get('/blog/all/?page=0')
        self.assertEquals(404, response.status_code)
        
        self.client.logout()


class TestBlogManagement(TestCase):
    def setUp(self):
        self.john = factory.create_user('john.carter@example.com', 'john.carter@example.com', '1234', 'John', 'Carter', True)
        self.adam = factory.create_user('adam.carter@example.com', 'adam.carter@example.com', '1234', 'Adam', 'Carter', True)
        self.staff = factory.create_user('staff.carter@example.com', 'staff.carter@example.com', '1234', 'Staff', 'Carter', True)
        self.staff.is_staff = True
        self.staff.save()

        self.category = factory.create_category('Animal', 'animal')
        self.location = factory.create_location('Japan', 'Tokyo', '0', '0')

        self.blogs = [
            factory.create_blog('John blog 1', self.john, self.category, self.location, private=True),
            factory.create_blog('John blog 2', self.john, self.category, self.location, private=True),
            factory.create_blog('John blog 3', self.john, self.category, self.location, private=True),
            factory.create_blog('Adam blog 1', self.adam, self.category, self.location, private=True),
            factory.create_blog('Adam blog 2', self.adam, self.category, self.location, private=True),
            factory.create_blog('Staff blog 1', self.staff, self.category, self.location, private=True),
        ]

    def tearDown(self):
        for blog in self.blogs:
            blog.delete()
        rm_user(self.john.id)
        rm_user(self.adam.id)
        rm_user(self.staff.id)
        self.client.logout()

    def test_anonymous_user_get(self):
        response = self.client.get(reverse('blog_manage'))
        self.assertEqual(403, response.status_code)

    def test_authenticated_user_get(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage'))
        self.assertEqual(200, response.status_code)

    def test_authenticated_user_can_see_only_own_story(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage'))
        self.assertEqual(3, response.context['blogs'].count())
        self.client.logout()

        self.client.login(username=self.adam.username, password='1234')
        response = self.client.get(reverse('blog_manage'))
        self.assertEqual(2, response.context['blogs'].count())
        self.client.logout()

    def test_staff_can_see_all_story(self):
        self.client.login(username=self.staff.username, password='1234')
        response = self.client.get(reverse('blog_manage'))
        all_blogs = Blog.objects.all()
        self.assertEqual(all_blogs.count(), response.context['blogs'].count())

    def test_anonymous_user_trash_blog(self):
        response = self.client.get(reverse('blog_trash', args=[self.blogs[0].id]))
        self.assertEquals(403, response.status_code)

    def test_authenticated_user_trash_own_blog_on_all_section(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_trash', args=[self.blogs[0].id]))
        self.assertRedirects(response, reverse('blog_manage'))
        blog = Blog.objects.get(id=self.blogs[0].id)
        self.assertTrue(blog.trash)
        self.client.logout()

    def test_authenticated_user_trash_own_blog_on_published_section(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_trash', args=[self.blogs[0].id]), {'section': 'published'})
        self.assertRedirects(response, reverse('blog_manage_published'))
        blog = Blog.objects.get(id=self.blogs[0].id)
        self.assertTrue(blog.trash)
        self.client.logout()

    def test_authenticated_user_trash_own_blog_on_draft_section(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_trash', args=[self.blogs[0].id]), {'section': 'draft'})
        self.assertRedirects(response, reverse('blog_manage_draft'))
        blog = Blog.objects.get(id=self.blogs[0].id)
        self.assertTrue(blog.trash)
        self.client.logout()

    def test_link_that_must_be_displayed_on_all_section_page(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage'))
        self.assertContains(response, reverse('blog_edit', args=[self.blogs[0].id]))
        self.assertContains(response, reverse('blog_trash', args=[self.blogs[0].id]))
        self.client.logout()

    def test_link_that_must_be_displayed_on_published_section_page(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage_published'))
        self.assertContains(response, reverse('blog_edit', args=[self.blogs[0].id]))
        self.assertContains(response, reverse('blog_trash', args=[self.blogs[0].id]) + '?section=published')
        self.client.logout()

    def test_link_that_must_be_displayed_on_draft_section_page(self):
        self.blogs[0].draft = True
        self.blogs[0].save()
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage_draft'))
        self.assertContains(response, reverse('blog_edit', args=[self.blogs[0].id]))
        self.assertContains(response, reverse('blog_trash', args=[self.blogs[0].id]) + '?section=draft')
        self.client.logout()

    def test_link_that_must_be_displayed_on_trash_section_page(self):
        self.blogs[0].trash = True
        self.blogs[0].save()
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage_trash'))
        self.assertNotContains(response, reverse('blog_edit', args=[self.blogs[0].id]))
        self.assertContains(response, reverse('blog_restore', args=[self.blogs[0].id]) + '?section=trash')
        self.client.logout()

    def test_blog_trash_cannot_edit(self):
        self.blogs[0].trash = True
        self.blogs[0].save()
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_edit', args=[self.blogs[0].id]))
        self.assertEqual(403, response.status_code)
        self.client.logout()

    def test_authenticated_user_trash_other_blog(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_trash', args=[self.blogs[3].id]))
        self.assertEqual(403, response.status_code)
        self.client.logout()

    def test_staff_user_trash_other_blog(self):
        self.client.login(username=self.staff.username, password='1234')
        response = self.client.get(reverse('blog_trash', args=[self.blogs[3].id]))
        self.assertRedirects(response, reverse('blog_manage'))
        blog = Blog.objects.get(id=self.blogs[3].id)
        self.assertTrue(blog.trash)
        self.client.logout()

    def test_trash_not_exists_blog(self):
        response = self.client.get(reverse('blog_trash', args=[0]))
        self.assertEquals(404, response.status_code)

    def test_trash_success_must_hide_blog_on_table(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_trash', args=[self.blogs[0].id]), follow=True)
        self.assertNotContains(response, reverse('blog_trash', args=[self.blogs[0].id]))
        self.client.logout()

    def test_number_of_blog_of_all_published_draft_trash(self):
        self.blogs[0].draft = False
        self.blogs[0].save()
        self.blogs[1].draft = True
        self.blogs[1].save()
        self.blogs[2].trash = True
        self.blogs[2].save()
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage'))
        self.assertEqual(2, response.context['num_all'])
        self.assertEqual(1, response.context['num_published'])
        self.assertEqual(1, response.context['num_draft'])
        self.assertEqual(1, response.context['num_trash'])
        self.client.logout()

    def test_view_manage_published(self):
        self.blogs[0].draft = False
        self.blogs[0].save()
        self.blogs[1].draft = True
        self.blogs[1].save()
        self.blogs[2].trash = True
        self.blogs[2].save()
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage_published'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context['blogs'].count())
        self.client.logout()

    def test_view_manage_draft(self):
        self.blogs[0].draft = True
        self.blogs[0].save()
        self.blogs[1].draft = True
        self.blogs[1].save()
        self.blogs[2].trash = True
        self.blogs[2].save()
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage_draft'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.context['blogs'].count())
        self.client.logout()

    def test_view_manage_trash(self):
        self.blogs[0].trash = True
        self.blogs[0].save()
        self.blogs[1].trash = True
        self.blogs[1].save()
        self.blogs[2].trash = True
        self.blogs[2].save()
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage_trash'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, response.context['blogs'].count())
        self.client.logout()

    def test_anonymous_user_restore_blog(self):
        response = self.client.get(reverse('blog_restore', args=[self.blogs[0].id]))
        self.assertEquals(403, response.status_code)

    def test_authenticated_user_restore_own_blog(self):
        self.blogs[0].trash = True
        self.blogs[0].save()
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_restore', args=[self.blogs[0].id]))
        self.assertRedirects(response, reverse('blog_manage_trash'))
        blog = Blog.objects.get(id=self.blogs[0].id)
        self.assertFalse(blog.trash)
        self.client.logout()

    def test_authenticated_user_restore_other_blog(self):
        self.blogs[3].trash = True
        self.blogs[3].save()
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_restore', args=[self.blogs[3].id]))
        self.assertEqual(403, response.status_code)
        self.assertTrue(self.blogs[3].trash)
        self.client.logout()

    def test_staff_user_restore_other_blog(self):
        self.blogs[3].trash = True
        self.blogs[3].save()
        self.client.login(username=self.staff.username, password='1234')
        response = self.client.get(reverse('blog_restore', args=[self.blogs[3].id]))
        self.assertRedirects(response, reverse('blog_manage_trash'))
        blog = Blog.objects.get(id=self.blogs[3].id)
        self.assertFalse(blog.trash)
        self.client.logout()

    def test_restore_not_exists_blog(self):
        response = self.client.get(reverse('blog_restore', args=[0]))
        self.assertEquals(404, response.status_code)

    def test_restore_success_must_hide_blog_on_table(self):
        self.blogs[0].trash = False
        self.blogs[0].save()
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_restore', args=[self.blogs[0].id]), follow=True)
        self.assertNotContains(response, reverse('blog_restore', args=[self.blogs[0].id]))
        self.client.logout()

    def test_bulk_form_action_on_all_section(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage'))
        self.assertContains(response, 'action="%s"' % reverse('blog_manage_bulk'))
        self.client.logout()

    def test_bulk_form_action_on_other_sections(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage_published'))
        self.assertContains(response, 'action="%s?section=published"' % reverse('blog_manage_bulk'))
        response = self.client.get(reverse('blog_manage_draft'))
        self.assertContains(response, 'action="%s?section=draft"' % reverse('blog_manage_bulk'))
        response = self.client.get(reverse('blog_manage_trash'))
        self.assertContains(response, 'action="%s?section=trash"' % reverse('blog_manage_bulk'))
        self.client.logout()

    def test_bulk_actions_available_on_each_sections(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage'))
        self.assertContains(response, '<option value="trash">Trash</option>')
        self.assertNotContains(response, '<option value="restore">Restore</option>')
        self.assertNotContains(response, '<option value="delete">Delete Permanently</option>')

        response = self.client.get(reverse('blog_manage_published'))
        self.assertContains(response, '<option value="trash">Trash</option>')
        self.assertNotContains(response, '<option value="restore">Restore</option>')
        self.assertNotContains(response, '<option value="delete">Delete Permanently</option>')

        response = self.client.get(reverse('blog_manage_draft'))
        self.assertContains(response, '<option value="trash">Trash</option>')
        self.assertNotContains(response, '<option value="restore">Restore</option>')
        self.assertNotContains(response, '<option value="delete">Delete Permanently</option>')

        response = self.client.get(reverse('blog_manage_trash'))
        self.assertNotContains(response, '<option value="trash">Trash</option>')
        self.assertContains(response, '<option value="restore">Restore</option>')
        self.assertContains(response, '<option value="delete">Delete Permanently</option>')

        self.client.logout()

    def test_bulk_checkboxes_tags_on_each_sections(self):
        self.blogs[0].draft = False
        self.blogs[0].save()
        self.blogs[1].draft = True
        self.blogs[1].save()
        self.blogs[2].trash = True
        self.blogs[2].save()

        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage'))
        self.assertContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[0].id)
        self.assertContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[1].id)
        self.assertNotContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[2].id)

        response = self.client.get(reverse('blog_manage_published'))
        self.assertContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[0].id)
        self.assertNotContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[1].id)
        self.assertNotContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[2].id)

        response = self.client.get(reverse('blog_manage_draft'))
        self.assertNotContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[0].id)
        self.assertContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[1].id)
        self.assertNotContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[2].id)

        response = self.client.get(reverse('blog_manage_trash'))
        self.assertNotContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[0].id)
        self.assertNotContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[1].id)
        self.assertContains(response, '<input type="checkbox" name="blog_id" value="%s">' % self.blogs[2].id)

        self.client.logout()

    def test_bulk_action_trash_post_by_anonymous_user(self):
        response = self.client.post(reverse('blog_manage_bulk'), {'op': 'trash', 'blog_id': self.blogs[0].id})
        blog = Blog.objects.get(id=self.blogs[0].id)
        self.assertFalse(blog.trash)
        self.assertEqual(403, response.status_code)

    def test_bulk_action_trash_get_by_anonymous_user(self):
        response = self.client.get(reverse('blog_manage_bulk'), {'op': 'trash', 'blog_id': self.blogs[0].id})
        blog = Blog.objects.get(id=self.blogs[0].id)
        self.assertFalse(blog.trash)
        self.assertEqual(403, response.status_code)

    def test_bulk_action_trash_get_by_authenticated_user(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage_bulk'), {'op': 'trash', 'blog_id': self.blogs[0].id})
        blog = Blog.objects.get(id=self.blogs[0].id)
        self.assertFalse(blog.trash)
        self.assertEqual(403, response.status_code)
        self.client.logout()

    def test_bulk_action_trash_own_blog_on_all_section_post_by_authenticated_user(self):
        self.client.login(username=self.john.username, password='1234')
        params = {
            'op': 'trash',
            'blog_id': [self.blogs[0].id, self.blogs[1].id, self.blogs[2].id]
        }
        response = self.client.post(reverse('blog_manage_bulk'), params, follow=True)
        self.blogs[0] = Blog.objects.get(id=self.blogs[0].id)
        self.assertTrue(self.blogs[0].trash)
        self.blogs[1] = Blog.objects.get(id=self.blogs[1].id)
        self.assertTrue(self.blogs[1].trash)
        self.blogs[2] = Blog.objects.get(id=self.blogs[2].id)
        self.assertTrue(self.blogs[2].trash)
        self.assertRedirects(response, reverse('blog_manage'))
        self.client.logout()

    def test_bulk_action_trash_own_blog_on_published_section_post_by_authenticated_user(self):
        self.client.login(username=self.john.username, password='1234')
        params = {
            'op': 'trash',
            'blog_id': [self.blogs[0].id, self.blogs[2].id]
        }
        response = self.client.post('%s?section=published' % reverse('blog_manage_bulk'), params, follow=True)
        self.blogs[0] = Blog.objects.get(id=self.blogs[0].id)
        self.assertTrue(self.blogs[0].trash)
        self.blogs[1] = Blog.objects.get(id=self.blogs[1].id)
        self.assertFalse(self.blogs[1].trash)
        self.blogs[2] = Blog.objects.get(id=self.blogs[2].id)
        self.assertTrue(self.blogs[2].trash)
        self.assertRedirects(response, reverse('blog_manage_published'))
        self.client.logout()

    def test_bulk_action_trash_own_blog_on_draft_section_post_by_authenticated_user(self):
        self.client.login(username=self.john.username, password='1234')
        params = {
            'op': 'trash',
            'blog_id': [self.blogs[1].id, self.blogs[2].id]
        }
        response = self.client.post('%s?section=draft' % reverse('blog_manage_bulk'), params, follow=True)
        self.blogs[0] = Blog.objects.get(id=self.blogs[0].id)
        self.assertFalse(self.blogs[0].trash)
        self.blogs[1] = Blog.objects.get(id=self.blogs[1].id)
        self.assertTrue(self.blogs[1].trash)
        self.blogs[2] = Blog.objects.get(id=self.blogs[2].id)
        self.assertTrue(self.blogs[2].trash)
        self.assertRedirects(response, reverse('blog_manage_draft'))
        self.client.logout()

    def test_bulk_action_trash_other_blog_post_by_authenticated_user(self):
        self.client.login(username=self.john.username, password='1234')
        params = {
            'op': 'trash',
            'blog_id': [self.blogs[3].id, self.blogs[4].id]
        }
        response = self.client.post(reverse('blog_manage_bulk'), params, follow=True)
        self.blogs[3] = Blog.objects.get(id=self.blogs[3].id)
        self.assertFalse(self.blogs[3].trash)
        self.blogs[4] = Blog.objects.get(id=self.blogs[4].id)
        self.assertFalse(self.blogs[4].trash)
        self.client.logout()

    def test_bulk_action_trash_other_blog_post_by_staff_user(self):
        self.client.login(username=self.staff.username, password='1234')
        params = {
            'op': 'trash',
            'blog_id': [self.blogs[3].id, self.blogs[4].id]
        }
        response = self.client.post(reverse('blog_manage_bulk'), params, follow=True)
        self.blogs[3] = Blog.objects.get(id=self.blogs[3].id)
        self.assertTrue(self.blogs[3].trash)
        self.blogs[4] = Blog.objects.get(id=self.blogs[4].id)
        self.assertTrue(self.blogs[4].trash)
        self.client.logout()

    def test_bulk_action_restore_own_blog_by_authenticated_user(self):
        self.blogs[0].trash = True
        self.blogs[0].save()
        self.blogs[1].trash = True
        self.blogs[1].save()
        self.blogs[2].trash = True
        self.blogs[2].save()
        self.client.login(username=self.john.username, password='1234')
        params = {
            'op': 'restore',
            'blog_id': [self.blogs[0].id, self.blogs[1].id, self.blogs[2].id]
        }
        response = self.client.post(reverse('blog_manage_bulk'), params, follow=True)
        self.blogs[0] = Blog.objects.get(id=self.blogs[0].id)
        self.assertFalse(self.blogs[0].trash)
        self.blogs[1] = Blog.objects.get(id=self.blogs[1].id)
        self.assertFalse(self.blogs[1].trash)
        self.blogs[2] = Blog.objects.get(id=self.blogs[2].id)
        self.assertFalse(self.blogs[2].trash)
        self.client.logout()

    def test_bulk_action_restore_redirect_by_authenticated_user(self):
        self.client.login(username=self.john.username, password='1234')
        params = {
            'op': 'restore',
            'blog_id': [self.blogs[0].id, self.blogs[1].id, self.blogs[2].id]
        }
        response = self.client.post('%s?section=trash' % reverse('blog_manage_bulk'), params, follow=True)
        self.assertRedirects(response, reverse('blog_manage_trash'))
        self.client.logout()

    def test_bulk_action_delete_own_trashed_blog_by_authenticated_user(self):
        self.blogs[0].trash = True
        self.blogs[0].save()
        self.blogs[1].trash = True
        self.blogs[1].save()
        self.blogs[2].trash = True
        self.blogs[2].save()
        self.client.login(username=self.john.username, password='1234')
        params = {
            'op': 'delete',
            'blog_id': [self.blogs[0].id, self.blogs[1].id, self.blogs[2].id]
        }
        response = self.client.post(reverse('blog_manage_bulk'), params, follow=True)
        with self.assertRaises(Blog.DoesNotExist):
            Blog.objects.get(id=self.blogs[0].id)
        with self.assertRaises(Blog.DoesNotExist):
            Blog.objects.get(id=self.blogs[1].id)
        with self.assertRaises(Blog.DoesNotExist):
            Blog.objects.get(id=self.blogs[2].id)
        self.client.logout()

    def test_bulk_action_delete_own_not_trash_blog_by_authenticated_user(self):
        self.client.login(username=self.john.username, password='1234')
        params = {
            'op': 'delete',
            'blog_id': [self.blogs[0].id, self.blogs[1].id, self.blogs[2].id]
        }
        response = self.client.post(reverse('blog_manage_bulk'), params, follow=True)
        self.assertTrue(type(Blog.objects.get(id=self.blogs[0].id)) is Blog)
        self.assertTrue(type(Blog.objects.get(id=self.blogs[1].id)) is Blog)
        self.assertTrue(type(Blog.objects.get(id=self.blogs[2].id)) is Blog)
        self.client.logout()

    def test_sort_links_displayed_on_all_section_by_default(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage'))
        self.assertContains(response, '%s?sort=title&order=asc' % reverse('blog_manage'))
        self.assertContains(response, '%s?sort=created&order=asc' % reverse('blog_manage'))
        self.assertContains(response, '%s?sort=num_loves&order=asc' % reverse('blog_manage'))
        self.assertContains(response, '%s?sort=num_views&order=asc' % reverse('blog_manage'))
        self.client.logout()

    def test_sort_links_displayed_on_all_section_when_order_by_asc(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get('%s?sort=title&order=asc' % reverse('blog_manage'))
        self.assertContains(response, '%s?sort=title&order=desc' % reverse('blog_manage'))
        self.assertContains(response, '%s?sort=created&order=desc' % reverse('blog_manage'))
        self.assertContains(response, '%s?sort=num_loves&order=desc' % reverse('blog_manage'))
        self.assertContains(response, '%s?sort=num_views&order=desc' % reverse('blog_manage'))
        self.client.logout()

    def test_sort_title_by_desc(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get('%s?sort=title&order=desc' % reverse('blog_manage'))
        self.assertEqual(response.context['blogs'][0], self.blogs[2])
        self.assertEqual(response.context['blogs'][1], self.blogs[1])
        self.assertEqual(response.context['blogs'][2], self.blogs[0])
        self.client.logout()

    def test_sort_title_by_asc(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get('%s?sort=title&order=asc' % reverse('blog_manage'))
        self.assertEqual(response.context['blogs'][0], self.blogs[0])
        self.assertEqual(response.context['blogs'][1], self.blogs[1])
        self.assertEqual(response.context['blogs'][2], self.blogs[2])
        self.client.logout()

    def test_sort_date_by_desc(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get('%s?sort=created&order=desc' % reverse('blog_manage'))
        self.assertEqual(response.context['blogs'][0], self.blogs[2])
        self.assertEqual(response.context['blogs'][1], self.blogs[1])
        self.assertEqual(response.context['blogs'][2], self.blogs[0])
        self.client.logout()

    def test_sort_date_by_asc(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get('%s?sort=created&order=asc' % reverse('blog_manage'))
        self.assertEqual(response.context['blogs'][0], self.blogs[0])
        self.assertEqual(response.context['blogs'][1], self.blogs[1])
        self.assertEqual(response.context['blogs'][2], self.blogs[2])
        self.client.logout()

    def test_sort_loves_by_desc(self):
        Love.objects.create(blog=self.blogs[1], user=self.john)
        Love.objects.create(blog=self.blogs[1], user=self.staff)
        Love.objects.create(blog=self.blogs[2], user=self.john)
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get('%s?sort=num_loves&order=desc' % reverse('blog_manage'))
        self.assertEqual(response.context['blogs'][0], self.blogs[1])
        self.assertEqual(response.context['blogs'][1], self.blogs[2])
        self.assertEqual(response.context['blogs'][2], self.blogs[0])
        self.client.logout()

    def test_sort_loves_by_asc(self):
        Love.objects.create(blog=self.blogs[1], user=self.john)
        Love.objects.create(blog=self.blogs[1], user=self.staff)
        Love.objects.create(blog=self.blogs[2], user=self.john)
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get('%s?sort=num_loves&order=asc' % reverse('blog_manage'))
        self.assertEqual(response.context['blogs'][0], self.blogs[0])
        self.assertEqual(response.context['blogs'][1], self.blogs[2])
        self.assertEqual(response.context['blogs'][2], self.blogs[1])
        self.client.logout()

    def test_sort_views_by_desc(self):
        self.client.login(username=self.john.username, password='1234')
        self.client.get(reverse('blog_view', args=[self.blogs[0].id]))
        self.client.get(reverse('blog_view', args=[self.blogs[2].id]))
        self.client.get(reverse('blog_view', args=[self.blogs[2].id]))
        self.client.get(reverse('blog_view', args=[self.blogs[2].id]))
        response = self.client.get('%s?sort=num_views&order=desc' % reverse('blog_manage'))
        self.assertEqual(response.context['blogs'][0], self.blogs[2])
        self.assertEqual(response.context['blogs'][1], self.blogs[0])
        self.assertEqual(response.context['blogs'][2], self.blogs[1])
        self.client.logout()

    def test_sort_views_by_asc(self):
        self.client.login(username=self.john.username, password='1234')
        self.client.get(reverse('blog_view', args=[self.blogs[0].id]))
        self.client.get(reverse('blog_view', args=[self.blogs[2].id]))
        self.client.get(reverse('blog_view', args=[self.blogs[2].id]))
        self.client.get(reverse('blog_view', args=[self.blogs[2].id]))
        response = self.client.get('%s?sort=num_views&order=asc' % reverse('blog_manage'))
        self.assertEqual(response.context['blogs'][0], self.blogs[1])
        self.assertEqual(response.context['blogs'][1], self.blogs[0])
        self.assertEqual(response.context['blogs'][2], self.blogs[2])
        self.client.logout()

    def test_sort_links_displayed_on_published_section_by_default(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage_published'))
        self.assertContains(response, '%s?sort=title&order=asc' % reverse('blog_manage_published'))
        self.assertContains(response, '%s?sort=created&order=asc' % reverse('blog_manage_published'))
        self.assertContains(response, '%s?sort=num_loves&order=asc' % reverse('blog_manage_published'))
        self.assertContains(response, '%s?sort=num_views&order=asc' % reverse('blog_manage_published'))
        self.client.logout()

    def test_sort_links_displayed_on_published_section_when_orderby_asc(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get('%s?sort=title&order=asc' % reverse('blog_manage_published'))
        self.assertContains(response, '%s?sort=title&order=desc' % reverse('blog_manage_published'))
        self.assertContains(response, '%s?sort=created&order=desc' % reverse('blog_manage_published'))
        self.assertContains(response, '%s?sort=num_loves&order=desc' % reverse('blog_manage_published'))
        self.assertContains(response, '%s?sort=num_views&order=desc' % reverse('blog_manage_published'))
        self.client.logout()

    def test_sort_links_displayed_on_draft_section_by_default(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get(reverse('blog_manage_draft'))
        self.assertContains(response, '%s?sort=title&order=asc' % reverse('blog_manage_draft'))
        self.assertContains(response, '%s?sort=created&order=asc' % reverse('blog_manage_draft'))
        self.assertContains(response, '%s?sort=num_loves&order=asc' % reverse('blog_manage_draft'))
        self.assertContains(response, '%s?sort=num_views&order=asc' % reverse('blog_manage_draft'))
        self.client.logout()

    def test_sort_links_displayed_on_draft_section_when_orderby_asc(self):
        self.client.login(username=self.john.username, password='1234')
        response = self.client.get('%s?sort=title&order=asc' % reverse('blog_manage_draft'))
        self.assertContains(response, '%s?sort=title&order=desc' % reverse('blog_manage_draft'))
        self.assertContains(response, '%s?sort=created&order=desc' % reverse('blog_manage_draft'))
        self.assertContains(response, '%s?sort=num_loves&order=desc' % reverse('blog_manage_draft'))
        self.assertContains(response, '%s?sort=num_views&order=desc' % reverse('blog_manage_draft'))
        self.client.logout()

