from account.models import Account, AccountKey
from django.test import TestCase
from django.contrib.auth.models import User
from tests import factory

from django.conf import settings
from override_settings import override_settings
import shutil

@override_settings(PRIVATE=False)
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
        response = self.client.post('/account/invite/', {'invite': invite}, follow=True)
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
        response = self.client.post('/account/invite/', {'invite': invite}, follow=True)
        self.assertContains(response, 'Sending email invite. you can see list of user invited in user managment.')
        
        account_key1 = AccountKey.objects.get(user=self.inactive_user1)
        account_key2 = AccountKey.objects.get(user=self.inactive_user2)
        self.assertNotEquals(key1, account_key1.key)
        self.assertNotEquals(key2, account_key2.key)
        self.client.logout()
    
    def test_account_invite_exists_active_user(self):
        self.client.login(username='staff@example.com', password='staff')
        invite = 'tester2@example.com, staff@example.com'
        response = self.client.post('/account/invite/', {'invite': invite}, follow=True)
        self.assertContains(response, 'Email user has joined : tester2@example.com, staff@example.com')
        
        tester2 = User.objects.get(username='tester2@example.com')
        staff = User.objects.get(username='staff@example.com')
        self.assertEquals(True, tester2.is_active)
        self.assertEquals(True, staff.is_active)
        self.client.logout()
    
    def test_account_invite_invalid_email(self):
        self.client.login(username='staff@example.com', password='staff')
        invite = 'testuser, www.google.com, tester bah bah, mail @com, testuser@example, testuser@.com'
        response = self.client.post('/account/invite/', {'invite': invite}, follow=True)
        self.assertContains(response, 'Email format is invalid : testuser, www.google.com, tester bah bah, mail @com, testuser@example, testuser@.com')
        self.client.logout()
    
    def test_account_activate(self):
        self.client.login(username='staff@example.com', password='staff')
        invite = 'testactivate@example.com'
        response = self.client.post('/account/invite/', {'invite': invite}, follow=True)
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

@override_settings(PRIVATE=False)
class TestCreateAccount(TestCase):
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
        self.client.login(username='staff@example.com', password='staff')
    
    def tearDown(self):
        pass
    
    def test_account_profile_create__get(self):
        response = self.client.get('/account/profile/create/')
        assert '<input id="id_username" type="text" class="span3" name="username" />' in response.content
        assert '<input id="id_password1" type="password" class="span3" name="password1" />' in response.content
        assert '<input id="id_password2" type="password" class="span3" name="password2" />' in response.content
        assert '<input id="id_firstname" type="text" class="span3" name="firstname" maxlength="200" />' in response.content
        assert '<input id="id_lastname" type="text" class="span3" name="lastname" maxlength="200" />' in response.content
        assert '<select name="timezone" id="id_timezone">' in response.content
        assert '<option value="UTC" selected="selected">UTC</option>' in response.content

    def test_account_profile_create__post_saved(self):
        response = self.client.post('/account/profile/create/', {'username': 'test@example.com', 'password1': 'password', 'password2': 'password', 'timezone': 'UTC'})
        self.assertContains(response, 'New profile created.')
        user = User.objects.get(username='test@example.com')
        self.assertTrue(user.account)

    def test_account_profile_create_post_invalid_username(self):
        response = self.client.post('/account/profile/create/', {'username': 'test'})
        self.assertContains(response, 'Please correct error(s) below.')
        self.assertContains(response, '<input id="id_username" type="text" class="span3" value="test" name="username" />')
        self.assertContains(response, '<span class="help-inline">* Enter a valid e-mail address.</span>')

@override_settings(PRIVATE=False)
class TestViewUserProfile(TestCase):
    def setUp(self):
        self.staff = factory.create_user('staff@example.com', 'staff@example.com', 'staff', 'John', 'Doe')
        self.staff.is_staff = True
        self.staff.save()
        self.user1 = factory.create_user('tester1@example.com', 'tester1@example.com', 'testuser1', 'Panudate', 'Vasinwattana')
        factory.create_blog(user=self.user1)

        self.user2 = factory.create_user('tester2@example.com', 'tester2@example.com', 'testuser2', 'Tavee', 'Khunbida')
        factory.create_blog(user=self.user2)
        factory.create_blog(user=self.user2)
        factory.create_blog(user=self.user2)
        factory.create_blog(user=self.user2)        
        factory.create_blog(user=self.user2)
        factory.create_blog(user=self.user2)
        factory.create_blog(user=self.user2)
        factory.create_blog(user=self.user2)
        factory.create_blog(user=self.user2)
        
        self.client.login(username='staff@example.com', password='staff')
    
    def tearDown(self):
        pass
    
    def test_user_profile_view__get_no_blogs_profile(self):
        user = User.objects.get(username='staff@example.com')
        response = self.client.get('/account/profile/%s/view/' % user.id)
        self.assertContains(response, '<span class="profile-name">John &nbsp; Doe</span>')
        self.assertContains(response, '<span class="profile-email grey">staff@example.com</span>')
        self.assertContains(response, '<span class="count-num">0</span>')
        self.assertContains(response, 'No photos found.')

    def test_user_profile_view__get_one_blog_profile(self):
        user = User.objects.get(username='tester1@example.com')
        response = self.client.get('/account/profile/%s/view/' % user.id)
        self.assertContains(response, '<span class="count-num">1</span>')
        self.assertContains(response, '<span class="grey">Photo</span>')
        self.assertContains(response, '<span class="mood-icon-s mood-happy-s">Mood</span><span class="location">Bangkok, Thailand</span>')

    def test_user_profile_view_get_blogs_profile_with_pagination(self):
        user = User.objects.get(username='tester2@example.com')
        response = self.client.get('/account/profile/%s/view/' % user.id)
        self.assertContains(response, '<span class="count-num">9</span>')
        self.assertContains(response, '<span class="grey">Photos</span>')
        self.assertContains(response, '<span class="mood-icon-s mood-happy-s">Mood</span><span class="location">Bangkok, Thailand</span>')
        self.assertContains(response, '<li><a href="?page=2">2</a></li>')

