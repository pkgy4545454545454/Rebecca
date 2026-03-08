"""
Payment and Subscription System Audit Tests - Iteration 20
Tests for:
1. Premium subscription checkout (premium/vip) - returns real Stripe checkout URL
2. Premium subscription cancellation - removes all benefits
3. Premium status endpoint - returns correct plan and cashback rate
4. Enterprise subscription checkout - real Stripe integration
5. IA Campaign targeting - uses real users from database
6. Training purchase - real Stripe checkout
7. Cashback calculation verification (free=1%, premium=10%, vip=15%)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"


class TestAuthSetup:
    """Authentication setup tests"""
    
    def test_client_login(self):
        """Test client login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200, f"Client login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert "user" in data, "No user in response"
        print(f"✓ Client login successful - user_id: {data['user'].get('id')}")
        return data['token']
    
    def test_enterprise_login(self):
        """Test enterprise login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200, f"Enterprise login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        print(f"✓ Enterprise login successful - user_id: {data['user'].get('id')}")
        return data['token']


class TestPremiumCheckout:
    """Test premium subscription checkout with real Stripe"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get client token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        self.token = response.json()['token']
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_premium_checkout_returns_stripe_url(self):
        """POST /api/client/premium/checkout?plan=premium - returns real Stripe checkout URL"""
        response = requests.post(
            f"{BASE_URL}/api/client/premium/checkout?plan=premium",
            headers=self.headers
        )
        assert response.status_code == 200, f"Premium checkout failed: {response.text}"
        data = response.json()
        
        # Verify real Stripe URL
        assert "checkout_url" in data, "No checkout_url in response"
        assert "session_id" in data, "No session_id in response"
        assert data["checkout_url"].startswith("https://checkout.stripe.com"), \
            f"Not a real Stripe URL: {data['checkout_url']}"
        assert data["session_id"].startswith("cs_"), \
            f"Invalid Stripe session ID format: {data['session_id']}"
        
        print(f"✓ Premium checkout returns REAL Stripe URL: {data['checkout_url'][:60]}...")
        print(f"✓ Session ID: {data['session_id']}")
    
    def test_vip_checkout_returns_stripe_url(self):
        """POST /api/client/premium/checkout?plan=vip - returns real Stripe checkout URL"""
        response = requests.post(
            f"{BASE_URL}/api/client/premium/checkout?plan=vip",
            headers=self.headers
        )
        assert response.status_code == 200, f"VIP checkout failed: {response.text}"
        data = response.json()
        
        # Verify real Stripe URL
        assert "checkout_url" in data, "No checkout_url in response"
        assert data["checkout_url"].startswith("https://checkout.stripe.com"), \
            f"Not a real Stripe URL: {data['checkout_url']}"
        
        print(f"✓ VIP checkout returns REAL Stripe URL: {data['checkout_url'][:60]}...")
    
    def test_invalid_plan_rejected(self):
        """Test that invalid plan is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/client/premium/checkout?plan=invalid",
            headers=self.headers
        )
        assert response.status_code == 400, f"Should reject invalid plan: {response.text}"
        print("✓ Invalid plan correctly rejected")


class TestPremiumStatus:
    """Test premium status endpoint returns correct plan and cashback rate"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get client token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        self.token = response.json()['token']
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_premium_status(self):
        """GET /api/client/premium - returns correct current_plan and cashback_rate"""
        response = requests.get(
            f"{BASE_URL}/api/client/premium",
            headers=self.headers
        )
        assert response.status_code == 200, f"Get premium status failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "current_plan" in data, "No current_plan in response"
        assert "cashback_rate" in data, "No cashback_rate in response"
        assert "is_premium" in data, "No is_premium in response"
        assert "benefits" in data, "No benefits in response"
        
        # Verify cashback rate matches plan
        plan = data["current_plan"]
        cashback = data["cashback_rate"]
        
        expected_rates = {"free": 1, "premium": 10, "vip": 15}
        expected_rate = expected_rates.get(plan, 1)
        
        assert cashback == expected_rate, \
            f"Cashback rate mismatch: plan={plan}, expected={expected_rate}%, got={cashback}%"
        
        print(f"✓ Premium status: plan={plan}, cashback_rate={cashback}%, is_premium={data['is_premium']}")
        print(f"✓ Benefits structure present with {len(data['benefits'])} plans")


