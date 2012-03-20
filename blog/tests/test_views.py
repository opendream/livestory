from django.contrib.auth.models import User
from django.core.files.base import File as DjangoFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson as json

from blog.models import Blog, Love
from blog.views import blog_bulk_update_private
from blog.views import blog_bulk_update_public
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
            blog.delete()
        
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

