from django.test import TestCase

class TestBlogAdmin(TestCase):
    def test_list_page(self):
        response = self.client.get('/admin/blog/blog/')  
        msg = "Blog Admin is missing!!"
        self.assertEqual(200, response.status_code, msg)
        
