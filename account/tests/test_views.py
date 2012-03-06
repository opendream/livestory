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
        self.client.logout()
    
    def test_account_invite_accessment(self):
        response = self.client.get('/account/invite/')
        self.assertEquals(403, response.status_code)
        
        staff = factory.create_user('staff@example.com', 'staff@example.com', 'staff', 'John', 'Doe')
        staff.is_staff = True
        staff.save()
        self.client.login(username='staff@example.com', password='staff')
        response = self.client.get('/account/invite/')
        self.assertEquals(200, response.status_code)
        self.client.logout()