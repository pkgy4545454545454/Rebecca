"""
Test suite for Titelli Marketplace - New Features Testing
Tests: Subscriptions, IA/Marketing sections, Multi-step registration, Enterprise profile
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


class TestSubscriptionsAPI:
    """Test subscription plans and add-ons API"""
    
    def test_get_subscription_plans(self):
        """Test /api/subscriptions/plans returns all plans and addons"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        assert "plans" in data
        assert "addons" in data
        assert "base_features" in data
        
        # Verify 10 subscription plans exist
        plans = data["plans"]
        assert len(plans) == 10, f"Expected 10 plans, got {len(plans)}"
        
        # Verify plan tiers
        basic_plans = [p for p in plans.values() if p.get("tier") == "basic"]
        premium_plans = [p for p in plans.values() if p.get("tier") == "premium"]
        optimisation_plans = [p for p in plans.values() if p.get("tier") == "optimisation"]
        
        assert len(basic_plans) == 2, "Should have 2 basic plans (Standard, Guest)"
        assert len(premium_plans) == 2, "Should have 2 premium plans"
        assert len(optimisation_plans) == 6, "Should have 6 optimisation plans"
        
        # Verify specific plans exist
        assert "standard" in plans
        assert "guest" in plans
        assert "premium" in plans
        assert "premium_mvp" in plans
        
        # Verify plan prices
        assert plans["standard"]["price"] == 200.0
        assert plans["guest"]["price"] == 250.0
        assert plans["premium"]["price"] == 500.0
        assert plans["premium_mvp"]["price"] == 1000.0
        
        print("✓ Subscription plans API returns 10 plans with correct tiers and prices")
    
    def test_get_addons(self):
        """Test add-ons are returned correctly"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        addons = data["addons"]
        
        # Verify 14 add-ons exist
        assert len(addons) == 14, f"Expected 14 addons, got {len(addons)}"
        
        # Verify specific add-ons
        assert "pub_extra" in addons
        assert "expert_label" in addons
        assert "fiscaliste" in addons
        
        # Verify addon types
        assert addons["pub_extra"]["type"] == "monthly"
        assert addons["expert_label"]["type"] == "one_time"
        
        print("✓ Add-ons API returns 14 options with correct types")
    
    def test_base_features(self):
        """Test base features included in all plans"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        base_features = data["base_features"]
        
        assert len(base_features) >= 10, "Should have at least 10 base features"
        assert "Fiches exigences clients" in base_features
        assert "Agenda interne" in base_features
        
        print("✓ Base features returned correctly")


class TestAuthenticationAPI:
    """Test authentication endpoints"""
    
    def test_enterprise_login(self):
        """Test enterprise user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "entreprise"
        assert data["user"]["email"] == ENTERPRISE_EMAIL
        
        print(f"✓ Enterprise login successful: {data['user']['first_name']} {data['user']['last_name']}")
        return data["token"]
    
    def test_client_login(self):
        """Test client user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "client"
        
        print(f"✓ Client login successful: {data['user']['first_name']} {data['user']['last_name']}")
        return data["token"]
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@email.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")


class TestEnterpriseAPI:
    """Test enterprise-related endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get enterprise auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_enterprises(self):
        """Test listing enterprises"""
        response = requests.get(f"{BASE_URL}/api/enterprises")
        assert response.status_code == 200
        
        data = response.json()
        assert "enterprises" in data
        assert "total" in data
        
        print(f"✓ Enterprises list: {data['total']} enterprises found")
    
    def test_get_current_subscription(self, auth_token):
        """Test getting current subscription for authenticated user"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/subscriptions/current", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # May or may not have active subscription
        print(f"✓ Current subscription check: {'Active' if data.get('is_active') else 'No active subscription'}")


class TestAdvertisingAPI:
    """Test advertising endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get enterprise auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_list_advertising(self, auth_token):
        """Test listing advertising campaigns"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/enterprise/advertising", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "campaigns" in data
        assert "stats" in data
        
        print(f"✓ Advertising list: {len(data['campaigns'])} campaigns found")
    
    def test_create_advertising(self, auth_token):
        """Test creating an advertising campaign"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        ad_data = {
            "title": "TEST_Promo Été 2026",
            "description": "Découvrez nos offres spéciales été",
            "ad_type": "banner",
            "placement": "homepage",
            "budget": 100.0,
            "target_audience": "all",
            "start_date": "2026-01-22",
            "end_date": "2026-01-29"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/advertising", json=ad_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["title"] == ad_data["title"]
        
        print(f"✓ Advertising campaign created: {data['id']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/enterprise/advertising/{data['id']}", headers=headers)


class TestCategoriesAPI:
    """Test category endpoints"""
    
    def test_get_service_categories(self):
        """Test getting service categories"""
        response = requests.get(f"{BASE_URL}/api/categories/services")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        # Verify category structure
        first_cat = data[0]
        assert "id" in first_cat
        assert "name" in first_cat
        
        print(f"✓ Service categories: {len(data)} categories found")
    
    def test_get_product_categories(self):
        """Test getting product categories"""
        response = requests.get(f"{BASE_URL}/api/categories/products")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        print(f"✓ Product categories: {len(data)} categories found")


class TestFeaturedAPI:
    """Test featured content endpoints"""
    
    def test_get_tendances(self):
        """Test getting trending enterprises"""
        response = requests.get(f"{BASE_URL}/api/featured/tendances")
        assert response.status_code == 200
        print("✓ Tendances endpoint working")
    
    def test_get_guests(self):
        """Test getting guest enterprises"""
        response = requests.get(f"{BASE_URL}/api/featured/guests")
        assert response.status_code == 200
        print("✓ Guests endpoint working")
    
    def test_get_offres(self):
        """Test getting offers"""
        response = requests.get(f"{BASE_URL}/api/featured/offres")
        assert response.status_code == 200
        print("✓ Offres endpoint working")
    
    def test_get_premium(self):
        """Test getting premium enterprises"""
        response = requests.get(f"{BASE_URL}/api/featured/premium")
        assert response.status_code == 200
        print("✓ Premium endpoint working")


class TestServicesProductsAPI:
    """Test services and products endpoints"""
    
    def test_list_services_products(self):
        """Test listing services and products"""
        response = requests.get(f"{BASE_URL}/api/services-products")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        
        print(f"✓ Services/Products: {data['total']} items found")
    
    def test_filter_by_type(self):
        """Test filtering by type"""
        response = requests.get(f"{BASE_URL}/api/services-products", params={"type": "service"})
        assert response.status_code == 200
        
        data = response.json()
        for item in data["items"]:
            assert item["type"] == "service"
        
        print(f"✓ Service filter working: {len(data['items'])} services")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
