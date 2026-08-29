from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from main.models.user_manager import UserManager
from main.models.restaurant import Restaurant


class RestaurantManagementTests(TestCase):
    """
    Test suite for Restaurant CRUD operations by authenticated Managers,
    verifying ownership association, validation, and mass assignment protection.
    """

    def setUp(self):
        self.client = APIClient()

        # Create Manager
        self.manager = UserManager.objects.create(
            first_name="Bruno",
            last_name="Toniatti",
            phone_number="11955554444",
            email="bruno.manager@example.com",
            username="bruno_manager"
        )
        self.manager.set_password("ManagerPassword123!")
        self.manager.save()

        # Generate JWT token directly for test client
        from main.services.auth_service import AuthService
        token_data = AuthService._generate_tokens_for_user(self.manager, "MANAGER")
        self.token = token_data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.restaurant_url = '/api/restaurants/'
        self.valid_payload = {
            "name": "Bistrô Paris 6",
            "cnpj": "12345678000195",
            "contact_phone": "1130004000",
            "address": "Rua Haddock Lobo, 1240, Jardins, São Paulo - SP",
            "site": "https://bistroparis.example.com",
            "instagram": "@bistroparis",
            "path_logo": "https://storage.example.com/logos/paris6.png"
        }

    def test_manager_creates_restaurant_success(self):
        """
        Tests successful creation of a restaurant by authenticated manager.
        """
        response = self.client.post(self.restaurant_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['name'], 'Bistrô Paris 6')
        self.assertEqual(response.data['data']['cnpj'], '12345678000195')
        self.assertEqual(response.data['data']['manager_id'], self.manager.id)

        # Verify in database
        restaurant = Restaurant.objects.get(id=response.data['data']['id'])
        self.assertEqual(restaurant.manager_id, self.manager.id)
        self.assertEqual(self.manager.restaurant_count, 1)

    def test_server_side_manager_assignment_ignores_payload_manager_id(self):
        """
        Tests that sending a fake manager_id in the payload is ignored and the server
        strictly assigns the authenticated manager from the verified JWT.
        """
        payload = self.valid_payload.copy()
        payload['manager_id'] = 999
        payload['manager'] = 999

        response = self.client.post(self.restaurant_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['manager_id'], self.manager.id)

    def test_manager_list_own_restaurants(self):
        """
        Tests listing restaurants owned by the authenticated manager.
        """
        # Create 2 restaurants
        self.client.post(self.restaurant_url, self.valid_payload, format='json')
        payload2 = self.valid_payload.copy()
        payload2['name'] = "Bistrô Paris 6 - Filial"
        self.client.post(self.restaurant_url, payload2, format='json')

        response = self.client.get(self.restaurant_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['data']), 2)

    def test_manager_get_single_restaurant(self):
        """
        Tests retrieving a single restaurant owned by the manager.
        """
        create_res = self.client.post(self.restaurant_url, self.valid_payload, format='json')
        restaurant_id = create_res.data['data']['id']

        response = self.client.get(f'/api/restaurants/{restaurant_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Bistrô Paris 6')

    def test_manager_update_restaurant(self):
        """
        Tests updating an owned restaurant.
        """
        create_res = self.client.post(self.restaurant_url, self.valid_payload, format='json')
        restaurant_id = create_res.data['data']['id']

        update_payload = {
            "name": "Bistrô Paris 6 - Atualizado",
            "contact_phone": "1133334444"
        }
        response = self.client.put(f'/api/restaurants/{restaurant_id}/', update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Bistrô Paris 6 - Atualizado')
        self.assertEqual(response.data['data']['contact_phone'], '1133334444')

    def test_mass_assignment_protection_on_update(self):
        """
        Tests that manager cannot alter manager_id or id via update payload.
        """
        create_res = self.client.post(self.restaurant_url, self.valid_payload, format='json')
        restaurant_id = create_res.data['data']['id']

        update_payload = {
            "id": 9999,
            "manager_id": 8888,
            "name": "Nome Alterado"
        }
        response = self.client.put(f'/api/restaurants/{restaurant_id}/', update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        restaurant = Restaurant.objects.get(id=restaurant_id)
        self.assertEqual(restaurant.id, restaurant_id)
        self.assertEqual(restaurant.manager_id, self.manager.id)

    def test_manager_delete_restaurant(self):
        """
        Tests deleting an owned restaurant.
        """
        create_res = self.client.post(self.restaurant_url, self.valid_payload, format='json')
        restaurant_id = create_res.data['data']['id']

        response = self.client.delete(f'/api/restaurants/{restaurant_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Restaurant.objects.filter(id=restaurant_id).exists())

    def test_invalid_cnpj_rejected(self):
        """
        Tests that invalid CNPJ format/length is rejected.
        """
        payload = self.valid_payload.copy()
        payload['cnpj'] = '123'

        response = self.client.post(self.restaurant_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
