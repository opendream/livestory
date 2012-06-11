from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from account.models import UserProfile, UserInvitation
from override_settings import override_settings
from tests import factory
import shutil

@override_settings(PRIVATE=False)
class TestUserProfile(TestCase):
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
        response = self.client.get('/accounts/login/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'registration/login.html')
    
    def test_account_login_authenticated(self):
        self.client.login(username='tester2@example.com', password='testuser2')
        response = self.client.get('/accounts/login/')
        # self.assertRedirects(response, '/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.client.logout()
    
    def test_account_invite_accessment(self):
        response = self.client.get('/account/invite/')
        self.assertRedirects(response, '/accounts/login/?next=/account/invite/')

        self.client.login(username='staff@example.com', password='staff')
        response = self.client.get('/account/invite/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'account/account_invite.html')
        self.client.logout()
        
    def test_account_invite_new_user(self):
        self.client.login(username='staff@example.com', password='staff')
        invite = 'testnewuser@example.com, testnewuser2@example.com'
        response = self.client.post('/account/invite/', {'emails': invite}, follow=True)
        self.assertContains(response, '<span class="tags">Success</span> Sending invitation email(s).')
        
        testnewuser = UserInvitation.objects.get(email='testnewuser@example.com')
        testnewuser2 = UserInvitation.objects.get(email='testnewuser2@example.com')
        self.assertEquals(True, len(testnewuser.invitation_key) > 0)
        self.assertEquals(True, len(testnewuser2.invitation_key) > 0)
        self.client.logout()
    
    def test_account_invite_exists_users(self):
        self.client.login(username='staff@example.com', password='staff')
        invite = 'tester2@example.com, staff@example.com'
        response = self.client.post('/account/invite/', {'emails': invite}, follow=True)
        self.assertContains(response, 'Email user has joined : tester2@example.com, staff@example.com')
        
        tester2 = User.objects.get(username='tester2@example.com')
        staff = User.objects.get(username='staff@example.com')
        self.assertEquals(True, tester2.is_active)
        self.assertEquals(True, staff.is_active)
        self.client.logout()
    
    def test_account_invite_invalid_email(self):
        self.client.login(username='staff@example.com', password='staff')
        invite = 'testuser, www.google.com, tester bah bah, mail @com, testuser@example, testuser@.com'
        response = self.client.post('/account/invite/', {'emails': invite}, follow=True)
        self.assertContains(response, 'The following email(s) is invalid and has not been sent: testuser, www.google.com, tester bah bah, mail @com, testuser@example, testuser@.com')
        self.client.logout()
    
    def test_account_activate(self):
        self.client.login(username='staff@example.com', password='staff')
        invite_email = 'testactivate@example.com'
        response = self.client.post('/account/invite/', {'emails': invite_email}, follow=True)
        self.assertEquals(200, response.status_code)

        account_key = UserInvitation.objects.get(email=invite_email)
        response = self.client.get('/account/activate/%s/' % account_key.invitation_key, follow=True)
        self.assertEquals(200, response.status_code)

        response = self.client.post('/account/activate/%s/' % account_key.invitation_key, {'first_name': 'test_firstname',
                                                                                           'last_name': 'test_lastname',
                                                                                           'password': 'password',
                                                                                           'confirm_password': 'password'})
        self.assertEquals(302, response.status_code)
        self.client.logout()
    
    def test_account_invalid_activate_key(self):
        response = self.client.get('/account/activate/invalidkey/', follow=True)
        self.assertContains(response, 'Invitation key is invalid')
        
    def test_account_profile_edit_get(self):
        response = self.client.get('/account/profile/edit/')
        self.assertRedirects(response, '/accounts/login/?next=/account/profile/edit/')

        self.client.login(username='staff@example.com', password='staff')
        response = self.client.get('/account/profile/edit/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'account/account_profile_edit.html')
        self.client.logout()
    
    def test_account_profile_edit_post_no_password(self):
        self.client.login(username='staff@example.com', password='staff')
        response = self.client.post(reverse('account_profile_edit'), {'first_name': 'Alan', 
                                                                      'last_name': 'Smith', 
                                                                      'timezone': 'Asia/Bangkok'})
        self.assertContains(response, 'Your profile has been saved.')

        current_user = User.objects.get(id=self.client.session.get('_auth_user_id'))

        self.assertEquals('staff@example.com', current_user.email)
        self.assertEquals('Asia/Bangkok', current_user.get_profile().timezone)
        self.assertEquals('Alan', current_user.get_profile().first_name)
        self.assertEquals('Smith', current_user.get_profile().last_name)
        self.assertEquals(True, current_user.check_password('staff'))
        self.client.logout()
    
    def test_account_profile_edit_post_new_password(self):
        self.client.login(username='staff@example.com', password='staff')
        response = self.client.post('/account/profile/edit/', {'first_name': 'Steve', 'last_name': 'Jobs', 'password': 'Apple', 'confirm_password': 'Apple', 'timezone': 'Europe/Berlin'})
        print '_auth_user_id', self.client.session.get('_auth_user_id')
        current_user = User.objects.get(id=self.client.session.get('_auth_user_id'))
        self.assertTemplateUsed(response, 'account/account_profile_edit.html')
        self.assertEquals('staff@example.com', current_user.email)
        self.assertEquals('Europe/Berlin', current_user.get_profile().timezone)
        self.assertEquals('Steve', current_user.get_profile().first_name)
        self.assertEquals('Jobs', current_user.get_profile().last_name)
        self.assertEquals(True, current_user.check_password('Apple'))
        
        self.client.logout()
        
    def test_account_profile_edit_post_missmatch_password(self):
        self.client.login(username='staff@example.com', password='staff')
        response = self.client.post('/account/profile/edit/', {'first_name': 'Steve', 'last_name': 'Jobs', 'password': 'Apple', 'confirm_password': 'APPLE', 'timezone': 'Europe/Berlin'})
        current_user = User.objects.get(id=self.client.session.get('_auth_user_id'))
        self.assertTemplateUsed(response, 'account/account_profile_edit.html')
        self.assertEquals('Asia/Bangkok', current_user.get_profile().timezone)
        self.assertEquals('John', current_user.get_profile().first_name)
        self.assertEquals('Doe', current_user.get_profile().last_name)
        self.assertEquals(True, current_user.check_password('staff'))
        self.assertContains(response, 'Password not match')

        self.client.logout()

@override_settings(PRIVATE=False)
class TestCreateUserProfile(TestCase):
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
        assert '<input id="id_email" type="text" class="span3" name="email" maxlength="254" />' in response.content
        assert '<input id="id_password1" type="password" class="span3" name="password1" />' in response.content
        assert '<input id="id_password2" type="password" class="span3" name="password2" />' in response.content
        assert '<input id="id_first_name" type="text" class="span3" name="first_name" maxlength="200" />' in response.content
        assert '<input id="id_last_name" type="text" class="span3" name="last_name" maxlength="200" />' in response.content
        assert '<select name="timezone" id="id_timezone">' in response.content
        assert '<option value="UTC" selected="selected">UTC</option>' in response.content

    def test_account_profile_create__post_saved(self):
        response = self.client.post('/account/profile/create/', {'email': 'test@example.com', 'first_name': 'test', 'last_name': 'example', 'password1': 'password', 'password2': 'password', 'timezone': 'UTC'})
        self.assertEquals(302, response.status_code)
        user = User.objects.get(email='test@example.com')
        self.assertTrue(user.get_profile())

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
        print response.content
        self.assertContains(response, '<span class="profile-name">John Doe</span>')
        self.assertContains(response, '<span class="profile-email grey">staff@example.com</span>')
        self.assertContains(response, '<span class="count-num">0</span>')
        self.assertContains(response, 'No photos found.')

    def test_user_profile_view__get_one_blog_profile(self):
        user = User.objects.get(username='tester1@example.com')
        response = self.client.get('/account/profile/%s/view/' % user.id)
        self.assertContains(response, '<span class="count-num">1</span>')
        self.assertContains(response, '<span class="grey">Photo</span>')
        self.assertContains(response, '<span class="mood-icon-s mood-fun-s">Mood</span><span class="location">Bangkok, Thailand</span>')

    def test_user_profile_view_get_blogs_profile_with_pagination(self):
        user = User.objects.get(username='tester2@example.com')
        response = self.client.get('/account/profile/%s/view/' % user.id)
        self.assertContains(response, '<span class="count-num">9</span>')
        self.assertContains(response, '<span class="grey">Photos</span>')
        self.assertContains(response, '<span class="mood-icon-s mood-fun-s">Mood</span><span class="location">Bangkok, Thailand</span>')
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
        self.assertContains(response, '<input name="first_name" value="Panudate" class="span3" maxlength="200" type="text" id="id_first_name" />')
        self.assertContains(response, '<input name="last_name" value="Vasinwattana" class="span3" maxlength="200" type="text" id="id_last_name" />')
        self.assertContains(response, '<input id="id_password" type="password" class="span3" name="password" maxlength="200" />')
        self.assertContains(response, '<input id="id_confirm_password" type="password" class="span3" name="confirm_password" maxlength="200" />')
        self.assertContains(response, '<select name="timezone" id="id_timezone">')
        self.assertContains(response, '<input checked="checked" type="checkbox" name="is_active" id="id_is_active" />')
        self.assertContains(response, '<button type="submit" class="btn-green">Update Profile</button>')

    def test_user_profile_edit__save(self):
        tz = 'Africa/Abidjan'
        user = User.objects.get(username='tester@example.com')
        response = self.client.post('/account/profile/%s/edit/' % user.id, {
                'first_name': 'Panudate', 
                'last_name': 'Vasinwattana',
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

        post_url = reverse('user_profile_edit', args=[user.id])
        resp = self.client.post(post_url, {'is_active': True, 
                                           'first_name': user.get_profile().first_name, 
                                           'last_name': user.get_profile().last_name})
        self.assertEquals(200, resp.status_code)
        print resp.content
        # check user is activated from database
        user2 = User.objects.get(username='tester@example.com')
        assert user2.is_active

    def test_user_profile_edit__block_user(self):
        user = User.objects.get(username='tester@example.com')
        assert user.is_active
        post_url = reverse('user_profile_edit', args=[user.id])
        resp = self.client.post(post_url, {'is_active': False,
                                           'first_name': user.get_profile().first_name,
                                           'last_name': user.get_profile().last_name})
        self.assertEquals(200, resp.status_code)
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
    

@override_settings(PRIVATE=False)
class TestAccountSearch(TestCase):
    def setUp(self):
        self.staff = factory.create_user('staff@example.com', 'staff@example.com', 'staff', 'John', 'Doe')
        self.staff.is_staff = True
        self.staff.save()

        self.user1 = factory.create_user('tester1@example.com', 'tester1@example.com', 'testuser1', 'Panudate', 'Vasinwattana', 'head master', 'playplanet')
        self.user2 = factory.create_user('tester2@example.com', 'tester2@example.com', 'testuser2', 'Tom', 'Hank', 'movie master', 'hollywood')
        self.user2 = factory.create_user('tester3@example.com', 'tester3@example.com', 'testuser3', 'Tom', 'Jerry', 'cartoon master', 'workplanet')
        
        self.client.login(username='staff@example.com', password='staff')

    def tearDown(self):
        self.client.logout()

    def test_search_get(self):
        response = self.client.get(reverse('account_profile_search'))
        self.assertEquals(200, response.status_code)

    def test_search_no_result(self):
        response = self.client.get(reverse('account_profile_search'), {'account_keywords': ''})
        self.assertContains(response, 'No results')

    def test_search_result(self):
        #search first_name
        response = self.client.get(reverse('account_profile_search'), {'account_keywords': 'tom'})
        self.assertEquals(2, response.context['user_profile'].count())

        #search last_name
        response = self.client.get(reverse('account_profile_search'), {'account_keywords': 'jerry'})
        self.assertEquals(1, response.context['user_profile'].count())

        #search office_name
        response = self.client.get(reverse('account_profile_search'), {'account_keywords': 'planet'})
        self.assertEquals(2, response.context['user_profile'].count())

    def test_search_keyword_insensitive(self):
        response1 = self.client.get(reverse('account_profile_search'), {'account_keywords': 'PANUDATE'})
        response2 = self.client.get(reverse('account_profile_search'), {'account_keywords': 'PanudatE'})
        self.assertEquals(response1.context['user_profile'].count(), response2.context['user_profile'].count())

    def test_search_keyword_with_spaces(self):
        response1 = self.client.get(reverse('account_profile_search'), {'account_keywords': '   PANUDATE   '})
        response2 = self.client.get(reverse('account_profile_search'), {'account_keywords': 'PanudatE'})
        self.assertEquals(response1.context['user_profile'].count(), response2.context['user_profile'].count())
