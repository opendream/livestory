from django.conf import settings
from django.test import TestCase
from override_settings import override_settings

from tests import factory, rm_user

from account.models import UserProfile, UserInvitation


@override_settings(PRIVATE=False)
class TestUserProfile(TestCase):
    def setUp(self):
        self.users = [
            factory.create_user('tester1@example.com', 'tester1@example.com', 'testuser1', 'Nirut', 'Khemasakchai', True),
            factory.create_user('tester2@example.com', 'tester2@example.com', 'testuser2', 'Panudate', 'Vasinwattana')
        ]
        
    def tearDown(self):
         if self.users[0].get_profile().avatar:
            self.users[0].get_profile().avatar.delete()
         # rm_user(self.users[0].id)
         # rm_user(self.users[1].id)
        
    def test_get_fullname(self):
        self.assertEquals('Nirut Khemasakchai', self.users[0].get_profile().get_full_name())
        self.assertEquals('Panudate Vasinwattana', self.users[1].get_profile().get_full_name())
        
    # def test_get_image(self):

    #     account_has_image = self.users[0].get_profile()
    #     account_no_image = self.users[1].get_profile()
        
    #     self.assertEquals('static/img/default_user.png', account_no_image.get_avatar().path)
    #     self.assertEquals('%simages/account/%s/avatar.png' % (settings.MEDIA_ROOT, account_has_image.user.id), account_has_image.get_avatar().path)
    
    # def test_get_image_url(self):
    #     account_has_image = self.users[0].get_profile()
    #     account_no_image = self.users[1].get_profile()
    #     self.assertEquals('/media/images/account/%s/avatar.png' % account_has_image.user.id, account_has_image.get_avatar_url())
    #     self.assertEquals(None, account_no_image.get_avatar_url())
        
    def test_unicode(self):
        self.assertEquals('Nirut Khemasakchai', self.users[0].get_profile().__unicode__())
        self.assertEquals('Panudate Vasinwattana', self.users[1].get_profile().__unicode__())

class TestUserInvitation(TestCase):
    def setUp(self):
        self.users = [
            factory.create_user('tester1@example.com', 'tester1@example.com', 'testuser1', 'Nirut', 'Khemasakchai'),
            factory.create_user('tester2@example.com', 'tester2@example.com', 'testuser2', 'Panudate', 'Vasinwattana')
        ]

    def tearDown(self):
        for user in self.users:
            rm_user(user.id)
        
    def test_unicode(self):
        invite1 = UserInvitation.objects.create_invitation(email='test1@invitation.com', invited_by=self.users[0])
        invite2 = UserInvitation.objects.create_invitation(email='test2@invitation.com', invited_by=self.users[1])
        self.assertEquals('test1@invitation.com has key %s' % invite1.invitation_key, invite1.__unicode__())
        self.assertEquals('test2@invitation.com has key %s' % invite2.invitation_key, invite2.__unicode__())

