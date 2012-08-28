import os
import shutil

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
#from statistic.models import ViewCount
from override_settings import override_settings

from tests import factory, rm_user

from blog.models import Blog, Love


@override_settings(PRIVATE=False)        
class TestBlog(TestCase):
    def setUp(self):
        self.category = factory.create_category()
        self.user = factory.create_user()
        self.location = factory.create_location() 

        self.blogs = [
            factory.create_blog('Hello world', self.user, self.category, self.location, 1),
            factory.create_blog('Hello world', self.user, self.category, self.location, 2),
            factory.create_blog('Hello world', self.user, self.category, self.location, 3),
            factory.create_blog('Hello world', self.user, self.category, self.location, 4),
            factory.create_blog('Hello world', self.user, self.category, self.location, 5),
            factory.create_blog('Hello world', self.user, self.category, self.location, 6),
            factory.create_blog('Hello world', self.user, self.category, self.location, 7),
            factory.create_blog('Hello world', self.user, self.category, self.location, 8),
            factory.create_blog('Hello world', self.user, self.category, self.location, 9),
            factory.create_blog('Hello world', self.user, self.category, self.location, 10),
            factory.create_blog('Hello world', self.user, self.category, self.location, 99)
        ]
        
    def tearDown(self):
        rm_user(self.user.id)
    
    def test_unicode(self):
        """
        Scenario: Given a blog named Icecream
        Expected:
        - its unicode should be (<id>) Icecream
        """
        # Arrage
        blog = Blog(title='Icecream') 
        blog.user = self.user
        blog.category = self.category
        blog.location = self.location
        blog.save()
        printed_unicode = '(%s) Icecream' % blog.id
        # Act
        result = blog.__unicode__()
        # Assert
        self.assertEquals(printed_unicode, result)
        
    def test_get_mood_text(self):
        self.assertEquals('Fun'         , self.blogs[0].get_mood_text())
        self.assertEquals('Amazed'      , self.blogs[1].get_mood_text())
        self.assertEquals('Happy'       , self.blogs[2].get_mood_text())
        self.assertEquals('Motivated'   , self.blogs[3].get_mood_text())
        self.assertEquals('Proud'       , self.blogs[4].get_mood_text())
        self.assertEquals('Excited'     , self.blogs[5].get_mood_text())
        self.assertEquals('Inspired'    , self.blogs[6].get_mood_text())
        self.assertEquals('Frustrated'  , self.blogs[7].get_mood_text())
        self.assertEquals('Angry'       , self.blogs[8].get_mood_text())
        self.assertEquals('Sad'         , self.blogs[9].get_mood_text())
        self.assertEquals('Moodless'    , self.blogs[10].get_mood_text())

    def test_blog_default_private_is_private(self):
        self.assertEqual(True, self.blogs[0].private)

    def test_blog_save_tags(self):
        self.blogs[0].save_tags(u'Red, Green, Blue')
        self.assertEqual(3, self.blogs[0].tags.all().count())

        self.blogs[0].save_tags(u'Red, Green, Blue, Alpha')
        self.assertEqual(4, self.blogs[0].tags.all().count())

    def test_blog_get_tags(self):
        self.blogs[0].save_tags(u'Red, Green, Blue')
        self.blogs[0].save()
        self.assertEqual('Red, Green, Blue', self.blogs[0].get_tags())

    def test_blog_delete(self):
        # to generate image cache
        self.client.login(username=self.user.username, password='testuser')
        self.client.get(reverse('blog_view', args=[self.blogs[0].id]))
        self.client.logout()

        blog_id = self.blogs[0].id
        self.blogs[0].delete()
        expected = os.path.exists('%sblog/%s/%s' % (settings.IMAGE_ROOT, self.user.id, blog_id))
        self.assertFalse(expected)
        expected = os.path.exists('%scache/images/blog/%s/%s' % (settings.MEDIA_ROOT, self.user.id, blog_id))
        self.assertFalse(expected)
        #with self.assertRaises(ViewCount.DoesNotExist):
        #    ViewCount.objects.get(blog__id=blog_id)
        
@override_settings(PRIVATE=False)
class TestLove(TestCase):
    
    def test_unicode(self):
        user = factory.create_user('loveuser@example.com', 'loveuser@example.com', 'loveuser')
        blog = factory.create_blog('Hello world', user) 
        love = Love(blog=blog, user=user)
        self.assertEquals('loveuser@example.com love Hello world', love.__unicode__())
        
        rm_user(user.id)

@override_settings(PRIVATE=False)
class TestCategory(TestCase):
    def test_unicode(self):
        category = factory.create_category('Animals', 'animals')
        self.assertEquals('Animals', category.__unicode__())