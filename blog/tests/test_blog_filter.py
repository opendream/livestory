from django.test import TestCase
from django.core.urlresolvers import reverse

from tests import factory

class TestBlogFilter(TestCase):
	fixtures = ['demo_data.json']

	def setUp(self):
		self.url = reverse('blog_place')
		self.user = factory.create_user('testuser1@example.com', 
										'testuser1@example.com', 
										'password', 'John', 'Doe 1', True)
		self.client.login(username='testuser1@example.com', 
			              password='password')

	def tearDown(self):
		self.client.logout()

	def test_blog_filtering_by_place(self):
		resp = self.client.get(self.url, {'country': 'Cambodia', 'city': 'Phnom Penh'})
		self.assertEquals(200, resp.status_code)
		self.assertTrue(len(resp.context['blogs']) > 0)

		blog1 = resp.context['blogs'][0]
		self.assertEquals('Cambodia', blog1.location.country)
		self.assertEquals('Phnom Penh', blog1.location.city)

	def test_blog_filtering_by_place_case_sensitive(self):
		resp = self.client.get(self.url, {'country': 'CAMBODIA', 'city': 'PHnoM PEnh'})
		self.assertEquals(200, resp.status_code)
		self.assertTrue(len(resp.context['blogs']) > 0)

		blog1 = resp.context['blogs'][0]
		self.assertEquals('Cambodia', blog1.location.country)
		self.assertEquals('Phnom Penh', blog1.location.city)

	def test_blog_filtering_by_country(self):
		resp = self.client.get(self.url, {'country': 'CaMbODiA'})
		self.assertEquals(200, resp.status_code)
		self.assertTrue(len(resp.context['blogs']) > 0)

		blog1 = resp.context['blogs'][0]
		self.assertEquals('Cambodia', blog1.location.country)

	def test_blog_filtering_by_city(self):
		resp = self.client.get(self.url, {'city': 'PHnoM PEnh'})
		self.assertEquals(200, resp.status_code)
		self.assertTrue(len(resp.context['blogs']) > 0)

		blog1 = resp.context['blogs'][0]
		self.assertEquals('Cambodia', blog1.location.country)
		self.assertEquals('Phnom Penh', blog1.location.city)

	def test_blog_filtering_by_place_partial(self):
		resp = self.client.get(self.url, {'country': 'Camb', 'city': '  PHnoM P'})
		self.assertEquals(200, resp.status_code)
		self.assertTrue(len(resp.context['blogs']) > 0)

		blog1 = resp.context['blogs'][0]
		self.assertEquals('Cambodia', blog1.location.country)
		self.assertEquals('Phnom Penh', blog1.location.city)