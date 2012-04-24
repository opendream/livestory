from account.models import UserProfile, UserInvitation
from django.test import TestCase
from notification.models import Notification
from override_settings import override_settings


from tests import factory

@override_settings(PRIVATE=False)
class TestNotification(TestCase):
	def setUp(self):
		self.user = factory.create_user('john.doe@example.com', 'john.doe@example.com', 'john123', 'John', 'Doe')
		self.location = factory.create_location('Thailand', 'Nakhonsawan')
		self.category = factory.create_category('Travel', 'travel')
		self.blog = factory.create_blog('Travel in Nakhonsawan', self.user, self.category, self.location)

		self.love_user = factory.create_user('adam.johnson@example.com', 'adam.johnson@example.com', 'adam123', 'Adam', 'Johnson')
		self.love_notification = Notification(subject=self.love_user, action=1, blog=self.blog)
		self.love_notification.save()

		self.download_notification = Notification(subject=self.user, action=2, blog=self.blog)
		self.download_notification.save()

	def tearDown(self):
		self.location.delete()
		self.category.delete()
		self.blog.delete()
		self.love_notification.delete()
		self.download_notification.delete()

		UserInvitation.objects.get(email=self.love_user.email).delete()
		UserProfile.objects.get(user=self.love_user).delete()
		self.love_user.delete()

		UserInvitation.objects.get(email=self.user.email).delete()
		UserProfile.objects.get(user=self.user).delete()
		self.user.delete()

	def test_unicode(self):
		self.assertEqual('Adam Johnson loved Travel in Nakhonsawan', self.love_notification.__unicode__())
		self.assertEqual('John Doe downloaded Travel in Nakhonsawan', self.download_notification.__unicode__())

	def test_get_action_text(self):
		self.assertEqual('loved', self.love_notification.get_action_text())
		self.assertEqual('downloaded', self.download_notification.get_action_text())