from account.models import Account, AccountKey
from django.test import TestCase
from notification.views import get_notifications
from tests import factory

class TestHelperFunction(TestCase):
	def setUp(self):
		self.user = factory.create_user('john@example.com', 'john@example.com', 'john123', 'John', 'Doe', True)

	def tearDown(self):
		AccountKey.objects.get(user=self.user).delete()
		Account.objects.get(user=self.user).delete()
		self.user.delete()

	def test_get_notifications_by_anonymous_user(self):
		self.assertEqual([], get_notifications(self.user))