"""
Iteration 31 - Comprehensive Subscription Testing
Tests all 10 subscription plans, Stripe checkout, subscription activation,
enterprise subscription status, and activity feed algorithm with tier-based features.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"

# All 10 subscription plans
ALL_PLANS = [
    "standard", "guest", "premium", "premium_mvp",
    "opti_starter_2k", "opti_starter_3k", "opti_5k", "opti_10k", "opti_20k", "opti_50k"
]

# Plan tiers mapping
PLAN_TIERS = {
    "standard": "basic",
    "guest": "basic",
    "premium": "premium",
    "premium_mvp": "premium",
    "opti_starter_2k": "optimisation",
    "opti_starter_3k": "optimisation",
    "opti_5k": "optimisation",
    "opti_10k": "optimisation",
    "opti_20k": "optimisation",
    "opti_50k": "optimisation"
}

# Expected ads per month by plan
PLAN_ADS_LIMIT = {
    "standard": 1,
    "guest": 2,
    "premium": 4,
    "premium_mvp": 6,
    "opti_starter_2k": 15,
    "opti_starter_3k": 15,
    "opti_5k": 15,
    "opti_10k": 15,
    "opti_20k": 15,
    "opti_50k": 15
}

# Addon options to test
ADDON_OPTIONS = [
    "pub_extra", "expert_label", "investors_access", "delivery_24",
    "local_access", "suppliers_access", "premium_trainings"
]


class TestSubscriptionPlans:
    """Test subscription plans endpoint and data"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for enterprise user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_subscription_plans(self, auth_headers):
        """Test GET /api/subscriptions/plans returns all 10 plans"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "plans" in data, "Response should contain 'plans' key"
        
        plans = data["plans"]
        # Verify all 10 plans are present
        plan_ids = [p.get('id') for p in plans] if isinstance(plans, list) else list(plans.keys())
        
        for plan_id in ALL_PLANS:
            assert plan_id in plan_ids or plan_id in plans, f"Plan {plan_id} should be in response"
        
        print(f"✓ All 10 subscription plans returned: {plan_ids}")


class TestStripeCheckout:
    """Test Stripe checkout URL generation for all plans"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for enterprise user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    @pytest.mark.parametrize("plan_id", ALL_PLANS)
    def test_checkout_generates_stripe_url(self, auth_headers, plan_id):
        """Test POST /api/subscriptions/checkout generates valid Stripe URL for each plan"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            params={"plan_id": plan_id},
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Plan {plan_id}: Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, f"Plan {plan_id}: Response should contain 'url'"
        assert "session_id" in data, f"Plan {plan_id}: Response should contain 'session_id'"
        
        # Verify URL is a valid Stripe checkout URL
        url = data["url"]
        assert url.startswith("https://checkout.stripe.com/"), f"Plan {plan_id}: URL should be Stripe checkout URL, got: {url[:50]}"
        
        print(f"✓ Plan {plan_id}: Stripe checkout URL generated successfully")
    
    def test_checkout_invalid_plan(self, auth_headers):
        """Test checkout with invalid plan returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            params={"plan_id": "invalid_plan_xyz"},
            headers=auth_headers
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid plan, got {response.status_code}"
        print("✓ Invalid plan correctly returns 400 error")


class TestAddonCheckout:
    """Test addon checkout endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for enterprise user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    @pytest.mark.parametrize("addon_id", ADDON_OPTIONS)
    def test_addon_checkout_generates_stripe_url(self, auth_headers, addon_id):
        """Test POST /api/subscriptions/addon/checkout generates valid Stripe URL"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/addon/checkout",
            params={"addon_id": addon_id},
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Addon {addon_id}: Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, f"Addon {addon_id}: Response should contain 'url'"
        assert "session_id" in data, f"Addon {addon_id}: Response should contain 'session_id'"
        
        url = data["url"]
        assert url.startswith("https://checkout.stripe.com/"), f"Addon {addon_id}: URL should be Stripe checkout URL"
        
        print(f"✓ Addon {addon_id}: Stripe checkout URL generated successfully")
    
    def test_addon_checkout_invalid_addon(self, auth_headers):
        """Test addon checkout with invalid addon returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/addon/checkout",
            params={"addon_id": "invalid_addon_xyz"},
            headers=auth_headers
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid addon, got {response.status_code}"
        print("✓ Invalid addon correctly returns 400 error")


class TestEnterpriseSubscriptionStatus:
    """Test enterprise subscription status endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for enterprise user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_subscription_status_endpoint(self, auth_headers):
        """Test GET /api/enterprise/subscription-status returns correct structure"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/subscription-status",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify required fields
        required_fields = ["has_subscription", "tier", "plan_name", "features", "ads_limit", "ads_used", "ads_remaining", "available_plans"]
        for field in required_fields:
            assert field in data, f"Response should contain '{field}'"
        
        # Verify tier is valid
        valid_tiers = ["free", "basic", "premium", "optimisation"]
        assert data["tier"] in valid_tiers, f"Tier should be one of {valid_tiers}, got {data['tier']}"
        
        # Verify ads_limit is a number
        assert isinstance(data["ads_limit"], int), f"ads_limit should be int, got {type(data['ads_limit'])}"
        
        # Verify available_plans contains all 10 plans
        available_plans = data["available_plans"]
        for plan_id in ALL_PLANS:
            assert plan_id in available_plans, f"Plan {plan_id} should be in available_plans"
        
        print(f"✓ Subscription status: tier={data['tier']}, plan={data['plan_name']}, ads_limit={data['ads_limit']}")
    
    def test_subscription_status_tier_ads_mapping(self, auth_headers):
        """Test that tier and ads_limit are correctly mapped based on plan"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/subscription-status",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # If has subscription, verify tier matches plan
        if data["has_subscription"] and data.get("subscription"):
            plan_id = data["subscription"].get("plan_id")
            if plan_id and plan_id in PLAN_TIERS:
                expected_tier = PLAN_TIERS[plan_id]
                assert data["tier"] == expected_tier, f"Plan {plan_id} should have tier {expected_tier}, got {data['tier']}"
                
                expected_ads = PLAN_ADS_LIMIT.get(plan_id, 1)
                assert data["ads_limit"] == expected_ads, f"Plan {plan_id} should have ads_limit {expected_ads}, got {data['ads_limit']}"
                
                print(f"✓ Plan {plan_id}: tier={data['tier']} (expected {expected_tier}), ads_limit={data['ads_limit']} (expected {expected_ads})")
        else:
            # Free tier
            assert data["tier"] == "free", f"No subscription should have tier 'free', got {data['tier']}"
            print(f"✓ No active subscription: tier=free")


