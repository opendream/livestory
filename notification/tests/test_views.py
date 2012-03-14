from account.models import Account, AccountKey
from django.core.urlresolvers import reverse
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
		self.notification = Notification(subject=self.user_with_notification, action=1, blog=self.blog)
		self.notification.save()

	def tearDown(self):
		AccountKey.objects.get(user=self.user).delete()
		Account.objects.get(user=self.user).delete()
		self.user.delete()

		AccountKey.objects.get(user=self.user_with_notification).delete()
		Account.objects.get(user=self.user_with_notification).delete()
		self.user_with_notification.delete()

		self.notification.delete()

	def test_get_notifications(self):
		self.assertEqual(1, len(get_notifications(self.user)))
		self.assertEqual(0, len(get_notifications(self.user_with_notification)))

	def test_get_notifications_after_viewed(self):
		self.assertEqual(1, len(get_notifications(self.user)))
		AccountKey.objects.get(user=self.user_with_notification).update_view_notification()
		self.assertEqual(0, len(get_notifications(self.user_with_notification)))

class TestNotification(TestCase):
	def setUp(self):
		self.user = factory.create_user('john.doe@example.com', 'john.doe@example.com', 'john123', 'John', 'Doe')
		self.user_with_notification = factory.create_user('adam.johnson@example.com', 'adam.johnson@example.com', 'adam123', 'Adam', 'Johnson')
		self.user_other = factory.create_user('tony.adams@example.com', 'tony.adams@example.com', 'tony123', 'Tony', 'Adams')

		self.location = factory.create_location('Thailand', 'Nakhonsawan')
		self.category = factory.create_category('Travel', 'travel')
		self.blog = factory.create_blog('Travel in Nakhonsawan', self.user, self.category, self.location)

		self.notification = Notification(subject=self.user_with_notification, action=1, blog=self.blog)
		self.notification.save()

	def tearDown(self):
		AccountKey.objects.get(user=self.user).delete()
		Account.objects.get(user=self.user).delete()
		self.user.delete()

		AccountKey.objects.get(user=self.user_with_notification).delete()
		Account.objects.get(user=self.user_with_notification).delete()
		self.user_with_notification.delete()

	def test_notification_page_get_by_anonymous_user(self):
		response = self.client.get(reverse('notification_view'))
		self.assertEqual(403, response.status_code)
		self.assertTemplateUsed(response, '403.html')

	def test_notification_page_get_by_authenticated_user(self):
		self.client.login(username='john.doe@example.com', password='john123')
		response = self.client.get(reverse('notification_view'))
		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, 'notification/notification_view.html')
		self.client.logout()

	def test_notification_page_after_viewed(self):
		self.assertEqual(1, len(get_notifications(self.user)))
		self.client.login(username='john.doe@example.com', password='john123')
		self.client.get(reverse('notification_view'))
		self.assertEqual(0, len(get_notifications(self.user)))
		self.client.logout()

	def test_notification_ajax_get(self):
		self.client.login(username='adam.johnson@example.com', password='adam123')
		response = self.client.get(reverse('notification_view'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertContains(response, '{"status": 200}')
		self.client.logout()

	def test_notification_with_love(self):
		num_notification_before = len(get_notifications(self.user))
		self.assertEqual(1, num_notification_before)

		self.client.login(username='tony.adams@example.com', password='tony123')
		self.client.get(reverse('blog_love', args=[self.blog.id]))
		num_notification_after_love = len(get_notifications(self.user))
		self.assertEqual(2, num_notification_after_love)
		self.client.logout()
