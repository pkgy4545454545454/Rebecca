"""
Test suite for Iteration 19 - Client Dashboard New Sections
Testing: Activity Feed, My Feed, Mode de vie, Invitations, Current Offers, Guests, Investments, Premium

Test credentials: test@example.com / Test123!
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestClientDashboardNewSections:
    """Test all 8 new client dashboard sections"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and authenticate"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as client
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.user = login_response.json().get("user")
        else:
            pytest.skip("Authentication failed - skipping tests")
    
    # ============ ACTIVITY FEED TESTS ============
    
    def test_activity_feed_endpoint_returns_200(self):
        """Test GET /api/client/activity-feed returns 200"""
        response = self.session.get(f"{BASE_URL}/api/client/activity-feed")
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        assert isinstance(data["activities"], list)
    
    def test_activity_feed_with_limit_parameter(self):
        """Test activity feed respects limit parameter"""
        response = self.session.get(f"{BASE_URL}/api/client/activity-feed?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["activities"]) <= 5
    
    def test_activity_feed_structure(self):
        """Test activity feed returns proper structure"""
        response = self.session.get(f"{BASE_URL}/api/client/activity-feed")
        assert response.status_code == 200
        data = response.json()
        # If there are activities, check structure
        if data["activities"]:
            activity = data["activities"][0]
            assert "type" in activity
            assert activity["type"] in ["review", "purchase", "training", "wishlist"]
    
    # ============ MY FEED TESTS ============
    
    def test_my_feed_endpoint_returns_200(self):
        """Test GET /api/client/my-feed returns 200"""
        response = self.session.get(f"{BASE_URL}/api/client/my-feed")
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        assert isinstance(data["activities"], list)
    
    def test_my_feed_with_limit_parameter(self):
        """Test my feed respects limit parameter"""
        response = self.session.get(f"{BASE_URL}/api/client/my-feed?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["activities"]) <= 10
    
    def test_my_feed_activity_structure(self):
        """Test my feed returns proper activity structure"""
        response = self.session.get(f"{BASE_URL}/api/client/my-feed")
        assert response.status_code == 200
        data = response.json()
        if data["activities"]:
            activity = data["activities"][0]
            assert "type" in activity
            assert "action" in activity
            assert "target" in activity
    
    # ============ LIFESTYLE (MODE DE VIE) TESTS ============
    
    def test_lifestyle_endpoint_returns_200(self):
        """Test GET /api/client/lifestyle returns 200"""
        response = self.session.get(f"{BASE_URL}/api/client/lifestyle")
        assert response.status_code == 200
        data = response.json()
        assert "wishlist" in data
        assert "personal_providers" in data
        assert "liked_items" in data
        assert "preferences" in data
    
    def test_lifestyle_preferences_structure(self):
        """Test lifestyle preferences has proper structure"""
        response = self.session.get(f"{BASE_URL}/api/client/lifestyle")
        assert response.status_code == 200
        data = response.json()
        prefs = data["preferences"]
        assert "top_categories" in prefs
        assert "top_enterprises" in prefs
        assert "total_orders" in prefs
        assert "total_trainings" in prefs
    
    def test_lifestyle_wishlist_is_list(self):
        """Test lifestyle wishlist is a list"""
        response = self.session.get(f"{BASE_URL}/api/client/lifestyle")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["wishlist"], list)
        assert isinstance(data["personal_providers"], list)
        assert isinstance(data["liked_items"], list)
    
    # ============ INVITATIONS TESTS ============
    
    def test_invitations_endpoint_returns_200(self):
        """Test GET /api/client/invitations returns 200"""
        response = self.session.get(f"{BASE_URL}/api/client/invitations")
        assert response.status_code == 200
        data = response.json()
        assert "invitations" in data
        assert isinstance(data["invitations"], list)
    
    def test_invitations_structure(self):
        """Test invitations have proper structure"""
        response = self.session.get(f"{BASE_URL}/api/client/invitations")
        assert response.status_code == 200
        data = response.json()
        # If there are invitations, check structure
        if data["invitations"]:
            inv = data["invitations"][0]
            assert "id" in inv
            assert "title" in inv or "enterprise_id" in inv
    
    # ============ CURRENT OFFERS TESTS ============
    
    def test_current_offers_endpoint_returns_200(self):
        """Test GET /api/client/current-offers returns 200"""
        response = self.session.get(f"{BASE_URL}/api/client/current-offers")
        assert response.status_code == 200
        data = response.json()
        assert "offers" in data
        assert isinstance(data["offers"], list)
    
    def test_current_offers_structure(self):
        """Test current offers have proper structure"""
        response = self.session.get(f"{BASE_URL}/api/client/current-offers")
        assert response.status_code == 200
        data = response.json()
        if data["offers"]:
            offer = data["offers"][0]
            assert "id" in offer
            assert "title" in offer or "enterprise_id" in offer
    
    # ============ GUESTS TESTS ============
    
    def test_guests_endpoint_returns_200(self):
        """Test GET /api/client/guests returns 200"""
        response = self.session.get(f"{BASE_URL}/api/client/guests")
        assert response.status_code == 200
        data = response.json()
        assert "guests" in data
        assert isinstance(data["guests"], list)
    
    def test_add_guest_to_favorites(self):
        """Test POST /api/client/guests - add guest to favorites"""
        guest_data = {
            "guest_user_id": f"TEST_guest_{datetime.now().timestamp()}",
            "guest_name": "TEST Guest User",
            "guest_avatar": None,
            "notes": "Test guest for iteration 19"
        }
        response = self.session.post(f"{BASE_URL}/api/client/guests", json=guest_data)
        assert response.status_code in [200, 201, 400]  # 400 if already exists
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "id" in data
            assert data["guest_name"] == "TEST Guest User"
            # Cleanup
            self.session.delete(f"{BASE_URL}/api/client/guests/{data['id']}")
    
    def test_remove_guest_from_favorites(self):
        """Test DELETE /api/client/guests/{guest_id}"""
        # First add a guest
        guest_data = {
            "guest_user_id": f"TEST_delete_guest_{datetime.now().timestamp()}",
            "guest_name": "TEST Delete Guest",
            "notes": "To be deleted"
        }
        add_response = self.session.post(f"{BASE_URL}/api/client/guests", json=guest_data)
        
        if add_response.status_code in [200, 201]:
            guest_id = add_response.json()["id"]
            # Now delete
            delete_response = self.session.delete(f"{BASE_URL}/api/client/guests/{guest_id}")
            assert delete_response.status_code in [200, 204]
    
    # ============ INVESTMENTS TESTS ============
    
    def test_investments_endpoint_returns_200(self):
        """Test GET /api/client/investments returns 200"""
        response = self.session.get(f"{BASE_URL}/api/client/investments")
        assert response.status_code == 200
        data = response.json()
        assert "investments" in data
        assert "statistics" in data
    
    def test_investments_statistics_structure(self):
        """Test investments statistics have proper structure"""
        response = self.session.get(f"{BASE_URL}/api/client/investments")
        assert response.status_code == 200
        data = response.json()
        stats = data["statistics"]
        assert "total_invested" in stats
        assert "total_current_value" in stats
        assert "total_roi" in stats
        assert "avg_roi_percent" in stats
        assert "investment_count" in stats
    
    def test_create_investment(self):
        """Test POST /api/client/investments - create investment"""
        investment_data = {
            "investment_type": "real_estate",
            "title": "TEST Appartement Lausanne",
            "description": "Test investment for iteration 19",
            "amount_invested": 50000.0,
            "current_value": 55000.0,
            "roi_percent": 10.0,
            "investment_date": "2024-01-15",
            "property_address": "Rue de Test 123, Lausanne",
            "status": "active"
        }
        response = self.session.post(f"{BASE_URL}/api/client/investments", json=investment_data)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["title"] == "TEST Appartement Lausanne"
        assert data["investment_type"] == "real_estate"
        assert data["amount_invested"] == 50000.0
        
        # Store for cleanup
        self.test_investment_id = data["id"]
    
    def test_create_business_investment(self):
        """Test creating a business type investment"""
        investment_data = {
            "investment_type": "business",
            "title": "TEST Business Investment",
            "description": "Test business investment",
            "amount_invested": 25000.0,
            "current_value": 27500.0,
            "roi_percent": 10.0,
            "investment_date": "2024-06-01",
            "status": "active"
        }
        response = self.session.post(f"{BASE_URL}/api/client/investments", json=investment_data)
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["investment_type"] == "business"
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/client/investments/{data['id']}")
    
    def test_delete_investment(self):
        """Test DELETE /api/client/investments/{investment_id}"""
        # First create an investment
        investment_data = {
            "investment_type": "other",
            "title": "TEST Delete Investment",
            "description": "To be deleted",
            "amount_invested": 1000.0,
            "investment_date": "2024-01-01",
            "status": "pending"
        }
        create_response = self.session.post(f"{BASE_URL}/api/client/investments", json=investment_data)
        
        if create_response.status_code in [200, 201]:
            investment_id = create_response.json()["id"]
            # Now delete
            delete_response = self.session.delete(f"{BASE_URL}/api/client/investments/{investment_id}")
            assert delete_response.status_code in [200, 204]
            
            # Verify deletion
            get_response = self.session.get(f"{BASE_URL}/api/client/investments")
            investments = get_response.json()["investments"]
            assert not any(inv["id"] == investment_id for inv in investments)
    
    # ============ PREMIUM TESTS ============
    
    def test_premium_status_endpoint_returns_200(self):
        """Test GET /api/client/premium returns 200"""
        response = self.session.get(f"{BASE_URL}/api/client/premium")
        assert response.status_code == 200
        data = response.json()
        assert "current_plan" in data
        assert "is_premium" in data
        assert "benefits" in data
    
    def test_premium_benefits_structure(self):
        """Test premium benefits have all plans"""
        response = self.session.get(f"{BASE_URL}/api/client/premium")
        assert response.status_code == 200
        data = response.json()
        benefits = data["benefits"]
        assert "free" in benefits
        assert "premium" in benefits
        assert "vip" in benefits
    
    def test_premium_plan_features(self):
        """Test each premium plan has features"""
        response = self.session.get(f"{BASE_URL}/api/client/premium")
        assert response.status_code == 200
        data = response.json()
        
        for plan in ["free", "premium", "vip"]:
            assert "features" in data["benefits"][plan]
            assert isinstance(data["benefits"][plan]["features"], list)
            assert len(data["benefits"][plan]["features"]) > 0
    
    def test_premium_cashback_rates(self):
        """Test premium cashback rates are correct"""
        response = self.session.get(f"{BASE_URL}/api/client/premium")
        assert response.status_code == 200
        data = response.json()
        
        # Cashback rate should be 1, 10, or 15 based on plan
        assert data["cashback_rate"] in [1, 10, 15]
    
    def test_upgrade_to_premium(self):
        """Test POST /api/client/premium/upgrade - upgrade to premium"""
        response = self.session.post(f"{BASE_URL}/api/client/premium/upgrade?plan=premium")
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["plan"] == "premium"
        assert data["status"] == "active"
    
    def test_upgrade_to_vip(self):
        """Test POST /api/client/premium/upgrade - upgrade to VIP"""
        response = self.session.post(f"{BASE_URL}/api/client/premium/upgrade?plan=vip")
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["plan"] == "vip"
        assert data["price"] == 29.99
    
    def test_upgrade_invalid_plan_fails(self):
        """Test upgrade with invalid plan returns error"""
        response = self.session.post(f"{BASE_URL}/api/client/premium/upgrade?plan=invalid")
        assert response.status_code == 400
    
    # ============ CLEANUP ============
    
    def test_cleanup_test_investments(self):
        """Cleanup any TEST_ prefixed investments"""
        response = self.session.get(f"{BASE_URL}/api/client/investments")
        if response.status_code == 200:
            investments = response.json()["investments"]
            for inv in investments:
                if inv.get("title", "").startswith("TEST"):
                    self.session.delete(f"{BASE_URL}/api/client/investments/{inv['id']}")


class TestClientDashboardIntegration:
    """Integration tests for client dashboard sections"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and authenticate"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Authentication failed")
    
    def test_all_endpoints_accessible(self):
        """Test all 8 new endpoints are accessible"""
        endpoints = [
            "/api/client/activity-feed",
            "/api/client/my-feed",
            "/api/client/lifestyle",
            "/api/client/invitations",
            "/api/client/current-offers",
            "/api/client/guests",
            "/api/client/investments",
            "/api/client/premium"
        ]
        
        for endpoint in endpoints:
            response = self.session.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Endpoint {endpoint} failed with status {response.status_code}"
    
    def test_investment_crud_flow(self):
        """Test complete CRUD flow for investments"""
        # CREATE
        investment_data = {
            "investment_type": "real_estate",
            "title": "TEST CRUD Investment",
            "description": "Testing CRUD flow",
            "amount_invested": 100000.0,
            "current_value": 110000.0,
            "roi_percent": 10.0,
            "investment_date": "2024-01-01",
            "property_address": "Test Address",
            "status": "active"
        }
        create_response = self.session.post(f"{BASE_URL}/api/client/investments", json=investment_data)
        assert create_response.status_code in [200, 201]
        investment_id = create_response.json()["id"]
        
        # READ
        read_response = self.session.get(f"{BASE_URL}/api/client/investments")
        assert read_response.status_code == 200
        investments = read_response.json()["investments"]
        assert any(inv["id"] == investment_id for inv in investments)
        
        # DELETE
        delete_response = self.session.delete(f"{BASE_URL}/api/client/investments/{investment_id}")
        assert delete_response.status_code in [200, 204]
        
        # VERIFY DELETION
        verify_response = self.session.get(f"{BASE_URL}/api/client/investments")
        investments = verify_response.json()["investments"]
        assert not any(inv["id"] == investment_id for inv in investments)
    
    def test_premium_upgrade_updates_status(self):
        """Test premium upgrade updates user status"""
        # Get initial status
        initial_response = self.session.get(f"{BASE_URL}/api/client/premium")
        initial_plan = initial_response.json()["current_plan"]
        
        # Upgrade to premium
        upgrade_response = self.session.post(f"{BASE_URL}/api/client/premium/upgrade?plan=premium")
        assert upgrade_response.status_code in [200, 201]
        
        # Verify status changed
        final_response = self.session.get(f"{BASE_URL}/api/client/premium")
        assert final_response.json()["current_plan"] == "premium"
        assert final_response.json()["is_premium"] == True


class TestUnauthorizedAccess:
    """Test unauthorized access to protected endpoints"""
    
    def test_activity_feed_requires_auth(self):
        """Test activity feed requires authentication"""
        response = requests.get(f"{BASE_URL}/api/client/activity-feed")
        assert response.status_code == 401
    
    def test_investments_requires_auth(self):
        """Test investments requires authentication"""
        response = requests.get(f"{BASE_URL}/api/client/investments")
        assert response.status_code == 401
    
    def test_premium_requires_auth(self):
        """Test premium status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/client/premium")
        assert response.status_code == 401
