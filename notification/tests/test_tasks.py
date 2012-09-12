from django.test import TestCase
from django.contrib.auth.models import User

from notification.tasks import comment_notify_blog_owner as notify_task
from notification.tasks import get_periodic_notify_users, notify_blog_owner 
from notification.tasks import get_blog_love_events, get_blog_comment_events
from account.models import UserProfile
from blog.models import Blog, Comment, Love
from datetime import date, datetime, timedelta
from tests import factory

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
        # set notification type to be immediately (-1), email sent
        last_notify_datetime = datetime.now() - timedelta(minutes=10)
        user_profile = self.comment.blog.user.get_profile()
        user_profile.notification_type = -1
        user_profile.next_notified = last_notify_datetime
        user_profile.save()

        response = notify_task(self.comment)
        self.assertNotEquals(response, None)

    def test_immediate_notification_task_email_not_sent(self):
        # people comment on their own blog, email not sent
        comment2 = Comment.objects.create(
            comment = 'test comment 2',
            user = self.comment.blog.user,
            blog = self.comment.blog
        )
        response = notify_task(self.comment)
        self.assertEquals(response, None)

        # set notification type to be weekly (7), email not sent
        user_profile = self.comment.blog.user.get_profile()
        user_profile.notification_type = 7
        user_profile.save()

        response = notify_task(self.comment)
        self.assertEquals(response, None)

