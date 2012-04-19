from django.test import TestCase

from tests import factory
from override_settings import override_settings

@override_settings(PRIVATE=False)
class TestBlogSearch(TestCase):
    def setup(self):
        self.user = factory.create_user('test@example.com', 'test@example.com', 'test')
        #self.category = factory.create_category('Food', 'food')
        #self.location = factory.create_location('Thailand', 'Bangkok')

    def teardown(self):
        pass

    def test_search_blog__get_no_keyword(self):
        self.client.login(username='test@example.com', password='test')
        response = self.client.get('/blog/search/', {'keyword': ''})
        self.assertContains(response, 'No keyword')
        self.client.logout()

    def test_search_blog__post_no_result(self):
        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/search/', {'keyword': 'food'})
        self.assertContains(response, 'No result')
        self.client.logout()

    def test_search_blog__post_with_result_no_pagination(self):
        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/search/', {'keyword': 'Donec'})
        self.assertNotContains(response, '<div class="pagination pagination-centered">')
        self.client.logout()

    def test_search_blog__post_with_result_with_pagination(self):
        self.client.login(username='test@example.com', password='test')
        response = self.client.post('/blog/search/', {'keyword': 'Lorem'})
        self.assertContains(response, '<div class="pagination pagination-centered">')
        self.assertContains(response, '<a href="?keyword=Lorem&page=3">3</a>')
        self.client.logout()

    def test_search_blog__post_with_result_case_insensitive(self):
        self.client.login(username='test@example.com', password='test')
        response1 = self.client.post('/blog/search/', {'keyword': 'Lorem'})
        response2 = self.client.post('/blog/search/', {'keyword': 'lorem'})
        self.assertEqual(response1.context['blogs'].count(), response2.context['blogs'].count())
        self.client.logout()

    def test_search_blog__post_keyword_with_spaces(self):
        print self.client.login(username='test@example.com', password='test')
        response1 = self.client.post('/blog/search/', {'keyword': ' Lorem  '})
        response2 = self.client.post('/blog/search/', {'keyword': 'Lorem'})
        self.assertEqual(response1.context['blogs'].count(), response2.context['blogs'].count())
        self.client.logout()

