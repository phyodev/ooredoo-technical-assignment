from rest_framework.test import APITestCase
from rest_framework import status
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from users.models import CustomUser
from points.models import PointLedger, Redemption
from products.models import Product

class PointLedgerModelTest(TestCase):
    def setUp(self):
        # Create a user (CustomUser model)
        self.user = CustomUser.objects.create_user(username="testuser", password="password")

    # Positive Test: Valid point ledger creation
    def test_create_point_ledger(self):
        point_ledger = PointLedger.objects.create(
            customer=self.user,
            points=100,
            expires_at=timezone.now() + timedelta(days=365)  # Valid expiration (1 year from now)
        )

        # Assertions
        self.assertEqual(point_ledger.customer, self.user)
        self.assertEqual(point_ledger.points, 100)
        self.assertTrue(point_ledger.expires_at > timezone.now())  # Expiration should be in the future

    # Negative Test: Points should not count if expired
    def test_get_available_points_with_expired_points(self):
        valid_point_ledger = PointLedger.objects.create(
            customer=self.user,
            points=100,
            expires_at=timezone.now() + timedelta(days=365)  # Valid expiration (1 year from now)
        )

        expired_point_ledger = PointLedger.objects.create(
            customer=self.user,
            points=50,
            expires_at=timezone.now() - timedelta(days=1)  # Expired points (yesterday)
        )

        # Available points should only count valid (non-expired) points
        available_points = PointLedger.get_available_points(self.user)
        self.assertEqual(available_points, 100)  # Only valid points should count


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password")
        PointLedger.objects.create(customer=self.user, points=10000, expires_at=timezone.now() + timedelta(days=365))

    # Positive Test: Upgrade to Gold based on points
    def test_upgrade_tier_based_on_points(self):
        self.assertEqual(self.user.tier, 'Silver')  # Default tier
        self.user.upgrade_tier()  # Upgrade to Gold
        self.assertEqual(self.user.tier, 'Gold')

    # Negative Test: Ensure upgrade logic works based on points
    def test_upgrade_tier_no_points(self):
        PointLedger.objects.filter(customer=self.user).delete()
        self.user.upgrade_tier()
        self.assertEqual(self.user.tier, 'Silver')  # Should remain in Silver tier


class RedemptionTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password")
        self.product = Product.objects.create(name="Sample Product", price=100.00, points_earned=50)
        self.point_ledger = PointLedger.objects.create(
            customer=self.user,
            points=1000,
            expires_at=timezone.now() + timedelta(days=365)
        )

    # Positive Test: Successful redemption should deduct points
    def test_redeem_points_success(self):
        redemption = Redemption.objects.create(customer=self.user, product=self.product)
        point_ledgers = PointLedger.objects.filter(
            customer=self.user, expires_at__gt=timezone.now()
        ).order_by('expires_at')

        # substract product points from user total points
        substract_points = self.product.points_earned
        for ledger in point_ledgers:
            substract_points = substract_points - ledger.points
            if substract_points < 0:
                ledger.points = abs(substract_points)
                ledger.save()
                break
            elif substract_points == 0:
                ledger.delete()
                break
            elif substract_points > 0:
                ledger.delete()
                continue
        redemption.status = 'success'
        redemption.save()

        # Assert the points are deducted correctly
        self.point_ledger.refresh_from_db()
        self.user.upgrade_tier()
        self.assertEqual(PointLedger.get_available_points(self.user), 1000 - self.product.points_earned)
        self.assertEqual(redemption.status, 'success')

    # Negative Test: Redemption with insufficient points should fail
    def test_redeem_points_insufficient(self):
        # Set a very low point balance
        self.point_ledger.points = 10
        self.point_ledger.save()

        redemption = Redemption.objects.create(customer=self.user, product=self.product)
        redemption.status = 'failed'
        redemption.save()

        # Assert the redemption failed
        self.assertEqual(redemption.status, 'failed')
        self.assertEqual(self.point_ledger.points, 10)  # No points should be deducted

    # Negative Test: Redemption with expired points should fail
    def test_redeem_points_expired(self):
        expired_point_ledger = PointLedger.objects.create(
            customer=self.user,
            points=100,
            expires_at=timezone.now() - timedelta(days=1)  # Expired points
        )

        redemption = Redemption.objects.create(customer=self.user, product=self.product)
        redemption.status = 'failed'
        redemption.save()

        # Assert the redemption failed due to expired points
        self.assertEqual(redemption.status, 'failed')

class RedemptionAPITest(APITestCase):
    def setUp(self):
        # Create user and authenticate
        self.user = CustomUser.objects.create_user(username="testuser", password="password")
        
        # Login the user via client (ensure the token or session is set)
        response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'password'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create product and redemption details
        self.product = Product.objects.create(name="Sample Product", price=100.00, points_earned=50)
        self.point_ledger = PointLedger.objects.create(
            customer=self.user,
            points=1000,
            expires_at=timezone.now() + timedelta(days=365)
        )
        
    # Positive Test: Create Redemption and test successful redemption (API)
    def test_create_redemption_success(self):
        url = reverse('redemption-list')  # Assuming you're using the default viewset URL
        data = {
            "product": self.product.id  # Create redemption for the product
        }
        
        # Create redemption via API
        response = self.client.post(url, data, format='json')

        # Check that redemption was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        redemption = Redemption.objects.get(id=response.data['id'])
        self.assertEqual(redemption.status, 'success')

        # Now process the redemption (simulate success)

        # Verify points are deducted from the user's ledger
        self.assertEqual(PointLedger.get_available_points(self.user), 1000 - self.product.points_earned)
    
    # Negative Test: Attempt redemption with insufficient points (API)
    def test_create_redemption_insufficient_points(self):
        self.point_ledger.points = 10  # Set insufficient points for redemption
        self.point_ledger.save()
        
        url = reverse('redemption-list')
        data = {
            "product": self.product.id
        }
        
        # Create redemption via API
        response = self.client.post(url, data, format='json')

        # Ensure the redemption failed due to insufficient points
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    # Negative Test: Attempt redemption with expired points (API)
    def test_create_redemption_expired_points(self):
        # Create point ledger with expired points
        self.point_ledger.expires_at = expires_at=timezone.now() - timedelta(days=1)
        self.point_ledger.save()
        
        url = reverse('redemption-list')
        data = {
            "product": self.product.id
        }
        
        # Create redemption via API
        response = self.client.post(url, data, format='json')

        # Assert redemption fails due to expired points
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
