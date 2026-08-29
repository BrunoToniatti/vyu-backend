from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from main.models.user_manager import UserManager
from main.models.restaurant import Restaurant


class PublicRestaurantSearchTests(TestCase):
    """
    Test suite for Public Restaurant Search & Retrieval.
    Ensures that public consumer endpoints return only sanitized public information.
    """

    def setUp(self):
        self.client = APIClient()

        self.manager = UserManager.objects.create(
            first_name="Leonardo",
            last_name="Gerente",
            phone_number="11944443333",
            email="leonardo.manager@example.com",
            username="leonardo_mgr"
        )
        self.manager.set_password("ManagerPass123!")
        self.manager.save()

        # Create restaurants
        self.r1 = Restaurant.objects.create(
            name="Pizzaria Bella Napoli",
            cnpj="12345678000101",
            manager=self.manager,
            contact_phone="1132221111",
            address="Rua Pamplona, 500, Jardim Paulista, São Paulo - SP",
            site="https://bellanapoli.example.com",
            instagram="@bellanapoli",
            path_logo="https://storage.example.com/bellanapoli.jpg"
        )

        self.r2 = Restaurant.objects.create(
            name="Sushi Matsu",
            cnpj="98765432000102",
            manager=self.manager,
            contact_phone="1133332222",
            address="Rua dos Pinheiros, 800, Pinheiros, São Paulo - SP",
            site="https://sushimatsu.example.com",
            instagram="@sushimatsu",
            path_logo="https://storage.example.com/sushimatsu.jpg"
        )

    def test_public_restaurant_list_success(self):
        """
        Tests public listing of all restaurants without authentication.
        """
        response = self.client.get('/api/restaurants/public/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['count'], 2)

        # Verify public schema (no manager_id, no sensitive internals)
        item = response.data['data'][0]
        self.assertIn('name', item)
        self.assertIn('address', item)
        self.assertIn('contact_phone', item)
        self.assertNotIn('manager_id', item)
        self.assertNotIn('manager', item)

    def test_public_restaurant_detail_success(self):
        """
        Tests public retrieval of a single restaurant by ID.
        """
        response = self.client.get(f'/api/restaurants/public/{self.r1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Pizzaria Bella Napoli')
        self.assertNotIn('manager_id', response.data['data'])
        self.assertNotIn('manager', response.data['data'])

    def test_search_by_name(self):
        """
        Tests filtering restaurants by name.
        """
        response = self.client.get('/api/restaurants/public/?search=Sushi')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['name'], 'Sushi Matsu')

    def test_search_by_address(self):
        """
        Tests filtering restaurants by address keyword.
        """
        response = self.client.get('/api/restaurants/public/?search=Pinheiros')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['name'], 'Sushi Matsu')

    def test_search_with_no_matches(self):
        """
        Tests search query that matches no restaurants.
        """
        response = self.client.get('/api/restaurants/public/?search=ChurrascariaInexistente')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['data']), 0)
