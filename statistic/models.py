from django.db import models

from blog.models import Blog

class BlogViewHit(models.Model):
    blog = models.ForeignKey(Blog)
    sessionkey = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        #blog_stat_summary = BlogViewSummary.objects.select_for_update().get(blog=blog) ### Use this statement instead when migrate to Django 1.4
        blog_stat_summary, created = BlogViewSummary.objects.get_or_create(blog=self.blog)
        blog_stat_summary.totalcount = blog_stat_summary.totalcount + 1
        blog_stat_summary.save()
        super(BlogViewHit, self).save(*args, **kwargs)

class BlogViewSummary(models.Model):
    blog = models.OneToOneField(Blog)
    totalcount = models.IntegerField(default=0)

    def __unicode__(self):
        return '%s has %d hits' % (self.blog.title, self.totalcount)