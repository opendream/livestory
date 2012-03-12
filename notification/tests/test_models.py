from notification.models import Notification
from django.test import TestCase

from tests import factory

class TestNotification(TestCase):
	def setUp(self):
		self.user = factory.create_user('john.doe@example.com', 'john.doe@example.com', 'john123', 'John', 'Doe')
		self.location = factory.create_location('Thailand', 'Nakhonsawan')
		self.category = factory.create_category('Travel', 'travel')
		self.blog = factory.create_blog('Travel in Nakhonsawan', self.user, self.category, self.location)

		self.love_user = factory.create_user('adam.johnson@example.com', 'adam.johnson@example.com', 'adam123', 'Adam', 'Johnson')
		self.notification = Notification(subject=self.love_user, action='loves', blog=self.blog)
		self.notification.save()

	def tearDown(self):
		pass

	def test_unicode(self):
		self.assertEqual('Adam Johnson loves Travel in Nakhonsawan', self.notification.__unicode__())