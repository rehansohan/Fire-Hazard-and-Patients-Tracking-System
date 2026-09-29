from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from unittest.mock import patch
from Core.models import HazardReport, Notification, Patient


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


class HazardNotificationTests(TestCase):
	def test_active_hazard_broadcasts_fire_alert_to_all_users(self):
		reporter = User.objects.create_user(username='reporter', password='password')
		other_user = User.objects.create_user(username='other', password='password')

		HazardReport.objects.create(
			user=reporter,
			title='Factory fire',
			description='Smoke near the main entrance.',
			servity='High',
			status='active',
		)

		alerts = Notification.objects.filter(notification_type='fire_alert')
		self.assertEqual(alerts.count(), 2)
		self.assertSetEqual(
			set(alerts.values_list('user__username', flat=True)),
			{'reporter', 'other'},
		)
		self.assertTrue(alerts.filter(title='Fire Alert', is_read=False).exists())

	def test_non_active_hazard_does_not_broadcast_fire_alert(self):
		user = User.objects.create_user(username='reporter', password='password')

		HazardReport.objects.create(
			user=user,
			title='Resolved incident',
			description='Already resolved.',
			servity='Low',
			status='resolved',
		)

		self.assertFalse(Notification.objects.filter(notification_type='fire_alert').exists())


class PatientIdentifierNotificationTests(TestCase):
	def setUp(self):
		self.first_user = User.objects.create_user(username='first', password='password')
		self.second_user = User.objects.create_user(username='second', password='password')
		self.patient = Patient.objects.create(
			patient_id='PAT-001',
			status='admitted',
		)

	def test_identification_is_hidden_until_confirmed_and_shared_by_users(self):
		self.assertFalse(self.patient.is_identified)

		self.client.force_login(self.first_user)
		response = self.client.post(f'/patient/{self.patient.pk}/identify/')

		self.assertEqual(response.status_code, 302)
		self.patient.refresh_from_db()
		self.assertTrue(self.patient.is_identified)
		self.assertEqual(
			set(self.patient.identified_by_users.values_list('pk', flat=True)),
			{self.first_user.pk},
		)

		self.client.force_login(self.second_user)
		self.client.post(f'/patient/{self.patient.pk}/identify/')

		self.assertSetEqual(
			set(self.patient.identified_by_users.values_list('pk', flat=True)),
			{self.first_user.pk, self.second_user.pk},
		)
		self.assertEqual(
			Notification.objects.filter(
				patient=self.patient,
				notification_type='identification',
			).count(),
			2,
		)

	def test_patient_status_update_notifies_all_identifying_users(self):
		self.patient.is_identified = True
		self.patient.identified_by = self.first_user
		self.patient.save(update_fields=['is_identified', 'identified_by'])
		self.patient.identified_by_users.add(self.first_user, self.second_user)

		self.patient.status = 'released'
		self.patient.save()

		updates = Notification.objects.filter(
			patient=self.patient,
			title='Patient Released',
		)
		self.assertSetEqual(
			set(updates.values_list('user__username', flat=True)),
			{'first', 'second'},
		)


class ExistingPatientIdentifierNotificationTests(TestCase):
	def test_patient_update_notifies_every_identifying_user(self):
		first_user = User.objects.create_user(username='first', password='password')
		second_user = User.objects.create_user(username='second', password='password')
		patient = Patient.objects.create(
			patient_id='PAT-001',
			is_identified=True,
			identified_by=first_user,
			status='admitted',
		)
		patient.identified_by_users.add(first_user, second_user)

		patient.status = 'released'
		patient.save()

		updates = Notification.objects.filter(
			patient=patient,
			title='Patient Released',
		)
		self.assertSetEqual(
			set(updates.values_list('user__username', flat=True)),
			{'first', 'second'},
		)

# Create your tests here.
