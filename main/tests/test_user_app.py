from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from main.models.user_app import UserApp
from main.models.user_manager import UserManager


class UserAppTests(TestCase):
    """
    Test suite for UserApp (Customer) registration, validation, security, and hashing.
    """

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/users/'
        self.valid_payload = {
            "first_name": "Ana",
            "last_name": "Souza",
            "phone_number": "11988887777",
            "path_photo": "https://images.example.com/ana.jpg",
            "email": "ana.cliente@example.com",
            "username": "ana_cliente",
            "password": "CustomerPass123!"
        }

    def test_user_app_registration_success(self):
        """
        Tests successful registration of an App User.
        Verifies 201 status, database persistence, and PBKDF2 hashed password.
        """
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['email'], 'ana.cliente@example.com')
        self.assertEqual(response.data['data']['username'], 'ana_cliente')

        # Password must NEVER appear in response
        self.assertNotIn('password', response.data['data'])
        self.assertNotIn('password_hash', response.data['data'])

        # Verify database state
        user_app = UserApp.objects.get(email='ana.cliente@example.com')
        self.assertNotEqual(user_app.password, 'CustomerPass123!')
        self.assertTrue(user_app.password.startswith('pbkdf2_'))
        self.assertTrue(user_app.check_password('CustomerPass123!'))

    def test_duplicate_email_in_user_app_rejected(self):
        """
        Tests that duplicate email registration within user_app is rejected.
        """
        self.client.post(self.register_url, self.valid_payload, format='json')
        duplicate_payload = self.valid_payload.copy()
        duplicate_payload['username'] = 'ana_different'

        response = self.client.post(self.register_url, duplicate_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', str(response.data))

    def test_user_app_can_share_email_with_user_manager(self):
        """
        Tests that a manager can also register as an app user with the same email,
        confirming table isolation per architectural decision.
        """
        # Create manager with same email first
        UserManager.objects.create(
            first_name="Ana",
            last_name="Manager",
            phone_number="11988887777",
            email="ana.cliente@example.com",
            username="ana_manager_account",
            password="ManagerPass123!"
        )

        # Create app user with same email
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserApp.objects.filter(email='ana.cliente@example.com').exists())
        self.assertTrue(UserManager.objects.filter(email='ana.cliente@example.com').exists())

    def test_mass_assignment_protection_on_user_app(self):
        """
        Tests that clients cannot inject id or protected fields during user app registration.
        """
        payload = self.valid_payload.copy()
        payload['id'] = 8888
        payload['email'] = 'mass.assign.app@example.com'
        payload['username'] = 'mass_assign_app'

        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_app = UserApp.objects.get(email='mass.assign.app@example.com')
        self.assertNotEqual(user_app.id, 8888)
