"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings

from common import utilities

import datetime

class ImageUtilitiesTest(TestCase):

    def setUp(self):
        self.test_image = open(settings.STATICFILES_DIRS[0] + '/tests/IMG_1405.jpg', 'r')

    def test_get_image_info(self):
        captured_device = utilities.get_image_captured_device(self.test_image)
        self.assertEqual('Canon/Canon EOS 7D', captured_device)

    def test_get_image_captured_date(self):
        captured_date = utilities.get_image_captured_date(self.test_image)
        self.assertEqual(datetime.datetime(2012,06,04,18,45,21), captured_date)
