"""
Test Premium Subscription Endpoints - Iteration 19
Tests for Stripe checkout session creation, subscription cancel, and confirm endpoints

Endpoints tested:
- POST /api/client/premium/checkout?plan=premium - Create checkout session for premium plan
- POST /api/client/premium/checkout?plan=vip - Create checkout session for VIP plan
- POST /api/client/premium/cancel - Cancel subscription and remove all benefits
- POST /api/client/premium/confirm?session_id=xxx - Confirm subscription after payment
- GET /api/auth/me - Verify user premium status
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Test123!"


class TestPremiumSubscription:
    """Test premium subscription checkout, cancel, and confirm endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session and authenticate"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None
        self.user_id = None
        
        # Login to get token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("token")
            self.user_id = data.get("user", {}).get("id")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip(f"Authentication failed: {login_response.status_code}")
    
    # ============ CHECKOUT TESTS ============
    
    def test_premium_checkout_creates_session(self):
        """Test POST /api/client/premium/checkout?plan=premium returns checkout_url and session_id"""
        response = self.session.post(f"{BASE_URL}/api/client/premium/checkout?plan=premium")
        
        print(f"Premium checkout response status: {response.status_code}")
        print(f"Premium checkout response: {response.text[:500] if response.text else 'empty'}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response contains checkout_url
        assert "checkout_url" in data, f"Response missing 'checkout_url': {data}"
        assert data["checkout_url"] is not None, "checkout_url should not be None"
        assert data["checkout_url"].startswith("https://checkout.stripe.com"), f"checkout_url should be Stripe URL: {data['checkout_url']}"
        
        # Verify response contains session_id
        assert "session_id" in data, f"Response missing 'session_id': {data}"
        assert data["session_id"] is not None, "session_id should not be None"
        assert data["session_id"].startswith("cs_"), f"session_id should start with 'cs_': {data['session_id']}"
        
        print(f"✓ Premium checkout successful - session_id: {data['session_id'][:20]}...")
    
    def test_vip_checkout_creates_session(self):
        """Test POST /api/client/premium/checkout?plan=vip returns checkout_url and session_id"""
        response = self.session.post(f"{BASE_URL}/api/client/premium/checkout?plan=vip")
        
        print(f"VIP checkout response status: {response.status_code}")
        print(f"VIP checkout response: {response.text[:500] if response.text else 'empty'}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response contains checkout_url
        assert "checkout_url" in data, f"Response missing 'checkout_url': {data}"
        assert data["checkout_url"] is not None, "checkout_url should not be None"
        assert data["checkout_url"].startswith("https://checkout.stripe.com"), f"checkout_url should be Stripe URL: {data['checkout_url']}"
        
        # Verify response contains session_id
        assert "session_id" in data, f"Response missing 'session_id': {data}"
        assert data["session_id"] is not None, "session_id should not be None"
        assert data["session_id"].startswith("cs_"), f"session_id should start with 'cs_': {data['session_id']}"
        
        print(f"✓ VIP checkout successful - session_id: {data['session_id'][:20]}...")
    
    def test_invalid_plan_checkout_fails(self):
        """Test POST /api/client/premium/checkout with invalid plan returns 400"""
        response = self.session.post(f"{BASE_URL}/api/client/premium/checkout?plan=invalid_plan")
        
        print(f"Invalid plan checkout response status: {response.status_code}")
        
        assert response.status_code == 400, f"Expected 400 for invalid plan, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "Error response should contain 'detail'"
        print(f"✓ Invalid plan correctly rejected: {data.get('detail')}")
    
    def test_checkout_without_auth_fails(self):
        """Test POST /api/client/premium/checkout without auth returns 401"""
        # Create new session without auth
        unauth_session = requests.Session()
        unauth_session.headers.update({"Content-Type": "application/json"})
        
        response = unauth_session.post(f"{BASE_URL}/api/client/premium/checkout?plan=premium")
        
        print(f"Unauthenticated checkout response status: {response.status_code}")
        
        assert response.status_code == 401, f"Expected 401 for unauthenticated request, got {response.status_code}"
        print("✓ Unauthenticated checkout correctly rejected")
    
    # ============ CANCEL TESTS ============
    
    def test_cancel_subscription_removes_benefits(self):
        """Test POST /api/client/premium/cancel removes all premium benefits"""
        # First, check current premium status
        me_response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        initial_user = me_response.json()
        print(f"Initial user premium status: is_premium={initial_user.get('is_premium')}, premium_plan={initial_user.get('premium_plan')}")
        
        # Try to cancel subscription
        cancel_response = self.session.post(f"{BASE_URL}/api/client/premium/cancel")
        
        print(f"Cancel subscription response status: {cancel_response.status_code}")
        print(f"Cancel subscription response: {cancel_response.text[:500] if cancel_response.text else 'empty'}")
        
        # If no active subscription, expect 404
        if cancel_response.status_code == 404:
            data = cancel_response.json()
            assert "detail" in data
            print(f"✓ No active subscription to cancel: {data.get('detail')}")
            return
        
        # If subscription exists, expect 200
        assert cancel_response.status_code == 200, f"Expected 200 or 404, got {cancel_response.status_code}: {cancel_response.text}"
        
        data = cancel_response.json()
        
        # Verify response structure
        assert "success" in data, f"Response missing 'success': {data}"
        assert data["success"] == True, f"Expected success=True: {data}"
        assert "message" in data, f"Response missing 'message': {data}"
        assert "new_plan" in data, f"Response missing 'new_plan': {data}"
        assert data["new_plan"] == "free", f"Expected new_plan='free': {data}"
        assert "new_cashback_rate" in data, f"Response missing 'new_cashback_rate': {data}"
        assert data["new_cashback_rate"] == 1, f"Expected new_cashback_rate=1: {data}"
        
        # Verify user profile updated via /api/auth/me
        me_response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        user = me_response.json()
        
        # Check premium benefits removed
        assert user.get("is_premium") == False, f"is_premium should be False after cancel: {user.get('is_premium')}"
        assert user.get("premium_plan") == "free", f"premium_plan should be 'free' after cancel: {user.get('premium_plan')}"
        
        print(f"✓ Subscription cancelled successfully - user is now on free plan")
    
    def test_cancel_without_subscription_returns_404(self):
        """Test POST /api/client/premium/cancel without active subscription returns 404"""
        # First cancel any existing subscription
        self.session.post(f"{BASE_URL}/api/client/premium/cancel")
        
        # Try to cancel again - should return 404
        response = self.session.post(f"{BASE_URL}/api/client/premium/cancel")
        
        print(f"Cancel without subscription response status: {response.status_code}")
        
        # Should return 404 since no active subscription
        assert response.status_code == 404, f"Expected 404 when no active subscription, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data
        print(f"✓ Correctly returned 404: {data.get('detail')}")
    
    # ============ CONFIRM TESTS ============
    
    def test_confirm_with_invalid_session_fails(self):
        """Test POST /api/client/premium/confirm with invalid session_id fails"""
        fake_session_id = "cs_test_invalid_session_12345"
        
        response = self.session.post(f"{BASE_URL}/api/client/premium/confirm?session_id={fake_session_id}")
        
        print(f"Confirm with invalid session response status: {response.status_code}")
        print(f"Confirm with invalid session response: {response.text[:500] if response.text else 'empty'}")
        
        # Should fail with 400, 404, or 500 (Stripe will reject invalid session)
        assert response.status_code in [400, 404, 500], f"Expected error status for invalid session, got {response.status_code}"
        print(f"✓ Invalid session correctly rejected with status {response.status_code}")
    
    def test_confirm_without_auth_fails(self):
        """Test POST /api/client/premium/confirm without auth returns 401"""
        unauth_session = requests.Session()
        unauth_session.headers.update({"Content-Type": "application/json"})
        
        response = unauth_session.post(f"{BASE_URL}/api/client/premium/confirm?session_id=cs_test_123")
        
        print(f"Unauthenticated confirm response status: {response.status_code}")
        
        assert response.status_code == 401, f"Expected 401 for unauthenticated request, got {response.status_code}"
        print("✓ Unauthenticated confirm correctly rejected")
    
    # ============ PREMIUM STATUS TESTS ============
    
    def test_get_premium_status(self):
        """Test GET /api/client/premium returns correct status"""
        response = self.session.get(f"{BASE_URL}/api/client/premium")
        
        print(f"Get premium status response status: {response.status_code}")
        print(f"Get premium status response: {response.text[:500] if response.text else 'empty'}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "current_plan" in data, f"Response missing 'current_plan': {data}"
        assert "is_premium" in data, f"Response missing 'is_premium': {data}"
        assert "benefits" in data, f"Response missing 'benefits': {data}"
        assert "cashback_rate" in data, f"Response missing 'cashback_rate': {data}"
        
        # Verify benefits contains all plans
        benefits = data["benefits"]
        assert "free" in benefits, "Benefits should contain 'free' plan"
        assert "premium" in benefits, "Benefits should contain 'premium' plan"
        assert "vip" in benefits, "Benefits should contain 'vip' plan"
        
        print(f"✓ Premium status retrieved - current_plan: {data['current_plan']}, is_premium: {data['is_premium']}, cashback_rate: {data['cashback_rate']}%")
    
    def test_auth_me_returns_premium_fields(self):
        """Test GET /api/auth/me returns premium-related fields"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        
        print(f"Auth me response status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify user has premium-related fields
        assert "is_premium" in data, f"User response missing 'is_premium': {data.keys()}"
        
        print(f"✓ Auth me returns premium fields - is_premium: {data.get('is_premium')}, premium_plan: {data.get('premium_plan', 'N/A')}")


class TestPremiumCheckoutIntegration:
    """Integration tests for premium checkout flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session and authenticate"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("Authentication failed")
    
    def test_full_checkout_flow_premium(self):
        """Test complete checkout flow for premium plan"""
        # Step 1: Create checkout session
        checkout_response = self.session.post(f"{BASE_URL}/api/client/premium/checkout?plan=premium")
        
        assert checkout_response.status_code == 200, f"Checkout failed: {checkout_response.text}"
        
        checkout_data = checkout_response.json()
        
        # Verify checkout URL is valid Stripe URL
        checkout_url = checkout_data.get("checkout_url")
        session_id = checkout_data.get("session_id")
        
        assert checkout_url is not None, "checkout_url is None"
        assert session_id is not None, "session_id is None"
        assert "checkout.stripe.com" in checkout_url, f"Invalid checkout URL: {checkout_url}"
        
        print(f"✓ Premium checkout session created successfully")
        print(f"  - Session ID: {session_id[:30]}...")
        print(f"  - Checkout URL: {checkout_url[:60]}...")
    
    def test_full_checkout_flow_vip(self):
        """Test complete checkout flow for VIP plan"""
        # Step 1: Create checkout session
        checkout_response = self.session.post(f"{BASE_URL}/api/client/premium/checkout?plan=vip")
        
        assert checkout_response.status_code == 200, f"Checkout failed: {checkout_response.text}"
        
        checkout_data = checkout_response.json()
        
        # Verify checkout URL is valid Stripe URL
        checkout_url = checkout_data.get("checkout_url")
        session_id = checkout_data.get("session_id")
        
        assert checkout_url is not None, "checkout_url is None"
        assert session_id is not None, "session_id is None"
        assert "checkout.stripe.com" in checkout_url, f"Invalid checkout URL: {checkout_url}"
        
        print(f"✓ VIP checkout session created successfully")
        print(f"  - Session ID: {session_id[:30]}...")
        print(f"  - Checkout URL: {checkout_url[:60]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
