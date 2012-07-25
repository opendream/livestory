from django.test import TestCase
from django.core.files import File
from django.core.urlresolvers import reverse
from django.conf import settings

from tests import factory
from datetime import datetime
from blog.functions import save_temporary_blog_image

class TestBlogImageData(TestCase):

    def setUp(self):
        self.user = factory.create_user(
            'test@example.com', 
            'test@example.com', 
            'test'
        )
        self.category = factory.create_category('Animal', 'animal')

    def test_blog_create_post(self):
        image = File(open(settings.BASE_PATH + '/static/tests/IMG_1405.jpg'))
        file_name, thumbnail_url = save_temporary_blog_image(image)

        params = {
            'title'           : 'Hello world',
            'image_file_name' : file_name,
            'description'     : 'lorem ipsum',
            'mood'            : '4',
            'country'         : 'Thailand',
            'city'            : 'Hat Yai',
            'private'         : '1',
            'draft'           : '0',
            'category'        : str(self.category.id),
            'allow_download'  : '0',
            'trash'           : '0',
            'publish'         : '1',
        }

        self.client.login(
            username='test@example.com', 
            password='test'
        )

        resp = self.client.post(reverse('blog_create'), params, follow=True)
        self.assertEquals(200, resp.status_code)
        blog = resp.context['blog']
        self.assertFalse(blog is None)
        self.assertEquals('Canon/Canon EOS 7D', blog.image_captured_device)
        self.assertEquals(datetime(2012, 01, 28, 18, 45, 21), blog.image_captured_date)        

        self.client.logout()