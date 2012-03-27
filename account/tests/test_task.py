from django.test import TestCase
from django.conf import settings

from django.conf import settings as project_settings

from account.tasks import send_invite
from tests import factory
from account.models import AccountKey
from override_settings import override_settings


@override_settings(PRIVATE=False)
class TestSendInvite(TestCase):
        
    def test_send_invite(self):

        self.settings = project_settings
        
        can_send_email_user = factory.create_user('test@example.com', 'test@example.com', 'test')
        invite_list = [
            {'email': 'test@example.com', 'activate_link': 'moc_activate_link'}
        ]
        send_invite(invite_list, 'livestory.com')
        account_key = AccountKey.objects.get(user__email='test@example.com')
        self.assertEquals(True, account_key.can_send_mail)
        
        #fail_send_email_user = factory.create_user('test@qpamkfjgh.com', 'test@qpamkfjgh.com', 'test')
        #invite_list = [
        #    {'email': 'test@qpamkfjgh.com', 'activate_link': 'moc_activate_link'}
        #]
        #send_invite(invite_list, 'livestory.com')
        ## TODO: make to False but now can not detect wrong email
        #self.assertEquals(False, AccountKey.objects.get(user__email='test@qpamkfjgh.com').can_send_mail)