from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from unittest.mock import patch


User = get_user_model()


class InitialAdminSetupTests(TestCase):
	setup_key = 'temporary-test-key'
	url = '/create-initial-admin/'

	def setUp(self):
		self.client = Client()
		self.environment = patch.dict('os.environ', {'ADMIN_SETUP_KEY': self.setup_key})
		self.environment.start()
		self.addCleanup(self.environment.stop)

	def test_invalid_key_is_rejected(self):
		response = self.client.get(self.url, {'key': 'wrong-key'})
		self.assertEqual(response.status_code, 403)

	def test_valid_key_opens_form_without_rendering_key(self):
		response = self.client.get(self.url, {'key': self.setup_key})
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, self.setup_key)

	def test_password_mismatch_is_rejected(self):
		self.client.get(self.url, {'key': self.setup_key})
		response = self.client.post(self.url, {
			'username': 'initial-admin',
			'email': 'admin@example.com',
			'password': 'StrongPassword123!',
			'password_confirm': 'DifferentPassword123!',
		})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Passwords do not match.')
		self.assertFalse(User.objects.filter(username='initial-admin').exists())

	def test_admin_is_created_and_existing_user_is_updated(self):
		self.client.get(self.url, {'key': self.setup_key})
		payload = {
			'username': 'initial-admin',
			'email': 'admin@example.com',
			'password': 'StrongPassword123!',
			'password_confirm': 'StrongPassword123!',
		}
		response = self.client.post(self.url, payload)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Admin account is ready')

		user = User.objects.get(username='initial-admin')
		self.assertTrue(user.is_staff)
		self.assertTrue(user.is_superuser)
		self.assertTrue(user.is_active)
		self.assertTrue(user.check_password(payload['password']))

		self.client.get(self.url, {'key': self.setup_key})
		payload['email'] = 'updated-admin@example.com'
		self.client.post(self.url, payload)
		self.assertEqual(User.objects.filter(username='initial-admin').count(), 1)
		user.refresh_from_db()
		self.assertEqual(user.email, payload['email'])

# Create your tests here.
