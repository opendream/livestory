from account.models import Account
from django.test import TestCase
from tests import factory

class TestAccount(TestCase):
    def test_get_fullname(self):
        user = factory.create_user('rutcreate1@gmail.com', 'rutcreate1@gmail.com', 'rutcreate', 'Nirut', 'Khemasakchai')
        self.assertEquals('Nirut Khemasakchai', user.get_profile().get_fullname())
        
    def test_get_image(self):
        self.assertEquals('', '')