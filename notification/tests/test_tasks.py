from django.test import TestCase

from notification.tasks import BlogCommentNotifyOwnerTask 
from account.models import UserProfile
from blog.models import Blog, Comment

class TestNotificationTask(TestCase):
	fixtures = ['demo_data.json']

	def setUp(self):
		james = UserProfile.objects.create_profile('james@opendream.co.th', '', '', '')
		blog = Blog.objects.get(id=1) # prepared by demo_data.json
		self.comment = Comment.objects.create(
			comment='test comment', 
			user=james, 
			blog=blog
		)

	def test_immediate_notification_task_email_sent(self):
		task = BlogCommentNotifyOwnerTask()

		# set notification type to be immediately (-1), email sent
		user_profile = self.comment.blog.user.get_profile()
		user_profile.notification_type = -1
		user_profile.save()

		response = task._notify(self.comment)
		self.assertEquals(response, self.comment.blog.user.email)

	def test_immediate_notification_task_email_not_sent(self):
		task = BlogCommentNotifyOwnerTask()

		# people comment on their own blog, email not sent
		comment2 = Comment.objects.create(
			comment = 'test comment 2',
			user = self.comment.blog.user,
			blog = self.comment.blog
		)
		response = task._notify(self.comment)
		self.assertEquals(response, None)

		# set notification type to be weekly (7), email not sent
		user_profile = self.comment.blog.user.get_profile()
		user_profile.notification_type = 7
		user_profile.save()

		response = task._notify(self.comment)
		self.assertEquals(response, None)
