from django.test import TestCase
from django.core.urlresolvers import reverse

from blog.models import Blog
from tests import factory
from common import rm_user

class TestBlogComment(TestCase):
	fixtures = ['demo_data.json']

	def setUp(self):
		self.user = factory.create_user('test@example.com', 'test@example.com', 'test')
		self.blog1 = Blog.objects.get(id=1) # prepared by demo_data.json

	def tearDown(self):
		rm_user(self.user.id)

	def test_blog_comment(self):
		self.client.login(username='test@example.com', password='test')

		# post empty comment
		params = {}
		resp = self.client.post(reverse('add_blog_comment', args=[self.blog1.id]), params, follow=True)
		self.assertEquals(200, resp.status_code)
		self.assertTrue(resp.context['comments'].count() <= 0)

		# post someting
		params.update({'comment': 'Nice shot'})
		resp = self.client.post(reverse('add_blog_comment', args=[self.blog1.id]), params, follow=True)
		self.assertEquals(200, resp.status_code)
		self.assertTrue(resp.context['comments'].count() == 1)
		self.assertEquals('Nice shot', resp.context['comments'][0].comment)

		self.client.logout()