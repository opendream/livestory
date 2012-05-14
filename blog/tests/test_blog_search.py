import urllib

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from tests import factory
from override_settings import override_settings

from common.utilities import generate_username

class TestBlogSearch(TestCase):
    fixtures = ['demo_data.json']

    def setUp(self):
        self.TEST_USER_EMAIL = 'test@example.com'
        self.TEST_USER_PASSWORD = 'test'
        self.user = factory.create_user(generate_username(self.TEST_USER_EMAIL), self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_search_blog__by_anonymous(self):
        response = self.client.get(reverse('blog_search'), {'keyword': 'food'})
        if settings.PRIVATE:
            self.assertRedirects(response, '%s?next=%s%s' % (reverse('account_login'), reverse('blog_search'), urllib.quote_plus('?%s' % urllib.urlencode({'keyword': 'food'}))))
        else:
            self.assertEquals(200, response.status_code)

    def test_search_blog__by_authenticated_user(self):
        self.client.login(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)

        response = self.client.get(reverse('blog_search'), {'keyword': 'food'})
        self.assertEquals(200, response.status_code)

    def test_search_blog__get_no_keyword(self):
        if settings.PRIVATE:
            self.client.login(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)

        response = self.client.get(reverse('blog_search'), {'keyword': ''})
        self.assertContains(response, 'No keyword')

    def test_search_blog__post_no_result(self):
        if settings.PRIVATE:
            self.client.login(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)

        response = self.client.post(reverse('blog_search'), {'keyword': 'star'})
        self.assertContains(response, 'No result')

    def test_search_blog__post_with_result_no_pagination(self):
        if settings.PRIVATE:
            self.client.login(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)

        response = self.client.post(reverse('blog_search'), {'keyword': 'Donec'})
        self.assertNotContains(response, '<div class="pagination pagination-centered">')

    def test_search_blog__post_with_result_with_pagination(self):
        if settings.PRIVATE:
            self.client.login(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)

        response = self.client.post(reverse('blog_search'), {'keyword': 'is'})
        self.assertEquals(response.context['page_range'], [1, 2, 3])

    def test_search_blog__post_with_result_case_insensitive(self):
        if settings.PRIVATE:
            self.client.login(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)

        response1 = self.client.post('/blog/search/', {'keyword': 'Lorem'})
        response2 = self.client.post('/blog/search/', {'keyword': 'lorem'})
        self.assertEqual(response1.context['blogs'].count(), response2.context['blogs'].count())

    def test_search_blog__post_keyword_with_spaces(self):
        if settings.PRIVATE:
            self.client.login(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)

        response1 = self.client.post('/blog/search/', {'keyword': ' Lorem  '})
        response2 = self.client.post('/blog/search/', {'keyword': 'Lorem'})
        self.assertEqual(response1.context['blogs'].count(), response2.context['blogs'].count())