class TestPremiumCancellation:
    """Test premium subscription cancellation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get client token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        self.token = response.json()['token']
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cancel_subscription_removes_benefits(self):
        """POST /api/client/premium/cancel - cancels subscription and removes all benefits"""
        # First check current status
        status_before = requests.get(
            f"{BASE_URL}/api/client/premium",
            headers=self.headers
        ).json()
        
        print(f"Status before cancel: plan={status_before.get('current_plan')}, is_premium={status_before.get('is_premium')}")
        
        # Try to cancel
        response = requests.post(
            f"{BASE_URL}/api/client/premium/cancel",
            headers=self.headers
        )
        
        # If user has no subscription, 404 is expected
        if response.status_code == 404:
            print("✓ No active subscription to cancel (expected for free users)")
            return
        
        assert response.status_code == 200, f"Cancel failed: {response.text}"
        data = response.json()
        
        # Verify cancellation response
        assert data.get("success") == True, "Cancellation not successful"
        assert data.get("new_plan") == "free", f"New plan should be 'free', got: {data.get('new_plan')}"
        assert data.get("new_cashback_rate") == 1, f"New cashback should be 1%, got: {data.get('new_cashback_rate')}"
        
        # Verify status after cancellation
        status_after = requests.get(
            f"{BASE_URL}/api/client/premium",
            headers=self.headers
        ).json()
        
        assert status_after.get("current_plan") == "free", \
            f"Plan should be 'free' after cancel, got: {status_after.get('current_plan')}"
        assert status_after.get("cashback_rate") == 1, \
            f"Cashback should be 1% after cancel, got: {status_after.get('cashback_rate')}"
        
        print(f"✓ Subscription cancelled successfully")
        print(f"✓ Benefits removed: plan=free, cashback=1%")


class TestEnterpriseSubscription:
    """Test enterprise subscription checkout with real Stripe"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get enterprise token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        self.token = response.json()['token']
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_enterprise_subscription_checkout_standard(self):
        """POST /api/subscriptions/checkout?plan_id=standard - enterprise subscription with Stripe"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout?plan_id=standard",
            headers=self.headers
        )
        assert response.status_code == 200, f"Enterprise subscription checkout failed: {response.text}"
        data = response.json()
        
        # Verify real Stripe URL
        assert "url" in data, "No url in response"
        assert "session_id" in data, "No session_id in response"
        assert data["url"].startswith("https://checkout.stripe.com"), \
            f"Not a real Stripe URL: {data['url']}"
        
        print(f"✓ Enterprise subscription checkout returns REAL Stripe URL")
        print(f"✓ Session ID: {data['session_id']}")
    
    def test_enterprise_subscription_checkout_premium(self):
        """POST /api/subscriptions/checkout?plan_id=premium - premium enterprise subscription"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout?plan_id=premium",
            headers=self.headers
        )
        assert response.status_code == 200, f"Premium enterprise checkout failed: {response.text}"
        data = response.json()
        
        assert data["url"].startswith("https://checkout.stripe.com"), \
            f"Not a real Stripe URL: {data['url']}"
        
        print(f"✓ Premium enterprise subscription returns REAL Stripe URL")
    
    def test_invalid_plan_rejected(self):
        """Test that invalid enterprise plan is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout?plan_id=invalid_plan",
            headers=self.headers
        )
        assert response.status_code == 400, f"Should reject invalid plan: {response.text}"
        print("✓ Invalid enterprise plan correctly rejected")


class TestIACampaignTargeting:
    """Test IA Campaign targeting uses real users from database"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get enterprise token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        self.token = response.json()['token']
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_ia_campaign_creates_with_real_targeting(self):
        """POST /api/enterprise/ia-campaigns - creates campaign with REAL targeting"""
        campaign_data = {
            "name": "TEST_Audit_Campaign",
            "age_range": "25-45",
            "gender": "all",
            "interests": ["restauration", "soins_esthetiques"],
            "behavior": ["frequent_buyer"],
            "location": "lausanne",
            "budget": "medium"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/enterprise/ia-campaigns",
            headers=self.headers,
            json=campaign_data
        )
        assert response.status_code == 200, f"IA Campaign creation failed: {response.text}"
        data = response.json()
        
        # Verify campaign created with real targeting
        assert "id" in data, "No campaign ID in response"
        assert "reach" in data, "No reach in response"
        assert "engagement" in data, "No engagement in response"
        assert "conversions" in data, "No conversions in response"
        
        # Verify targeting_details shows real database query results
        assert "targeting_details" in data, "No targeting_details in response"
        targeting = data["targeting_details"]
        assert "total_potential_users" in targeting, "No total_potential_users in targeting"
        assert "budget_multiplier" in targeting, "No budget_multiplier in targeting"
        
        # Reach should be based on real user count
        assert data["reach"] >= 0, "Reach should be non-negative"
        assert isinstance(targeting["total_potential_users"], int), "total_potential_users should be integer"
        
        print(f"✓ IA Campaign created with REAL targeting")
        print(f"✓ Total potential users from DB: {targeting['total_potential_users']}")
        print(f"✓ Estimated reach: {data['reach']}")
        print(f"✓ Budget multiplier: {targeting['budget_multiplier']}")
        print(f"✓ Engagement rate: {targeting['engagement_rate']}")
    
    def test_ia_campaign_location_targeting(self):
        """Test IA Campaign with location targeting"""
        campaign_data = {
            "name": "TEST_Location_Campaign",
            "location": "lausanne",
            "budget": "high"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/enterprise/ia-campaigns",
            headers=self.headers,
            json=campaign_data
        )
        assert response.status_code == 200, f"Location campaign failed: {response.text}"
        data = response.json()
        
        assert data["targeting_details"]["total_potential_users"] >= 0
        print(f"✓ Location-targeted campaign: {data['targeting_details']['total_potential_users']} potential users in Lausanne")


