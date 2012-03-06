from account.models import Account, AccountKey
from django.test import TestCase
from django.contrib.auth.models import User
from tests import factory

import settings

class TestAccount(TestCase):
    def setUp(self):
        self.staff = factory.create_user('staff@example.com', 'staff@example.com', 'staff', 'John', 'Doe')
        self.staff.is_staff = True
        self.staff.save()
        self.user = factory.create_user('tester2@example.com', 'tester2@example.com', 'testuser2', 'Panudate', 'Vasinwattana')
        self.inactive_user1 = factory.create_user('inactivetest1@example.com', 'inactivetest1@example.com', 'inactivetest1')
        self.inactive_user1.is_active = False
        self.inactive_user1.save()
        self.inactive_user2 = factory.create_user('inactivetest2@example.com', 'inactivetest2@example.com', 'inactivetest2')
        self.inactive_user2.is_active = False
        self.inactive_user2.save()
    
    def tearDown(self):
        pass
    
    def test_account_login_anonymous(self):
        response = self.client.get('/account/login/')
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
    
    def test_account_login_authenticated(self):
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

        self.client.login(username='staff@example.com', password='staff')
        response = self.client.get('/account/invite/')
        self.assertEquals(200, response.status_code)
        self.client.logout()
        
    def test_account_invite_new_user(self):
        self.client.login(username='staff@example.com', password='staff')
        invite = 'testnewuser@example.com, testnewuser2@example.com'
        response = self.client.post('/account/invite/', {'invite': invite})
        self.assertContains(response, 'Sending email invite. you can see list of user invited in user managment.')
        
        testnewuser = User.objects.get(username='testnewuser@example.com')
        testnewuser2 = User.objects.get(username='testnewuser2@example.com')
        self.assertEquals(False, testnewuser.is_active)
        self.assertEquals(False, testnewuser2.is_active)
        self.client.logout()
    
    def test_account_invite_exists_user_inactive(self):    
        account_key1 = AccountKey.objects.get(user=self.inactive_user1)
        account_key2 = AccountKey.objects.get(user=self.inactive_user2)
        
        key1 = account_key1.key
        key2 = account_key2.key
        
        self.client.login(username='staff@example.com', password='staff')
        invite = 'inactivetest1@example.com, inactivetest2@example.com'
        response = self.client.post('/account/invite/', {'invite': invite})
        self.assertContains(response, 'Sending email invite. you can see list of user invited in user managment.')
        
        account_key1 = AccountKey.objects.get(user=self.inactive_user1)
        account_key2 = AccountKey.objects.get(user=self.inactive_user2)
        self.assertNotEquals(key1, account_key1.key)
        self.assertNotEquals(key2, account_key2.key)
        self.client.logout()
        