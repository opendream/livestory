from account.models import Account
from django.test import TestCase
from tests import factory

import settings

class TestAccount(TestCase):
    def setUp(self):
        self.users = [
            factory.create_user('testlove1', 'tester1@example.com', 'testuser1', 'Nirut', 'Khemasakchai', True),
            factory.create_user('testlove2', 'tester2@example.com', 'testuser2', 'Panudate', 'Vasinwattana')
        ]
        
    def tearDown(self):
         self.users[0].get_profile().image.delete()
        
    def test_get_fullname(self):
        self.assertEquals('Nirut Khemasakchai', self.users[0].get_profile().get_fullname())
        self.assertEquals('Panudate Vasinwattana', self.users[1].get_profile().get_fullname())
        
    def test_get_image(self):

        account_has_image = self.users[0].get_profile()
        account_no_image = self.users[1].get_profile()
        
        self.assertEquals('static/img/default_user.png', account_no_image.get_image().path)
        self.assertEquals('%simages/account/%s/avatar.png' % (settings.MEDIA_ROOT, account_has_image.user.id), account_has_image.get_image().path)