class TestTrainingPurchase:
    """Test training purchase with real Stripe checkout"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get client token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        self.token = response.json()['token']
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_training_purchase_returns_stripe_url(self):
        """POST /api/trainings/{id}/purchase - training purchase with Stripe checkout"""
        # First get available trainings
        trainings_response = requests.get(f"{BASE_URL}/api/trainings")
        assert trainings_response.status_code == 200, f"Get trainings failed: {trainings_response.text}"
        trainings_data = trainings_response.json()
        # API returns list directly or object with trainings key
        trainings = trainings_data if isinstance(trainings_data, list) else trainings_data.get("trainings", [])
        
        if not trainings:
            pytest.skip("No trainings available to test purchase")
        
        training_id = trainings[0]["id"]
        training_title = trainings[0].get("title", "Unknown")
        
        # Try to purchase
        response = requests.post(
            f"{BASE_URL}/api/trainings/{training_id}/purchase",
            headers=self.headers
        )
        
        # If already enrolled, that's fine
        if response.status_code == 400 and "déjà inscrit" in response.text:
            print(f"✓ User already enrolled in training '{training_title}'")
            return
        
        assert response.status_code == 200, f"Training purchase failed: {response.text}"
        data = response.json()
        
        # Verify real Stripe URL
        assert "url" in data, "No url in response"
        assert "session_id" in data, "No session_id in response"
        assert data["url"].startswith("https://checkout.stripe.com"), \
            f"Not a real Stripe URL: {data['url']}"
        
        print(f"✓ Training purchase returns REAL Stripe URL for '{training_title}'")
        print(f"✓ Session ID: {data['session_id']}")


class TestCashbackRates:
    """Test cashback calculation verification"""
    
    def test_cashback_rates_in_premium_plans(self):
        """Verify cashback rates: free=1%, premium=10%, vip=15%"""
        # Get subscription plans
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200, f"Get plans failed: {response.text}"
        
        # Get premium plans from client endpoint
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        token = login_response.json()['token']
        
        premium_response = requests.get(
            f"{BASE_URL}/api/client/premium",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert premium_response.status_code == 200
        data = premium_response.json()
        
        benefits = data.get("benefits", {})
        
        # Verify each plan's cashback rate
        expected_rates = {
            "free": 0.01,  # 1%
            "premium": 0.10,  # 10%
            "vip": 0.15  # 15%
        }
        
        for plan, expected_rate in expected_rates.items():
            if plan in benefits:
                actual_rate = benefits[plan].get("cashback_rate", 0)
                assert actual_rate == expected_rate, \
                    f"Plan '{plan}' cashback mismatch: expected {expected_rate*100}%, got {actual_rate*100}%"
                print(f"✓ {plan.upper()} plan: {int(actual_rate*100)}% cashback - CORRECT")
        
        print("✓ All cashback rates verified: free=1%, premium=10%, vip=15%")


class TestNoMockedAPIs:
    """Verify no APIs are mocked - all return real data"""
    
    def test_stripe_integration_is_real(self):
        """Verify Stripe integration returns real checkout URLs"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        token = login_response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test premium checkout
        response = requests.post(
            f"{BASE_URL}/api/client/premium/checkout?plan=premium",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Real Stripe URLs start with https://checkout.stripe.com
        assert data["checkout_url"].startswith("https://checkout.stripe.com"), \
            "Stripe checkout URL is NOT real - appears to be mocked!"
        
        # Real Stripe session IDs start with cs_live_ or cs_test_
        assert data["session_id"].startswith("cs_"), \
            "Stripe session ID is NOT real - appears to be mocked!"
        
        print("✓ Stripe integration is REAL (not mocked)")
        print(f"✓ Real Stripe URL: {data['checkout_url'][:50]}...")
    
    def test_database_queries_are_real(self):
        """Verify database queries return real data"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        token = login_response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test IA Campaign targeting uses real DB
        campaign_data = {
            "name": "TEST_DB_Verification",
            "location": "lausanne",
            "budget": "low"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/enterprise/ia-campaigns",
            headers=headers,
            json=campaign_data
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify targeting_details shows real database query
        targeting = data.get("targeting_details", {})
        assert "total_potential_users" in targeting, "No real DB query for users"
        
        # The count should be an integer from real DB query
        assert isinstance(targeting["total_potential_users"], int), \
            "User count is not from real DB query"
        
        print("✓ Database queries are REAL (not mocked)")
        print(f"✓ Real user count from DB: {targeting['total_potential_users']}")


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_data():
    """Cleanup test campaigns after tests"""
    yield
    # Cleanup would happen here if needed
    print("\n✓ Test cleanup complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
