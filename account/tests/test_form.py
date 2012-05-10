from django.test import TestCase

from account.forms import UserProfileCreationForm

class TestAccountCreationForm(TestCase):

	def test_render_empty_form(self):
		form = UserProfileCreationForm()
		html_out = form.as_table()
		print html_out
		assert 'input id="id_email" type="text" class="span3" name="email" maxlength="254" />' in html_out
		assert '<input id="id_password1" type="password" class="span3" name="password1" />' in html_out
		assert '<input id="id_password2" type="password" class="span3" name="password2" />' in html_out
		assert '<input id="id_first_name" type="text" class="span3" name="first_name" maxlength="200" />' in html_out
		assert '<input id="id_last_name" type="text" class="span3" name="last_name" maxlength="200" />' in html_out
		assert '<select name="timezone" id="id_timezone">' in html_out

	def test_invalid_data_form(self):
		form = UserProfileCreationForm({})
		form.is_valid()
		self.assertTrue(form.errors)

	def test_valid_data_form(self):
		form = UserProfileCreationForm(dict(email='test@example.com', 
											first_name='test_firstname', 
											last_name='test_lastname', 
											password1='testpassword', 
											password2='testpassword'))
		self.assertTrue(form.is_valid())

	# def test_save_form_email(self):
	# 	form = UserProfileCreationForm(dict(email='test@example.com',
	# 										password1='testpassword', 
	# 										password2='testpassword', 
	# 										first_name='test_firstname',
	# 										last_name='test_lastname'))
	# 	self.assertTrue(form.is_valid())
	# 	account = form.save()
	# 	user = account.user
	# 	self.assertEquals(user.email, 'test@example.com')
	# 	self.assertEquals(user.username, 'test@example.com')
	# 	self.assertEquals(account.first_name, 'test_firstname')
	# 	self.assertEquals(account.last_name, 'test_lastname')
	# 	self.assertTrue(user.is_active)

	def test_save_form_invalid_email(self):
		form = UserProfileCreationForm(dict(email='test'))
		form.is_valid()
		assert '<li>Enter a valid e-mail address.</li>' in form.as_ul()

