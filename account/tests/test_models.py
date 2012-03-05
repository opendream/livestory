from account.models import Account
from django.test import TestCase
from tests import factory

class TestAccount(TestCase):
    def test_get_fullname(self):
        user = factory.create_user('rutcreate1@gmail.com', 'rutcreate1@gmail.com', 'rutcreate')
        account = Account(firstname='Nirut', lastname='Khemasakchai', user=user)
        account.save()
        self.assertEquals('Nirut Khemasakchai', user.get_profile().get_fullname())