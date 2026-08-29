from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from main.models.user_manager import UserManager
from main.models.user_app import UserApp


from django.core.cache import cache


class AuthJWTTests(TestCase):
    """
    Test suite for SimpleJWT authentication, token claims, token refresh,
    and anti-enumeration security.
    """

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.manager_login_url = '/api/auth/manager/login/'
        self.app_login_url = '/api/auth/app/login/'
        self.refresh_url = '/api/auth/token/refresh/'

        # Create test Manager
        self.manager = UserManager.objects.create(
            first_name="Roberto",
            last_name="Gerente",
            phone_number="11977776666",
            email="roberto.gerente@example.com",
            username="roberto_gerente"
        )
        self.manager.set_password("ManagerSecret123!")
        self.manager.save()

        # Create test App User
        self.app_user = UserApp.objects.create(
            first_name="Julia",
            last_name="Cliente",
            phone_number="11966665555",
            email="julia.cliente@example.com",
            username="julia_cliente"
        )
        self.app_user.set_password("ClientSecret123!")
        self.app_user.save()

    def test_manager_login_with_email_success(self):
        """
        Tests Manager login using email and correct password.
        """
        payload = {
            "identifier": "roberto.gerente@example.com",
            "password": "ManagerSecret123!"
        }
        response = self.client.post(self.manager_login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['data']['user_type'], 'MANAGER')

        # Verify SimpleJWT token claims
        token = AccessToken(response.data['data']['access'])
        self.assertEqual(token['user_id'], self.manager.id)
        self.assertEqual(token['user_type'], 'MANAGER')
        self.assertEqual(token['username'], 'roberto_gerente')

    def test_manager_login_with_username_success(self):
        """
        Tests Manager login using username and correct password.
        """
        payload = {
            "identifier": "roberto_gerente",
            "password": "ManagerSecret123!"
        }
        response = self.client.post(self.manager_login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])

    def test_app_user_login_success(self):
        """
        Tests App User login using email and correct password.
        """
        payload = {
            "identifier": "julia.cliente@example.com",
            "password": "ClientSecret123!"
        }
        response = self.client.post(self.app_login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertEqual(response.data['data']['user_type'], 'APP_USER')

        token = AccessToken(response.data['data']['access'])
        self.assertEqual(token['user_id'], self.app_user.id)
        self.assertEqual(token['user_type'], 'APP_USER')

    def test_login_anti_enumeration_on_wrong_password(self):
        """
        Tests that wrong password returns generic 401 response to prevent user enumeration.
        """
        payload = {
            "identifier": "roberto.gerente@example.com",
            "password": "IncorrectPassword"
        }
        response = self.client.post(self.manager_login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Credenciais inválidas", str(response.data))

    def test_login_anti_enumeration_on_nonexistent_user(self):
        """
        Tests that non-existent user returns the EXACT same generic 401 response.
        """
        payload = {
            "identifier": "nonexistent.user@example.com",
            "password": "AnyPassword123!"
        }
        response = self.client.post(self.manager_login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Credenciais inválidas", str(response.data))

    def test_token_refresh_flow(self):
        """
        Tests the token refresh endpoint using a valid refresh token.
        """
        login_response = self.client.post(
            self.manager_login_url,
            {"identifier": "roberto_gerente", "password": "ManagerSecret123!"},
            format='json'
        )
        refresh_token = login_response.data['data']['refresh']

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format='json'
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data['data'])

    def test_protected_route_without_token_rejected(self):
        """
        Tests that accessing a protected endpoint without JWT returns 401 Unauthorized.
        """
        response = self.client.get('/api/managers/me/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_protected_route_with_invalid_token_rejected(self):
        """
        Tests that accessing a protected endpoint with forged JWT returns 401.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid.fake.token')
        response = self.client.get('/api/managers/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_rate_throttling_triggered(self):
        """
        Tests that exceeding login attempts per minute triggers HTTP 429 Too Many Requests.
        """
        cache.clear()
        payload = {
            "identifier": "roberto.gerente@example.com",
            "password": "WrongPassword"
        }
        # Send 10 rapid failed login requests (exceeding/hitting threshold)
        throttled = False
        for _ in range(15):
            res = self.client.post(self.manager_login_url, payload, format='json')
            if res.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                throttled = True
                break

        self.assertTrue(throttled, "LoginRateThrottle should have throttled excessive login attempts with 429")