@override_settings(PRIVATE=False)
class TestEditUserProfile(TestCase):
    def setUp(self):
        self.staff = factory.create_user('staff@example.com', 'staff@example.com', 'staff', 'John', 'Doe')
        self.staff.is_staff = True
        self.staff.save()

        self.user = factory.create_user('tester@example.com', 'tester@example.com', 'testuser', 'Panudate', 'Vasinwattana')

        self.client.login(username='staff@example.com', password='staff')

    def tearDown(self):
        self.client.logout()

    def test_user_profile_edit__get(self):
        user = User.objects.get(username='tester@example.com')
        response = self.client.get('/account/profile/%s/edit/' % user.id)
        self.assertContains(response, '<span class="grey label-inline-form">tester@example.com</span>')
        self.assertContains(response, '<input name="firstname" value="Panudate" class="span3" maxlength="200" type="text" id="id_firstname" />')
        self.assertContains(response, '<input name="lastname" value="Vasinwattana" class="span3" maxlength="200" type="text" id="id_lastname" />')
        self.assertContains(response, '<input id="id_password" type="password" class="span3" name="password" maxlength="200" />')
        self.assertContains(response, '<input id="id_confirm_password" type="password" class="span3" name="confirm_password" maxlength="200" />')
        self.assertContains(response, '<select name="timezone" id="id_timezone">')
        self.assertContains(response, '<input checked="checked" type="checkbox" name="is_active" id="id_is_active" />')
        self.assertContains(response, '<button type="submit" class="btn-green">Update Profile</button>')

    def test_user_profile_edit__save(self):
        tz = 'Africa/Abidjan'
        user = User.objects.get(username='tester@example.com')
        response = self.client.post('/account/profile/%s/edit/' % user.id, {
                'firstname': 'Panudate', 
                'lastname': 'Vasinwattana',
                'timezone': tz,
                'is_active': True}
        )
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'User profile has been updated.')
        user2 = User.objects.get(username='tester@example.com')
        user2_profile = user2.get_profile()
        self.assertEquals(user2_profile.timezone, tz)

    def test_user_profile_edit__activate_user(self):
        user = User.objects.get(username='tester@example.com')
        user.is_active = False
        user.save()

        response = self.client.post('/account/profile/%s/edit/' % user.id, {'is_active': True})
        self.assertEquals(200, response.status_code)
        # check user is activated from database
        user2 = User.objects.get(username='tester@example.com')
        assert user2.is_active

    def test_user_profile_edit__block_user(self):
        user = User.objects.get(username='tester@example.com')
        assert user.is_active
        response = self.client.post('/account/profile/%s/edit/' % user.id, {'is_active': False})
        self.assertEquals(200, response.status_code)
        # check user is blocked from database
        user2 = User.objects.get(username='tester@example.com')
        assert user2.is_active == False

@override_settings(PRIVATE=False)
class TestManageUserBulk(TestCase):
    def setUp(self):
        self.staff = factory.create_user('staff@example.com', 'staff@example.com', 'staff', 'John', 'Doe')
        self.staff.is_staff = True
        self.staff.save()

        self.user1 = factory.create_user('tester1@example.com', 'tester1@example.com', 'testuser1', 'Panudate', 'Vasinwattana')
        self.user2 = factory.create_user('tester2@example.com', 'tester2@example.com', 'testuser2', 'Tom', 'Hank')
        
        self.client.login(username='staff@example.com', password='staff')

    def tearDown(self):
        self.client.logout()

    def test_user_manage_bulk__get(self):
        resp = self.client.get('/account/users/manage/')
        self.assertContains(resp, '<option value="block">Block user</option>')
        self.assertContains(resp, '<input type="submit" value="Apply" class="btn-grey">')
        self.assertContains(resp, 'Tom Hank')
        self.assertContains(resp, 'Panudate Vasinwattana')

    def test_user_manage_bulk_post_block_users(self):
        user1 = User.objects.get(username='tester1@example.com')
        user2 = User.objects.get(username='tester2@example.com')
        params = {
            'op': 'block',
            'user_id': [user1.id, user2.id]
        }
        self.client.post('/account/users/bulk/', params, follow=True)
        user1 = User.objects.get(username='tester1@example.com')
        user2 = User.objects.get(username='tester2@example.com')
        assert user1.is_active == False
        assert user2.is_active == False
    
    def test_user_manage_bulk_post_unblock_users(self):
        user1 = User.objects.get(username='tester1@example.com')
        user1.is_active = False
        user1.save()

        user2 = User.objects.get(username='tester2@example.com')
        user2.is_active = False
        user2.save()
        
        assert user1.is_active == False
        assert user2.is_active == False
        params = {
            'op': 'unblock',
            'user_id': [user1.id, user2.id]
        }
        self.client.post('/account/users/bulk/', params, follow=True)
        user1 = User.objects.get(username='tester1@example.com')
        user2 = User.objects.get(username='tester2@example.com')
        assert user1.is_active
        assert user2.is_active
    