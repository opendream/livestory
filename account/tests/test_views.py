from account.models import Account, AccountKey
from django.test import TestCase
from tests import factory

import settings

class TestAccount(TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_account_login_anonymous(self):
        response = self.client.get('/account/login/')
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
    
    def test_account_login_authenticated(self):
        factory.create_user('tester2@example.com', 'tester2@example.com', 'testuser2', 'Panudate', 'Vasinwattana')
        self.client.login(username='tester2@example.com', password='testuser2')
        response = self.client.get('/account/login/')
        # self.assertRedirects(response, '/')
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')