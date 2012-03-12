from blog.models import Blog
from django.contrib.auth.models import User
from django.db import models

class Notification(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	action = models.CharField(max_length=100)

	subject = models.ForeignKey(User)
	blog = models.ForeignKey(Blog)

	def __unicode__(self):
		return '%s %s %s' % (self.subject.get_profile().get_fullname(), self.action, self.blog.title)