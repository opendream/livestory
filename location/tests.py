"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from location.models import Location

class LocationTest(TestCase):
    def setUp(self):
        Location.objects.create(country='Japan', city='Tokyo')
        Location.objects.create(country='Thailand', city='Hat Yai')
        Location.objects.create(country='Mali', city='Gao')

    def tearDown(self):
        pass

    def test_duplicate_location(self):
        loc, created = Location.objects.get_or_create(country__iexact='Thailand', city__iexact='Hat Yai')
        self.assertFalse(created)
        self.assertEqual('Thailand', loc.country)
        self.assertEqual('Hat yai', loc.city)

