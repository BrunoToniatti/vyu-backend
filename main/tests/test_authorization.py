from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from main.models.user_manager import UserManager
from main.models.user_app import UserApp
from main.models.restaurant import Restaurant


class AuthorizationSecurityTests(TestCase):
    """
    Critical Security Suite:
    - IDOR / BOLA Prevention (Manager A cannot access or modify Manager B's restaurant)
    - Role Isolation & Privilege Escalation Prevention (App User cannot manage restaurants)
    - IsRestaurantOwner Dual Verification (Type check + Ownership check)
    """

    def setUp(self):
        self.client_a = APIClient()
        self.client_b = APIClient()
        self.client_app = APIClient()

        # Manager A
        self.manager_a = UserManager.objects.create(
            first_name="Manager",
            last_name="Alpha",
            phone_number="11911112222",
            email="manager.a@example.com",
            username="manager_a"
        )
        self.manager_a.set_password("ManagerAlphaPass123!")
        self.manager_a.save()

        # Manager B
        self.manager_b = UserManager.objects.create(
            first_name="Manager",
            last_name="Beta",
            phone_number="11933334444",
            email="manager.b@example.com",
            username="manager_b"
        )
        self.manager_b.set_password("ManagerBetaPass123!")
        self.manager_b.save()

        # App User (Customer)
        self.app_user = UserApp.objects.create(
            first_name="User",
            last_name="Customer",
            phone_number="11955556666",
            email="customer@example.com",
            username="customer_app"
        )
        self.app_user.set_password("CustomerPass123!")
        self.app_user.save()

        # Generate JWT tokens directly
        from main.services.auth_service import AuthService
        token_a = AuthService._generate_tokens_for_user(self.manager_a, "MANAGER")['access']
        self.client_a.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}')

        token_b = AuthService._generate_tokens_for_user(self.manager_b, "MANAGER")['access']
        self.client_b.credentials(HTTP_AUTHORIZATION=f'Bearer {token_b}')

        token_app = AuthService._generate_tokens_for_user(self.app_user, "APP_USER")['access']
        self.client_app.credentials(HTTP_AUTHORIZATION=f'Bearer {token_app}')

        # Manager A creates Restaurant A
        res_a = self.client_a.post('/api/restaurants/', {
            "name": "Restaurante Alpha",
            "cnpj": "11111111000111",
            "contact_phone": "11911112222",
            "address": "Av Paulista, 1000",
        }, format='json')
        self.restaurant_a_id = res_a.data['data']['id']

        # Manager B creates Restaurant B
        res_b = self.client_b.post('/api/restaurants/', {
            "name": "Restaurante Beta",
            "cnpj": "22222222000122",
            "contact_phone": "11933334444",
            "address": "Av Faria Lima, 2000",
        }, format='json')
        self.restaurant_b_id = res_b.data['data']['id']

    def test_idor_manager_a_cannot_view_restaurant_b(self):
        """
        Tests that Manager A cannot view Restaurant B's administrative details,
        even if Manager A knows Restaurant B's ID.
        """
        response = self.client_a.get(f'/api/restaurants/{self.restaurant_b_id}/')
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_idor_manager_a_cannot_update_restaurant_b(self):
        """
        Tests that Manager A cannot update Restaurant B.
        """
        update_payload = {"name": "Hacked Restaurant Name"}
        response = self.client_a.put(f'/api/restaurants/{self.restaurant_b_id}/', update_payload, format='json')
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        # Verify restaurant name in DB was NOT changed
        restaurant_b = Restaurant.objects.get(id=self.restaurant_b_id)
        self.assertEqual(restaurant_b.name, "Restaurante Beta")

    def test_idor_manager_a_cannot_delete_restaurant_b(self):
        """
        Tests that Manager A cannot delete Restaurant B.
        """
        response = self.client_a.delete(f'/api/restaurants/{self.restaurant_b_id}/')
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        # Verify restaurant still exists
        self.assertTrue(Restaurant.objects.filter(id=self.restaurant_b_id).exists())

    def test_privilege_escalation_app_user_cannot_create_restaurant(self):
        """
        Tests that an App User (Consumer) cannot create a restaurant.
        """
        payload = {
            "name": "Restaurante Fake",
            "cnpj": "33333333000133",
            "contact_phone": "11988889999",
            "address": "Rua Augusta, 500",
        }
        response = self.client_app.post('/api/restaurants/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_privilege_escalation_app_user_cannot_access_manager_admin_endpoints(self):
        """
        Tests that an App User cannot access manager administrative endpoints.
        """
        response = self.client_app.get(f'/api/restaurants/{self.restaurant_a_id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
