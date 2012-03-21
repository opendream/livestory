from django.contrib.auth.models import User
from django.db import models

from blog.models import Blog

class History(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User)
	blog = models.ForeignKey(Blog)