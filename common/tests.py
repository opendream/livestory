"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTestCase(TestCase):

    def test_simple(self):
        self.assertEqual(1+1, 2)
