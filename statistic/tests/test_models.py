from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from override_settings import override_settings

from tests import factory, rm_user

from blog.models import Blog
from statistic.models import BlogViewHit, BlogViewSummary

@override_settings(PRIVATE=False)
class TestBaseData(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = factory.create_user('john.doe@example.com', 'john.doe@example.com', '1234', 'John', 'Doe')
        self.category = factory.create_category('Travel', 'travel')
        self.location = factory.create_location('Czech', 'Praque', 0, 0)
        self.blog = factory.create_blog('Visit Praque', self.user, self.category, self.location)

    def tearDown(self):
        #self.blog.delete()
        pass

class TestBlogViewHit(TestBaseData):
    def test_create_hit(self):
        self.client.login(username='john.doe@example.com', password='1234')
        hit = BlogViewHit.objects.create(blog=self.blog, sessionkey=self.client.session.session_key)
        self.assertQuerysetEqual(BlogViewSummary.objects.filter(blog=self.blog), ['<BlogViewSummary: %s has 1 hits>' % self.blog.title])

    def test_view_blog(self):
        self.client.login(username='john.doe@example.com', password='1234')
        response = self.client.get(reverse('blog_view', args=[self.blog.id]))
        self.assertQuerysetEqual(BlogViewSummary.objects.filter(blog=self.blog), ['<BlogViewSummary: %s has 1 hits>' % self.blog.title])
