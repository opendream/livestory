from account.models import Account
from django.test import TestCase
from tests import factory

class TestAccount(TestCase):
    def setUp(self):
        self.users = [
            factory.create_user('testlove1', 'tester1@example.com', 'testuser1', 'Nirut', 'Khemasakchai'),
            factory.create_user('testlove2', 'tester2@example.com', 'testuser2', 'Panudate', 'Vasinwattana')
        ]
        
    def test_get_fullname(self):
        self.assertEquals('Nirut Khemasakchai', self.users[0].get_profile().get_fullname())
        self.assertEquals('Panudate Vasinwattana', self.users[1].get_profile().get_fullname())
        
    def test_get_image(self):
        self.assertEquals('', '')