from django.test import TestCase

from tests import factory
from override_settings import override_settings

@override_settings(PRIVATE=False)
class TestBlogSearch(TestCase):
	def setup(self):
		self.user = factory.create_user()
		#self.category = factory.create_category('Food', 'food')
		#self.location = factory.create_location('Thailand', 'Bangkok')

	def teardown(self):
		pass

	def test_search_blog__get_no_keyword(self):
		response = self.client.get('/blog/search/', {'keyword': ''})
		self.assertContains(response, 'No keyword')

	def test_search_blog__post_no_result(self):
		response = self.client.post('/blog/search/', {'keyword': 'food'})
		self.assertContains(response, 'No result')  

	def test_search_blog__post_with_result_no_pagination(self):
		response = self.client.post('/blog/search/', {'keyword': 'Donec'})
		self.assertNotContains(response, '<div class="pagination pagination-centered">')

	def test_search_blog__post_with_result_with_pagination(self):
		response = self.client.post('/blog/search/', {'keyword': 'Lorem'})
		print response.content
		self.assertContains(response, '<div class="pagination pagination-centered">')
		self.assertContains(response, '<a href="?keyword=Lorem&page=3">3</a>')

	def test_search_blog__post_with_result_case_insensitive(self):
		response1 = self.client.post('/blog/search/', {'keyword': 'Lorem'})
		response2 = self.client.post('/blog/search/', {'keyword': 'lorem'})
		self.assertEqual(response1.context['blogs'].count(), response2.context['blogs'].count())

	def test_search_blog__post_keyword_with_spaces(self):
		response1 = self.client.post('/blog/search/', {'keyword': ' Lorem  '})
		response2 = self.client.post('/blog/search/', {'keyword': 'Lorem'})
		self.assertEqual(response1.context['blogs'].count(), response2.context['blogs'].count())

