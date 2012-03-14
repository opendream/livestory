from account.models import Account, AccountKey
from django.test import TestCase
from notification.models import Notification
from notification.views import get_notifications
from tests import factory

class TestHelperFunction(TestCase):
	def setUp(self):
		self.user = factory.create_user('john.doe@example.com', 'john.doe@example.com', 'john123', 'John', 'Doe')
		self.location = factory.create_location('Thailand', 'Nakhonsawan')
		self.category = factory.create_category('Travel', 'travel')
		self.blog = factory.create_blog('Travel in Nakhonsawan', self.user, self.category, self.location)

		self.user_with_notification = factory.create_user('adam.johnson@example.com', 'adam.johnson@example.com', 'adam123', 'Adam', 'Johnson')
		self.notification = Notification(subject=self.user_with_notification, action='loves', blog=self.blog)
		self.notification.save()

	def tearDown(self):
		AccountKey.objects.get(user=self.user).delete()
		Account.objects.get(user=self.user).delete()
		self.user.delete()

		AccountKey.objects.get(user=self.user_with_notification).delete()
		Account.objects.get(user=self.user_with_notification).delete()
		self.user_with_notification.delete()

	def test_get_notifications(self):
		self.assertEqual(0, len(get_notifications(self.user)))
		self.assertEqual(1, len(get_notifications(self.user_with_notification)))

	def test_get_notifications_after_viewed(self):
		self.assertEqual(1, len(get_notifications(self.user_with_notification)))
		AccountKey.objects.get(user=self.user_with_notification).update_view_notification()
		self.assertEqual(0, len(get_notifications(self.user_with_notification)))