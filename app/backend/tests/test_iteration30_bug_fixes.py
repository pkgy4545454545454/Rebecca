"""
Iteration 30 - Bug Fixes Testing
Tests for:
1. Enterprise subscription checkout - Stripe checkout URL generation
2. Client dashboard cart section - CartContext integration
3. Notification counters display
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

# Test credentials
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"


class TestAuthentication:
    """Authentication tests for both enterprise and client users"""
    
    def test_enterprise_login(self):
        """Test enterprise user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200, f"Enterprise login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not in response"
        assert "user" in data, "User not in response"
        assert data["user"]["user_type"] == "entreprise", "User type should be entreprise"
        print(f"✓ Enterprise login successful - User: {data['user']['first_name']} {data['user']['last_name']}")
    
    def test_client_login(self):
        """Test client user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200, f"Client login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not in response"
        assert "user" in data, "User not in response"
        assert data["user"]["user_type"] == "client", "User type should be client"
        print(f"✓ Client login successful - User: {data['user']['first_name']} {data['user']['last_name']}")


class TestSubscriptionCheckout:
    """Tests for subscription checkout functionality - Bug #1 fix verification"""
    
    @pytest.fixture
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Enterprise authentication failed")
    
    def test_get_subscription_plans(self):
        """Test fetching subscription plans"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200, f"Failed to get plans: {response.text}"
        data = response.json()
        assert "plans" in data, "Plans not in response"
        assert "addons" in data, "Addons not in response"
        assert "base_features" in data, "Base features not in response"
        
        # Verify standard plan exists
        plans = data["plans"]
        assert "standard" in plans, "Standard plan not found"
        assert plans["standard"]["price"] == 200.0, "Standard plan price incorrect"
        print(f"✓ Subscription plans fetched - {len(plans)} plans available")
    
    def test_subscription_checkout_standard_plan(self, enterprise_token):
        """Test creating checkout session for standard plan"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            params={"plan_id": "standard"},
            headers=headers
        )
        assert response.status_code == 200, f"Checkout creation failed: {response.text}"
        data = response.json()
        
        # Verify response contains Stripe checkout URL
        assert "url" in data, "URL not in response"
        assert "session_id" in data, "Session ID not in response"
        assert "checkout.stripe.com" in data["url"], "URL should be Stripe checkout URL"
        print(f"✓ Standard plan checkout created - Session: {data['session_id'][:20]}...")
    
    def test_subscription_checkout_guest_plan(self, enterprise_token):
        """Test creating checkout session for guest plan"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            params={"plan_id": "guest"},
            headers=headers
        )
        assert response.status_code == 200, f"Checkout creation failed: {response.text}"
        data = response.json()
        
        assert "url" in data, "URL not in response"
        assert "checkout.stripe.com" in data["url"], "URL should be Stripe checkout URL"
        print(f"✓ Guest plan checkout created")
    
    def test_subscription_checkout_premium_plan(self, enterprise_token):
        """Test creating checkout session for premium plan"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            params={"plan_id": "premium"},
            headers=headers
        )
        assert response.status_code == 200, f"Checkout creation failed: {response.text}"
        data = response.json()
        
        assert "url" in data, "URL not in response"
        assert "checkout.stripe.com" in data["url"], "URL should be Stripe checkout URL"
        print(f"✓ Premium plan checkout created")
    
    def test_subscription_checkout_invalid_plan(self, enterprise_token):
        """Test checkout with invalid plan returns error"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            params={"plan_id": "invalid_plan"},
            headers=headers
        )
        assert response.status_code == 400, "Should return 400 for invalid plan"
        print(f"✓ Invalid plan correctly rejected")
    
    def test_subscription_checkout_requires_auth(self):
        """Test checkout requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            params={"plan_id": "standard"}
        )
        assert response.status_code == 401, "Should return 401 without auth"
        print(f"✓ Checkout correctly requires authentication")


