"""
Iteration 37 - RDV chez Titelli & Demandes Spécialistes Testing
Tests for:
- RDV social booking system (friendly/romantic offers)
- Invitations and chat
- Romantic subscription
- Specialist requests
- Lifestyle passes (Healthy, Better You, MVP)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
CLIENT_EMAIL = "test.client@titelli.com"
CLIENT_PASSWORD = "Test123!"
ENTERPRISE_EMAIL = "test.entreprise@titelli.com"
ENTERPRISE_PASSWORD = "Test123!"


class TestRdvCategories:
    """Test RDV categories endpoint - public"""
    
    def test_get_rdv_categories(self):
        """GET /api/rdv/categories - should return categories list"""
        response = requests.get(f"{BASE_URL}/api/rdv/categories")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        # Verify category structure
        cat = data["categories"][0]
        assert "id" in cat
        assert "name" in cat
        assert "icon" in cat
        print(f"SUCCESS: Got {len(data['categories'])} RDV categories")


class TestSpecialistCategories:
    """Test Specialist categories endpoint - public"""
    
    def test_get_specialist_categories(self):
        """GET /api/specialists/categories - should return categories list"""
        response = requests.get(f"{BASE_URL}/api/specialists/categories")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        # Verify category structure
        cat = data["categories"][0]
        assert "id" in cat
        assert "name" in cat
        print(f"SUCCESS: Got {len(data['categories'])} specialist categories")


class TestLifestylePasses:
    """Test Lifestyle Passes endpoint - public"""
    
    def test_get_lifestyle_passes(self):
        """GET /api/specialists/passes - should return passes with prices"""
        response = requests.get(f"{BASE_URL}/api/specialists/passes")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "passes" in data
        
        passes = data["passes"]
        # Verify all 3 passes exist
        assert "healthy" in passes, "Missing 'healthy' pass"
        assert "better_you" in passes, "Missing 'better_you' pass"
        assert "mvp" in passes, "Missing 'mvp' pass"
        
        # Verify prices
        assert passes["healthy"]["price"] == 99.00, f"Healthy pass should be 99 CHF, got {passes['healthy']['price']}"
        assert passes["better_you"]["price"] == 149.00, f"Better You pass should be 149 CHF, got {passes['better_you']['price']}"
        assert passes["mvp"]["price"] == 299.00, f"MVP pass should be 299 CHF, got {passes['mvp']['price']}"
        
        print(f"SUCCESS: Lifestyle passes verified - Healthy: {passes['healthy']['price']} CHF, Better You: {passes['better_you']['price']} CHF, MVP: {passes['mvp']['price']} CHF")


class TestAuthenticatedRdvEndpoints:
    """Test RDV endpoints that require authentication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token"""
        # Try client login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Could not login with client credentials: {login_response.text}")
        
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user = login_response.json().get("user", {})
        print(f"Logged in as: {self.user.get('email')}")
    
    def test_get_rdv_stats(self):
        """GET /api/rdv/stats - should return user statistics"""
        response = requests.get(f"{BASE_URL}/api/rdv/stats", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "offers_created" in data
        assert "offers_confirmed" in data
        assert "invitations_received" in data
        assert "has_romantic_subscription" in data
        
        print(f"SUCCESS: RDV stats - offers_created: {data['offers_created']}, has_romantic: {data['has_romantic_subscription']}")
    
    def test_get_romantic_subscription_status(self):
        """GET /api/rdv/subscriptions/romantic/status - should return subscription status"""
        response = requests.get(f"{BASE_URL}/api/rdv/subscriptions/romantic/status", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "has_subscription" in data
        
        if not data["has_subscription"]:
            assert "price" in data
            assert data["price"] == 200.00, f"Romantic subscription should be 200 CHF, got {data['price']}"
        
        print(f"SUCCESS: Romantic subscription status - has_subscription: {data['has_subscription']}")
    
    def test_create_friendly_offer(self):
        """POST /api/rdv/offers - create a friendly offer (free)"""
        offer_data = {
            "title": f"TEST_Brunch amical {uuid.uuid4().hex[:8]}",
            "description": "Test offer for automated testing",
            "offer_type": "friendly",
            "category": "restaurant",
            "location": "Lausanne",
            "price_per_person": 25.0
        }
        
        response = requests.post(f"{BASE_URL}/api/rdv/offers", 
                                 json=offer_data, 
                                 headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "offer_id" in data
        assert "offer" in data
        assert data["offer"]["offer_type"] == "friendly"
        assert data["offer"]["status"] == "open"
        
        print(f"SUCCESS: Created friendly offer with ID: {data['offer_id']}")
        
        # Store for cleanup
        self.created_offer_id = data["offer_id"]
    
    def test_get_offers_list(self):
        """GET /api/rdv/offers - should return list of offers"""
        response = requests.get(f"{BASE_URL}/api/rdv/offers?offer_type=friendly", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "offers" in data
        assert "total" in data
        
        print(f"SUCCESS: Got {len(data['offers'])} friendly offers (total: {data['total']})")
    
    def test_get_my_offers(self):
        """GET /api/rdv/offers/my - should return user's own offers"""
        response = requests.get(f"{BASE_URL}/api/rdv/offers/my", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "offers" in data
        assert "count" in data
        
        print(f"SUCCESS: Got {data['count']} of my offers")
    
    def test_get_received_invitations(self):
        """GET /api/rdv/invitations/received - should return received invitations"""
        response = requests.get(f"{BASE_URL}/api/rdv/invitations/received", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "invitations" in data
        assert "count" in data
        
        print(f"SUCCESS: Got {data['count']} received invitations")
    
    def test_romantic_offer_requires_subscription(self):
        """POST /api/rdv/offers - romantic offer should require subscription"""
        offer_data = {
            "title": f"TEST_Date romantique {uuid.uuid4().hex[:8]}",
            "description": "Test romantic offer",
            "offer_type": "romantic",
            "category": "restaurant",
            "location": "Lausanne"
        }
        
        response = requests.post(f"{BASE_URL}/api/rdv/offers", 
                                 json=offer_data, 
                                 headers=self.headers)
        
        # Should return 402 if no subscription, or 200 if has subscription
        assert response.status_code in [200, 402], f"Expected 200 or 402, got {response.status_code}: {response.text}"
        
        if response.status_code == 402:
            print("SUCCESS: Romantic offer correctly requires subscription (402)")
        else:
            print("SUCCESS: User has romantic subscription, offer created")


class TestAuthenticatedSpecialistEndpoints:
    """Test Specialist endpoints that require authentication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Could not login: {login_response.text}")
        
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user = login_response.json().get("user", {})
    
    def test_create_specialist_request(self):
        """POST /api/specialists/requests - create a specialist request"""
        request_data = {
            "title": f"TEST_Recherche bijoutier {uuid.uuid4().hex[:8]}",
            "description": "Je recherche un bijoutier pour créer une bague sur mesure avec un design unique",
            "category": "artisanat",
            "urgency": "normal",
            "budget_min": 200,
            "budget_max": 500,
            "location": "Lausanne"
        }
        
        response = requests.post(f"{BASE_URL}/api/specialists/requests", 
                                 json=request_data, 
                                 headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "request_id" in data
        assert "request" in data
        assert data["request"]["status"] == "open"
        
        print(f"SUCCESS: Created specialist request with ID: {data['request_id']}")
    
    def test_get_specialist_requests(self):
        """GET /api/specialists/requests - should return list of requests"""
        response = requests.get(f"{BASE_URL}/api/specialists/requests", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "requests" in data
        assert "total" in data
        
        print(f"SUCCESS: Got {len(data['requests'])} specialist requests (total: {data['total']})")
    
    def test_get_my_specialist_requests(self):
        """GET /api/specialists/requests/my - should return user's own requests"""
        response = requests.get(f"{BASE_URL}/api/specialists/requests/my", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "requests" in data
        assert "count" in data
        
        print(f"SUCCESS: Got {data['count']} of my specialist requests")
    
    def test_get_my_passes(self):
        """GET /api/specialists/passes/my - should return user's active passes"""
        response = requests.get(f"{BASE_URL}/api/specialists/passes/my", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "passes" in data
        assert "count" in data
        
        print(f"SUCCESS: Got {data['count']} active lifestyle passes")


class TestEnterpriseSpecialistResponse:
    """Test enterprise-specific specialist endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as enterprise"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Could not login as enterprise: {login_response.text}")
        
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user = login_response.json().get("user", {})
        print(f"Logged in as enterprise: {self.user.get('email')}")
    
    def test_enterprise_can_view_requests(self):
        """Enterprise should be able to view specialist requests"""
        response = requests.get(f"{BASE_URL}/api/specialists/requests", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "requests" in data
        
        print(f"SUCCESS: Enterprise can view {len(data['requests'])} specialist requests")


class TestRomanticSubscriptionFlow:
    """Test romantic subscription Stripe checkout flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Could not login: {login_response.text}")
        
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_subscribe_romantic_returns_checkout_url(self):
        """POST /api/rdv/subscriptions/romantic - should return Stripe checkout URL"""
        response = requests.post(f"{BASE_URL}/api/rdv/subscriptions/romantic", headers=self.headers)
        
        # Should return 200 with checkout_url or has_subscription
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        if data.get("has_subscription"):
            print("SUCCESS: User already has romantic subscription")
        else:
            assert "checkout_url" in data, "Expected checkout_url in response"
            assert "stripe.com" in data["checkout_url"], "Checkout URL should be Stripe"
            print(f"SUCCESS: Got Stripe checkout URL for romantic subscription")


class TestLifestylePassSubscriptionFlow:
    """Test lifestyle pass Stripe checkout flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Could not login: {login_response.text}")
        
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_subscribe_healthy_pass_returns_checkout_url(self):
        """POST /api/specialists/passes/subscribe - should return Stripe checkout URL"""
        response = requests.post(f"{BASE_URL}/api/specialists/passes/subscribe", 
                                 json={"pass_type": "healthy"},
                                 headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        if data.get("has_subscription"):
            print("SUCCESS: User already has healthy pass")
        else:
            assert "checkout_url" in data, "Expected checkout_url in response"
            assert "stripe.com" in data["checkout_url"], "Checkout URL should be Stripe"
            print(f"SUCCESS: Got Stripe checkout URL for Healthy pass")


class TestUnauthenticatedAccess:
    """Test that protected endpoints require authentication"""
    
    def test_rdv_stats_requires_auth(self):
        """GET /api/rdv/stats - should require authentication"""
        response = requests.get(f"{BASE_URL}/api/rdv/stats")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("SUCCESS: /api/rdv/stats correctly requires authentication")
    
    def test_rdv_offers_requires_auth(self):
        """GET /api/rdv/offers - should require authentication"""
        response = requests.get(f"{BASE_URL}/api/rdv/offers")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("SUCCESS: /api/rdv/offers correctly requires authentication")
    
    def test_specialist_requests_requires_auth(self):
        """GET /api/specialists/requests - should require authentication"""
        response = requests.get(f"{BASE_URL}/api/specialists/requests")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("SUCCESS: /api/specialists/requests correctly requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
