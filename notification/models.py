from blog.models import Blog
from django.contrib.auth.models import User
from django.db import models

from datetime import datetime

ACTION_CHOICES = (
    (1, 'loved'),
    (2, 'downloaded'),
)

class Notification(models.Model):
    datetime = models.DateTimeField()
    action = models.IntegerField()

    subject = models.ForeignKey(User)
    blog = models.ForeignKey(Blog)

    def __unicode__(self):
        return '%s %s %s' % (self.subject.get_profile().get_fullname(), self.get_action_text(), self.blog.title)

    def get_action_text(self):
        actions = dict(ACTION_CHOICES)
        return actions[self.action]

    def save(self, *args, **kwargs):
        try:
            notification = Notification.objects.get(subject=self.subject, action=self.action, blog=self.blog)
        except Notification.DoesNotExist:
            if not self.id and not self.datetime:
                self.datetime = datetime.now()
            super(Notification, self).save(*args, **kwargs)