class TestPeriodicNotificationTask(TestCase):

    def setUp(self):
        self.category = factory.create_category()
        self.user1 = UserProfile.objects.create_profile('tavee@opendream.co.th', '', '', '')
        self.user2 = UserProfile.objects.create_profile('taveek@gmail.com', '', '', '')
        self.user3 = UserProfile.objects.create_profile('jimmy@opendream.co.th', '', '', '')
        self.location = factory.create_location() 
        self.blog1 = factory.create_blog('Hello world 1', self.user1, self.category, self.location, 1)
        self.blog2 = factory.create_blog('Hello world 2', self.user2, self.category, self.location, 1)

    def test_get_blog_events(self):
        expected_day = date(2011, 1, 12)
        user = self.user1
        str_date = expected_day - timedelta(user.get_profile().notification_type)
        end_date = datetime(expected_day.year, expected_day.month, expected_day.day, 23, 59, 59)

        l = Love.objects.create(user=self.user2, blog=self.blog1)
        l.datetime=datetime(2011, 1, 11, 0, 0, 0)
        l.save()

        love_list = get_blog_love_events(user, str_date, end_date)
        self.assertEquals(1, len(love_list))
        
        l = Love.objects.create(user=self.user3, blog=self.blog1)
        l.datetime=datetime(2011, 1, 12, 23, 59, 59)
        l.save()

        love_list = get_blog_love_events(user, str_date, end_date)
        self.assertEquals(2, len(love_list))
        
        c = Comment.objects.create(comment='test comment', user=self.user2, blog=self.blog1)
        c.post_date=datetime(2011, 1, 11, 0, 0, 0)
        c.save()

        comment_list = get_blog_comment_events(user, str_date, end_date)
        self.assertEquals(1, len(comment_list))

        c = Comment.objects.create(comment='test comment', user=self.user3, blog=self.blog1)
        c.post_date=datetime(2011, 1, 12, 23, 59, 59)
        c.save()

        comment_list = get_blog_comment_events(user, str_date, end_date)
        self.assertEquals(2, len(comment_list))

    def test_daily_notify_blog_owner_one_user_event(self):
        period = 1
        execute_date = date(2000, 1, 1)

        p = self.user1.get_profile()
        p.notification_type = period
        p.next_notified = execute_date
        p.save()

        l = Love.objects.create(user=self.user2, blog=self.blog1)
        l.datetime=datetime(1999, 12, 31, 0, 0, 0)
        l.save()

        response = notify_blog_owner(execute_date)
        self.assertEquals(1, len(response))

        pf = User.objects.get(id=self.user1.id).get_profile()
        self.assertEquals(pf.next_notified, execute_date + timedelta(period))

    def test_weekly_notify_blog_owner_one_user_event(self):
        period = 7
        execute_date = date(2000, 1, 1)

        p = self.user1.get_profile()
        p.notification_type = period
        p.next_notified = execute_date
        p.save()

        l = Love.objects.create(user=self.user2, blog=self.blog1)
        l.datetime=datetime(1999, 12, 31, 0, 0, 0)
        l.save()

        response = notify_blog_owner(execute_date)
        self.assertEquals(1, len(response))

        pf = User.objects.get(id=self.user1.id).get_profile()
        self.assertEquals(pf.next_notified, execute_date + timedelta(period))

    def test_daily_notify_blog_owner_one_blog_three_user_events(self):
        period = 1
        execute_date = date(2000, 1, 2)

        p = self.user1.get_profile()
        p.notification_type = period
        p.next_notified = execute_date
        p.save()

        l = Love.objects.create(user=self.user1, blog=self.blog1)
        l.datetime=datetime(2000, 1, 1, 0, 0, 0)
        l.save()

        l = Love.objects.create(user=self.user2, blog=self.blog1)
        l.datetime=datetime(2000, 1, 1, 12, 30, 30)
        l.save()

        l = Love.objects.create(user=self.user3, blog=self.blog1)
        l.datetime=datetime(2000, 1, 1, 23, 59, 59)
        l.save()

        response = notify_blog_owner(execute_date)
        self.assertEquals(1, len(response))

        pf = User.objects.get(id=self.user1.id).get_profile()
        self.assertEquals(pf.next_notified, execute_date + timedelta(period))

    def test_weekly_notify_blog_owner_one_blog_three_user_events(self):
        period = 7
        execute_date = date(2000, 1, 2)

        p = self.user1.get_profile()
        p.notification_type = period
        p.next_notified = execute_date
        p.save()

        l = Love.objects.create(user=self.user1, blog=self.blog1)
        l.datetime=datetime(1999, 12, 25, 0, 0, 0)
        l.save()

        l = Love.objects.create(user=self.user2, blog=self.blog1)
        l.datetime=datetime(2000, 1, 1, 12, 30, 30)
        l.save()

        l = Love.objects.create(user=self.user3, blog=self.blog1)
        l.datetime=datetime(2000, 1, 1, 23, 59, 59)
        l.save()

        response = notify_blog_owner(execute_date)
        self.assertEquals(1, len(response))

        pf = User.objects.get(id=self.user1.id).get_profile()
        self.assertEquals(pf.next_notified, execute_date + timedelta(period))

    def test_daily_notify_blog_owner_two_blogs_two_events(self):
        period = 1
        execute_date = date(2000, 1, 2)

        p = self.user1.get_profile()
        p.notification_type = period
        p.next_notified = execute_date
        p.save()

        p = self.user2.get_profile()
        p.notification_type = period
        p.next_notified = execute_date
        p.save()

        l = Love.objects.create(user=self.user2, blog=self.blog1)
        l.datetime=datetime(2000, 1, 1, 10, 10, 10)
        l.save()

        l = Love.objects.create(user=self.user3, blog=self.blog2)
        l.datetime=datetime(2000, 1, 1, 10, 10, 10)
        l.save()

        response = notify_blog_owner(execute_date)
        self.assertEquals(2, len(response))

        pf1 = User.objects.get(id=self.user1.id).get_profile()
        self.assertEquals(pf1.next_notified, execute_date + timedelta(period))

        pf2 = User.objects.get(id=self.user2.id).get_profile()
        self.assertEquals(pf2.next_notified, execute_date + timedelta(period))

    def test_weekly_notify_blog_owner_two_blogs_two_events(self):
        period = 7
        execute_date = date(2000, 1, 2)

        p = self.user1.get_profile()
        p.notification_type = period
        p.next_notified = execute_date
        p.save()

        p = self.user2.get_profile()
        p.notification_type = period
        p.next_notified = execute_date
        p.save()

        l = Love.objects.create(user=self.user2, blog=self.blog1)
        l.datetime=datetime(1999, 12, 30, 10, 10, 10)
        l.save()

        l = Love.objects.create(user=self.user3, blog=self.blog2)
        l.datetime=datetime(2000, 1, 1, 10, 10, 10)
        l.save()

        response = notify_blog_owner(execute_date)
        self.assertEquals(2, len(response))

        pf1 = User.objects.get(id=self.user1.id).get_profile()
        self.assertEquals(pf1.next_notified, execute_date + timedelta(period))

        pf2 = User.objects.get(id=self.user2.id).get_profile()
        self.assertEquals(pf2.next_notified, execute_date + timedelta(period))
