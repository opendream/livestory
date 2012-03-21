from django.test import TestCase

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
		self.category.delete()
		self.location.delete()
		self.blog.delete()

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
		view = ViewCount.objects.create(blog=self.blog, totalcount=3, weekcount=2, daycount=1)
		self.assertEqual(view.blog.id, self.blog.id)
		self.assertEqual(view.totalcount, 3)
		self.assertEqual(view.weekcount, 2)
		self.assertEqual(view.daycount, 1)
