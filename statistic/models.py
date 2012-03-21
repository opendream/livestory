from django.contrib.auth.models import User
from django.db import models

from blog.models import Blog


class History(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User)
	blog = models.ForeignKey(Blog)

	def __unicode__(self):
		return '%s(%s) viewed %s(%s) on %s' % (self.user.get_profile().get_fullname(), self.user.id, self.blog.title, self.blog.id, self.datetime.strftime('%Y/%m/%d'))


class ViewCount(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	blog = models.OneToOneField(Blog)
	totalcount = models.IntegerField(default=0)
	weekcount = models.IntegerField(default=0)
	daycount = models.IntegerField(default=0)

	def update(self):
		self.totalcount = self.totalcount + 1
		self.weekcount = self.weekcount + 1
		self.daycount = self.daycount + 1
		self.save()

	def __unicode__(self):
		return '%s has %s view(s), %s view(s) in week, %s view(s) in day' % (self.blog.title, self.totalcount, self.weekcount, self.daycount)
