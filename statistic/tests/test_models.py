from django.test import TestCase

from blog.models import Blog
from common import rm_user
from statistic.models import History, ViewCount
from tests import factory

class TestBaseData(TestCase):
	def setUp(self):
		self.user = factory.create_user('john.doe@example.com', 'john.doe@example.com', '1234', 'John', 'Doe')
		self.category = factory.create_category('Travel', 'travel')
		self.location = factory.create_location('Czech', 'Praque', 0, 0)
		self.blog = factory.create_blog('Visit Praque', self.user, self.category, self.location)

	def tearDown(self):
		rm_user(self.user.id)

class TestHistory(TestBaseData):
	def test_create(self):
		history = History.objects.create(user=self.user, blog=self.blog)
		self.assertEqual(history.user.id, self.user.id)
		self.assertEqual(history.blog.id, self.blog.id)

	def test_unicode(self):
		history = History.objects.create(user=self.user, blog=self.blog)
		self.assertEqual(history.__unicode__(), 'John Doe(%s) viewed Visit Praque(%s) on %s' % (self.user.id, self.blog.id, history.datetime.strftime('%Y/%m/%d')))


class TestViewCount(TestBaseData):
	def test_create(self):
		blog = Blog.objects.create(title='Visit Pattaya', user=self.user, category=self.category, location=self.location)
		view = ViewCount.objects.create(blog=blog, totalcount=3, weekcount=2, daycount=1)
		self.assertEqual(view.blog.id, blog.id)
		self.assertEqual(view.totalcount, 3)
		self.assertEqual(view.weekcount, 2)
		self.assertEqual(view.daycount, 1)

	def test_get_from_blog(self):
		self.assertEqual(self.blog.viewcount.totalcount, 0)
		self.assertEqual(self.blog.viewcount.weekcount, 0)
		self.assertEqual(self.blog.viewcount.daycount, 0)

	def test_unicode(self):
		self.assertEqual(self.blog.viewcount.__unicode__(), 'Visit Praque has 0 view(s), 0 view(s) in week, 0 view(s) in day')

	def test_update(self):
		self.blog.viewcount.update()
		self.assertEqual(self.blog.viewcount.totalcount, 1)
		self.assertEqual(self.blog.viewcount.weekcount, 1)
		self.assertEqual(self.blog.viewcount.daycount, 1)
