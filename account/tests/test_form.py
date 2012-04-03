from django.test import TestCase

from account.forms import AccountCreationForm

class TestAccountCreationForm(TestCase):

	def test_render_empty_form(self):
		form = AccountCreationForm()
		html_out = form.as_table()
		assert '<input id="id_username" type="text" name="username" maxlength="30" />' in html_out
		assert '<input type="password" name="password1" id="id_password1" />' in html_out
		assert '<input type="password" name="password2" id="id_password2" />' in html_out
		assert '<input type="text" name="email" id="id_email" />' in html_out
		assert '<input id="id_firstname" type="text" class="span3" name="firstname" maxlength="200" />' in html_out
		assert '<input id="id_lastname" type="text" class="span3" name="lastname" maxlength="200" />' in html_out

	def test_invalid_data_form(self):
		form = AccountCreationForm({})
		form.is_valid()
		self.assertTrue(form.errors)

	def test_valid_data_form(self):
		form = AccountCreationForm(dict(email='test@example.com', username='test', password1='testpassword', password2='testpassword'))
		self.assertTrue(form.is_valid())

	def test_save_form_email(self):
		form = AccountCreationForm(dict(email='test@example.com', username='test', password1='testpassword', password2='testpassword'))
		self.assertTrue(form.is_valid())
		account = form.save()
		user = account.user
		self.assertEquals(user.email, 'test@example.com')
		self.assertEquals(user.username, 'test')

