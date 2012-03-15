from account.models import Account, AccountKey
from django.test import TestCase
from tests import factory

from common import rm_user

import settings

class TestAccount(TestCase):
    def setUp(self):
        self.users = [
            factory.create_user('tester1@example.com', 'tester1@example.com', 'testuser1', 'Nirut', 'Khemasakchai', True),
            factory.create_user('tester2@example.com', 'tester2@example.com', 'testuser2', 'Panudate', 'Vasinwattana')
        ]
        
    def tearDown(self):
         self.users[0].get_profile().image.delete()
         rm_user(self.users[0].id)
         rm_user(self.users[1].id)
        
    def test_get_fullname(self):
        self.assertEquals('Nirut Khemasakchai', self.users[0].get_profile().get_fullname())
        self.assertEquals('Panudate Vasinwattana', self.users[1].get_profile().get_fullname())
        
    def test_get_image(self):

        account_has_image = self.users[0].get_profile()
        account_no_image = self.users[1].get_profile()
        
        self.assertEquals('static/img/default_user.png', account_no_image.get_image().path)
        self.assertEquals('%simages/account/%s/avatar.png' % (settings.MEDIA_ROOT, account_has_image.user.id), account_has_image.get_image().path)
    
    def test_get_image_url(self):
        account_has_image = self.users[0].get_profile()
        account_no_image = self.users[1].get_profile()
        self.assertEquals('/media/images/account/%s/avatar.png' % account_has_image.user.id, account_has_image.get_image_url())
        self.assertEquals(None, account_no_image.get_image_url())
        
    def test_unicode(self):
        self.assertEquals('Nirut Khemasakchai', self.users[0].get_profile().__unicode__())
        self.assertEquals('Panudate Vasinwattana', self.users[1].get_profile().__unicode__())

class TestAccountKey(TestCase):
    def setUp(self):
        self.users = [
            factory.create_user('tester1@example.com', 'tester1@example.com', 'testuser1', 'Nirut', 'Khemasakchai'),
            factory.create_user('tester2@example.com', 'tester2@example.com', 'testuser2', 'Panudate', 'Vasinwattana')
        ]

    def tearDown(self):
        for user in self.users:
            rm_user(user.id)
            AccountKey.objects.get(user=user).delete()
            Account.objects.get(user=user).delete()
            user.delete()
        
    def test_unicode(self):
        account_key1 = AccountKey.objects.get(user=self.users[0])
        account_key2 = AccountKey.objects.get(user=self.users[1])
        self.assertEquals('tester1@example.com has key %s' % account_key1.key, account_key1.__unicode__())
        self.assertEquals('tester2@example.com has key %s' % account_key2.key, account_key2.__unicode__())

    def test_update_view_notification(self):
        account_key = AccountKey.objects.get(user=self.users[0])
        before = account_key.view_notification
        account_key.update_view_notification()
        after = account_key.view_notification
        self.assertGreater(after, before)
