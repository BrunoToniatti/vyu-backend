from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from main.models.user_manager import UserManager


class UserManagerTests(TestCase):
    """
    Test suite for UserManager registration, validation, security, and hashing.
    """

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/managers/'
        self.valid_payload = {
            "first_name": "Carlos",
            "last_name": "Silva",
            "phone_number": "11999998888",
            "path_photo": "https://images.example.com/carlos.jpg",
            "email": "carlos.gerente@example.com",
            "username": "carlos_gerente",
            "password": "StrongPassword123!"
        }

    def test_manager_registration_success(self):
        """
        Tests successful registration of a Manager.
        Verifies 201 status, database persistence, and hashed password.
        """
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['email'], 'carlos.gerente@example.com')
        self.assertEqual(response.data['data']['username'], 'carlos_gerente')

        # Password and password_hash must NEVER appear in response
        self.assertNotIn('password', response.data['data'])
        self.assertNotIn('password_hash', response.data['data'])

        # Verify database state
        manager = UserManager.objects.get(email='carlos.gerente@example.com')
        self.assertNotEqual(manager.password, 'StrongPassword123!')
        self.assertTrue(manager.password.startswith('pbkdf2_'))
        self.assertTrue(manager.check_password('StrongPassword123!'))
        self.assertFalse(manager.check_password('WrongPassword'))

    def test_duplicate_email_rejected(self):
        """
        Tests that duplicate email registration returns 400 Bad Request.
        """
        self.client.post(self.register_url, self.valid_payload, format='json')
        duplicate_payload = self.valid_payload.copy()
        duplicate_payload['username'] = 'carlos_other'

        response = self.client.post(self.register_url, duplicate_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', str(response.data))

    def test_duplicate_username_rejected(self):
        """
        Tests that duplicate username registration returns 400 Bad Request.
        """
        self.client.post(self.register_url, self.valid_payload, format='json')
        duplicate_payload = self.valid_payload.copy()
        duplicate_payload['email'] = 'other.carlos@example.com'

        response = self.client.post(self.register_url, duplicate_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', str(response.data))

    def test_short_password_rejected(self):
        """
        Tests that passwords shorter than 8 characters are rejected.
        """
        payload = self.valid_payload.copy()
        payload['password'] = 'short'
        payload['email'] = 'short.pass@example.com'
        payload['username'] = 'short_pass'

        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_phone_rejected(self):
        """
        Tests that invalid phone numbers are rejected.
        """
        payload = self.valid_payload.copy()
        payload['phone_number'] = '123'
        payload['email'] = 'invalid.phone@example.com'
        payload['username'] = 'invalid_phone'

        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mass_assignment_protection_on_registration(self):
        """
        Tests that clients cannot inject id or protected fields during registration.
        """
        payload = self.valid_payload.copy()
        payload['id'] = 9999
        payload['restaurant_count'] = 50
        payload['email'] = 'mass.assign@example.com'
        payload['username'] = 'mass_assign_mgr'

        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        manager = UserManager.objects.get(email='mass.assign@example.com')
        # Injected id 9999 should NOT be applied (auto-increment used)
        self.assertNotEqual(manager.id, 9999)
        self.assertEqual(manager.restaurant_count, 0)
