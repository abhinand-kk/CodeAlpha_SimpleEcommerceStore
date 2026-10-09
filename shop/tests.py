from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Order, OrderItem
from django.contrib.auth.models import User
from decimal import Decimal

class StorefrontAndCartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.product1 = Product.objects.create(name='P1', slug='p1', price=Decimal('10.00'), stock=5, is_active=True)
        self.product2 = Product.objects.create(name='P2', slug='p2', price=Decimal('20.00'), stock=0, is_active=True)
        self.product3 = Product.objects.create(name='P3', slug='p3', price=Decimal('15.00'), stock=10, is_active=False)
        
    def test_storefront(self):
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'P1')
        self.assertContains(response, 'P2')
        self.assertNotContains(response, 'P3') # Inactive product hidden
        
    def test_cart_add_and_limits(self):
        # Normal add
        response = self.client.post(reverse('shop:cart_add', args=[self.product1.id]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        cart = self.client.session.get('cart')
        self.assertEqual(cart[str(self.product1.id)], 2)
        
        # Exceed stock limit
        response = self.client.post(reverse('shop:cart_add', args=[self.product1.id]), {'quantity': 4})
        cart = self.client.session.get('cart')
        self.assertEqual(cart[str(self.product1.id)], 2) # Should not have changed
        
    def test_checkout_auth_required(self):
        response = self.client.get(reverse('shop:checkout'))
        # redirects to login logic
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        
    def test_checkout_process_and_rollback(self):
        self.client.login(username='testuser', password='password123')
        self.client.post(reverse('shop:cart_add', args=[self.product1.id]), {'quantity': 2})
        
        post_data = {
            'customer_name': 'Test User',
            'email': 'test@test.com',
            'phone': '123456',
            'delivery_address': '123 Test St',
            'city': 'TestCity',
            'postal_code': '12345'
        }
        
        # Simulate stock depletion from another parallel process before checkout
        self.product1.stock = 1
        self.product1.save()
        
        response = self.client.post(reverse('shop:checkout'), post_data)
        self.assertEqual(response.status_code, 302)
        
        # Order should NOT have been created
        self.assertEqual(Order.objects.count(), 0)
        
        # Cart MUST be preserved
        cart = self.client.session.get('cart')
        self.assertIn(str(self.product1.id), cart)
        
    def test_successful_checkout(self):
        self.client.login(username='testuser', password='password123')
        self.client.post(reverse('shop:cart_add', args=[self.product1.id]), {'quantity': 2})
        
        post_data = {
            'customer_name': 'Test User',
            'email': 'test@test.com',
            'phone': '123456',
            'delivery_address': '123 Test St',
            'city': 'TestCity',
            'postal_code': '12345'
        }
        response = self.client.post(reverse('shop:checkout'), post_data)
        
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        
        order = Order.objects.first()
        self.assertEqual(order.total_amount, Decimal('20.00'))
        
        # Stock should be 5 - 2 = 3
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, 3)
        
        # Cart MUST be deleted/cleared
        self.assertNotIn('cart', self.client.session)
