from account.models import Account, AccountKey
from django.test import TestCase
from django.contrib.auth.models import User
from tests import factory

from django.conf import settings

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
        self.assertTemplateUsed(response, 'registration/login.html')
    
    def test_account_login_authenticated(self):
        self.client.login(username='tester2@example.com', password='testuser2')
        response = self.client.get('/account/login/')
        # self.assertRedirects(response, '/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.client.logout()
    
    def test_account_invite_accessment(self):
        response = self.client.get('/account/invite/')
        self.assertEquals(403, response.status_code)

        self.client.login(username='staff@example.com', password='staff')
        response = self.client.get('/account/invite/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'account/account_invite.html')
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
    
    def test_account_invite_exists_inactive_user(self):    
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
    
    def test_account_invite_exists_active_user(self):
        self.client.login(username='staff@example.com', password='staff')
        invite = 'tester2@example.com, staff@example.com'
        response = self.client.post('/account/invite/', {'invite': invite})
        self.assertContains(response, 'Email user has joined : tester2@example.com, staff@example.com')
        
        tester2 = User.objects.get(username='tester2@example.com')
        staff = User.objects.get(username='staff@example.com')
        self.assertEquals(True, tester2.is_active)
        self.assertEquals(True, staff.is_active)
        self.client.logout()
    
    def test_account_invite_invalid_email(self):
        self.client.login(username='staff@example.com', password='staff')
        invite = 'testuser, www.google.com, tester bah bah, mail @com, testuser@example, testuser@.com'
        response = self.client.post('/account/invite/', {'invite': invite})
        self.assertContains(response, 'Email format is invalid : testuser, www.google.com, tester bah bah, mail @com, testuser@example, testuser@.com')
        self.client.logout()
    
    def test_account_activate(self):
        self.client.login(username='staff@example.com', password='staff')
        invite = 'testactivate@example.com'
        response = self.client.post('/account/invite/', {'invite': invite})
        self.client.logout()
        
        account_key = AccountKey.objects.get(user__username='testactivate@example.com')
        response = self.client.get('/account/activate/%s/' % account_key.key, follow=True)
        current_user = User.objects.get(id=self.client.session.get('_auth_user_id'))
        
        self.assertRedirects(response, '/account/profile/edit/?activate=1')
        self.assertEquals(True, bool(self.client.session))
        self.assertEquals('testactivate@example.com', current_user.username)
        self.assertContains(response, 'Password must be update')
        self.assertContains(response, 'Password must be confirm')
        self.assertContains(response, 'testactivate@example.com')
        self.client.logout()
    
    def test_account_invalid_activate_key(self):
        response = self.client.get('/account/activate/invalidkey/', follow=True)
        self.assertTemplateUsed(response, 'account/account_key_error.html')
        
    def test_account_profile_edit_get(self):
        response = self.client.get('/account/profile/edit/')
        self.assertEquals(403, response.status_code)
        
        self.client.login(username='staff@example.com', password='staff')
        response = self.client.get('/account/profile/edit/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'account/account_profile_edit.html')
        self.client.logout()
    
    def test_account_profile_edit_post_no_password(self):
        self.client.login(username='staff@example.com', password='staff')
        response = self.client.post('/account/profile/edit/', {'firstname': 'Alan', 'lastname': 'Smith', 'password': '', 'confirm_password': '', 'timezone': 'Asia/Bangkok'})
        current_user = User.objects.get(id=self.client.session.get('_auth_user_id'))
        self.assertTemplateUsed(response, 'account/account_profile_edit.html')
        self.assertEquals('Asia/Bangkok', current_user.get_profile().timezone)
        self.assertEquals('Smith', current_user.get_profile().lastname)
        self.assertEquals('Smith', current_user.get_profile().lastname)
        self.assertEquals(True, current_user.check_password('staff'))
        self.client.logout()
    
    def test_account_profile_edit_post_new_password(self):
        self.client.login(username='staff@example.com', password='staff')
        response = self.client.post('/account/profile/edit/', {'firstname': 'Steve', 'lastname': 'Jobs', 'password': 'Apple', 'confirm_password': 'Apple', 'timezone': 'Europe/Berlin'})
        current_user = User.objects.get(id=self.client.session.get('_auth_user_id'))
        self.assertTemplateUsed(response, 'account/account_profile_edit.html')
        self.assertEquals('Europe/Berlin', current_user.get_profile().timezone)
        self.assertEquals('Steve', current_user.get_profile().firstname)
        self.assertEquals('Jobs', current_user.get_profile().lastname)
        self.assertEquals(True, current_user.check_password('Apple'))
        
        self.client.logout()
        
    def test_account_profile_edit_post_missmatch_password(self):
        self.client.login(username='staff@example.com', password='staff')
        response = self.client.post('/account/profile/edit/', {'firstname': 'Steve', 'lastname': 'Jobs', 'password': 'Apple', 'confirm_password': 'APPLE', 'timezone': 'Europe/Berlin'})
        current_user = User.objects.get(id=self.client.session.get('_auth_user_id'))
        self.assertTemplateUsed(response, 'account/account_profile_edit.html')
        self.assertEquals('Asia/Bangkok', current_user.get_profile().timezone)
        self.assertEquals('John', current_user.get_profile().firstname)
        self.assertEquals('Doe', current_user.get_profile().lastname)
        self.assertEquals(True, current_user.check_password('staff'))
        self.assertContains(response, 'Password not match')

        self.client.logout()
    