from blog.models import Blog, Love, blog_image_path
from django.test import TestCase
from tests import factory
from common import rm_user

import os
import settings
import shutil
        
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
            factory.create_blog('Hello world', self.user, self.category, self.location, 10)
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
        self.assertEquals('Happy'     , self.blogs[0].get_mood_text())
        self.assertEquals('Sad'       , self.blogs[1].get_mood_text())
        self.assertEquals('Excited'   , self.blogs[2].get_mood_text())
        self.assertEquals('Inspired'  , self.blogs[3].get_mood_text())
        self.assertEquals('Frustrated', self.blogs[4].get_mood_text())
        self.assertEquals('Angry'     , self.blogs[5].get_mood_text())
        self.assertEquals('Fun'       , self.blogs[6].get_mood_text())
        self.assertEquals('Proud'     , self.blogs[7].get_mood_text())
        self.assertEquals('Amazed'    , self.blogs[8].get_mood_text())
        self.assertEquals('Motivated' , self.blogs[9].get_mood_text())
        
        
    def test_blog_image_path(self):
        image_path = blog_image_path(self.blogs[0], self.blogs[0].image.file.name)
        
        self.assertEquals(True, os.path.exists('%s/media/images/blog/%d' % (settings.base_path, self.blogs[0].user.id)))
        self.assertEquals('%s/media/images/blog/%d/%d/blog_%d.jpg' % (settings.base_path, self.blogs[0].user.id, self.blogs[0].id, self.blogs[0].id), image_path)
        
        

class TestLove(TestCase):
    
    def test_unicode(self):
        user = factory.create_user('loveuser@example.com', 'loveuser@example.com', 'loveuser')
        blog = factory.create_blog('Hello world', user) 
        love = Love(blog=blog, user=user)
        self.assertEquals('loveuser@example.com love Hello world', love.__unicode__())
        
        rm_user(user.id)


class TestCategory(TestCase):
    def test_unicode(self):
        category = factory.create_category('Animals', 'animals')
        self.assertEquals('Animals', category.__unicode__())