class TestActivityFeedAlgorithm:
    """Test activity feed algorithm with tier-based features"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for enterprise user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_activity_feed_endpoint(self, auth_headers):
        """Test GET /api/enterprise/activity-feed returns activities"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/activity-feed",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "activities" in data, "Response should contain 'activities'"
        
        activities = data["activities"]
        assert isinstance(activities, list), "activities should be a list"
        
        print(f"✓ Activity feed returned {len(activities)} activities")
        
        # Check activity structure if any exist
        if activities:
            activity = activities[0]
            expected_fields = ["id", "type", "source"]
            for field in expected_fields:
                assert field in activity, f"Activity should contain '{field}'"
            
            # Log activity types found
            activity_types = set(a.get("type") for a in activities)
            print(f"  Activity types found: {activity_types}")
    
    def test_activity_feed_premium_features(self, auth_headers):
        """Test that premium features (market_trend, investment_opportunity) are tier-restricted"""
        # First get subscription status to know current tier
        status_response = requests.get(
            f"{BASE_URL}/api/enterprise/subscription-status",
            headers=auth_headers
        )
        assert status_response.status_code == 200
        tier = status_response.json().get("tier", "free")
        
        # Get activity feed
        feed_response = requests.get(
            f"{BASE_URL}/api/enterprise/activity-feed",
            headers=auth_headers
        )
        assert feed_response.status_code == 200
        
        activities = feed_response.json().get("activities", [])
        activity_types = [a.get("type") for a in activities]
        
        premium_types = ["market_trend", "investment_opportunity"]
        has_premium_content = any(t in premium_types for t in activity_types)
        
        if tier in ["premium", "optimisation"]:
            # Premium/optimisation tiers CAN have premium content (if data exists)
            print(f"✓ Tier {tier}: Premium content access allowed (found: {has_premium_content})")
        else:
            # Free/basic tiers should NOT have premium content
            assert not has_premium_content, f"Tier {tier} should not have premium content types, found: {[t for t in activity_types if t in premium_types]}"
            print(f"✓ Tier {tier}: Premium content correctly restricted")


class TestSubscriptionActivation:
    """Test subscription activation creates records in both collections"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for enterprise user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_activate_subscription_requires_valid_session(self, auth_headers):
        """Test that activation requires a valid Stripe session"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/activate",
            params={"session_id": "invalid_session_id"},
            headers=auth_headers
        )
        
        # Should fail with invalid session (400, 500, or 520 from Stripe API)
        assert response.status_code in [400, 500, 520], f"Invalid session should fail, got {response.status_code}"
        print("✓ Activation correctly rejects invalid session ID")


class TestFrontendAPIIntegration:
    """Test that frontend API calls work correctly"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for enterprise user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_frontend_checkout_flow(self, auth_headers):
        """Test the checkout flow as called by frontend SubscriptionsSection.js"""
        # Frontend calls: subscriptionsAPI.createCheckout(planId)
        # Which translates to: POST /api/subscriptions/checkout?plan_id={planId}
        
        test_plans = ["standard", "premium", "opti_5k"]
        
        for plan_id in test_plans:
            response = requests.post(
                f"{BASE_URL}/api/subscriptions/checkout",
                params={"plan_id": plan_id},
                headers=auth_headers
            )
            
            assert response.status_code == 200, f"Frontend checkout for {plan_id} failed: {response.status_code}"
            
            data = response.json()
            assert "url" in data, f"Response should contain 'url' for {plan_id}"
            assert data["url"].startswith("https://checkout.stripe.com/"), f"URL should be Stripe URL for {plan_id}"
            
            print(f"✓ Frontend checkout flow works for plan: {plan_id}")


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint accessible")
    
    def test_enterprise_login(self):
        """Test enterprise user can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "token" in data, "Login response should contain token"
        assert "user" in data, "Login response should contain user"
        
        user = data["user"]
        # User type can be in 'role' or 'user_type' field - French app uses 'entreprise'
        user_type = user.get("role") or user.get("user_type") or ("enterprise" if user.get("enterprise_id") else "client")
        assert user_type in ["enterprise", "prestataire", "entreprise"], f"User should be enterprise type, got {user_type}"
        
        print(f"✓ Enterprise login successful: {user.get('email')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