class TestClientDashboard:
    """Tests for client dashboard functionality - Bug #2 fix verification"""
    
    @pytest.fixture
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Client authentication failed")
    
    def test_client_orders_endpoint(self, client_token):
        """Test client can fetch their orders"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/orders", headers=headers)
        assert response.status_code == 200, f"Failed to get orders: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Orders should be a list"
        print(f"✓ Client orders fetched - {len(data)} orders")
    
    def test_client_notifications_endpoint(self, client_token):
        """Test client can fetch notifications"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code == 200, f"Failed to get notifications: {response.text}"
        data = response.json()
        assert "notifications" in data, "Notifications not in response"
        assert "unread_count" in data, "Unread count not in response"
        print(f"✓ Client notifications fetched - {data['unread_count']} unread")
    
    def test_client_cashback_balance(self, client_token):
        """Test client can fetch cashback balance"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/cashback/balance", headers=headers)
        assert response.status_code == 200, f"Failed to get cashback: {response.text}"
        data = response.json()
        assert "balance" in data, "Balance not in response"
        print(f"✓ Client cashback balance: {data['balance']} CHF")
    
    def test_client_profile_endpoint(self, client_token):
        """Test client can fetch their profile"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/client/profile", headers=headers)
        assert response.status_code == 200, f"Failed to get profile: {response.text}"
        data = response.json()
        assert "user" in data, "User not in response"
        print(f"✓ Client profile fetched")


class TestServicesAndProducts:
    """Tests for services and products - Cart functionality support"""
    
    def test_list_services(self):
        """Test listing available services"""
        response = requests.get(f"{BASE_URL}/api/services-products", params={"type": "service"})
        assert response.status_code == 200, f"Failed to get services: {response.text}"
        data = response.json()
        assert "items" in data, "Items not in response"
        assert "total" in data, "Total not in response"
        print(f"✓ Services listed - {data['total']} services available")
    
    def test_list_products(self):
        """Test listing available products"""
        response = requests.get(f"{BASE_URL}/api/services-products", params={"type": "product"})
        assert response.status_code == 200, f"Failed to get products: {response.text}"
        data = response.json()
        assert "items" in data, "Items not in response"
        print(f"✓ Products listed - {data['total']} products available")
    
    def test_get_service_detail(self):
        """Test getting service detail"""
        # First get list of services
        response = requests.get(f"{BASE_URL}/api/services-products", params={"type": "service", "limit": 1})
        if response.status_code == 200 and response.json().get("items"):
            service_id = response.json()["items"][0]["id"]
            detail_response = requests.get(f"{BASE_URL}/api/services-products/{service_id}")
            assert detail_response.status_code == 200, f"Failed to get service detail: {detail_response.text}"
            data = detail_response.json()
            assert "id" in data, "ID not in response"
            assert "name" in data, "Name not in response"
            assert "price" in data, "Price not in response"
            print(f"✓ Service detail fetched - {data['name']}")
        else:
            pytest.skip("No services available to test")


class TestNotificationCounters:
    """Tests for notification counters - Verifying real-time notification support"""
    
    @pytest.fixture
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Client authentication failed")
    
    def test_notifications_list(self, client_token):
        """Test notifications list endpoint"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code == 200, f"Failed to get notifications: {response.text}"
        data = response.json()
        assert "notifications" in data, "Notifications not in response"
        assert "unread_count" in data, "Unread count not in response"
        assert isinstance(data["notifications"], list), "Notifications should be a list"
        print(f"✓ Notifications list - {len(data['notifications'])} notifications, {data['unread_count']} unread")
    
    def test_friends_requests(self, client_token):
        """Test friend requests endpoint for notification counter"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/client/friend-requests", headers=headers)
        assert response.status_code == 200, f"Failed to get friend requests: {response.text}"
        data = response.json()
        assert "received" in data, "Received not in response"
        assert "sent" in data, "Sent not in response"
        print(f"✓ Friend requests - {len(data['received'])} received, {len(data['sent'])} sent")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
