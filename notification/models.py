from blog.models import Blog
from django.contrib.auth.models import User
from django.db import models

ACTION_CHOICES = (
    (1, 'loved'),
    (2, 'downloaded'),
)

class Notification(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    action = models.IntegerField()

    subject = models.ForeignKey(User)
    blog = models.ForeignKey(Blog)

    def __unicode__(self):
        return '%s %s %s' % (self.subject.get_profile().get_fullname(), self.get_action_text(), self.blog.title)

    def get_action_text(self):
        actions = dict(ACTION_CHOICES)
        return actions[self.action]
