from blog.models import Blog
from django.test import TestCase
from tests import factory

class TestBlog(TestCase):
    def setUp(self):
        self.category = factory.create_category()
        self.user = factory.create_user()
        self.location = factory.create_location() 

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
        self.assertEqual(printed_unicode, result)

