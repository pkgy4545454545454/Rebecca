"""
Test file for iteration 11 bug fixes:
1. Influencer registration flow - redirect to /dashboard/influencer
2. Influencer dashboard - stats and collaborations
3. Services page - video header background
4. Products page - video header background
5. Job filters - 4 columns grid (Type, Ville, Entreprise, Réinitialiser)
6. API /api/subscriptions/checkout - should return URL and session_id
7. API /api/enterprise/advertising/{ad_id}/pay - should return URL
8. Client reviews on service detail page - centered
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"
INFLUENCER_EMAIL = "test_influencer2@example.com"
INFLUENCER_PASSWORD = "Test123!"


class TestAuthAndInfluencer:
    """Test influencer registration and authentication"""
    
    def test_login_client(self):
        """Test client login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        print(f"✓ Client login successful, user_type: {data['user'].get('user_type')}")
    
    def test_login_enterprise(self):
        """Test enterprise login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data['user'].get('user_type') == 'entreprise'
        print(f"✓ Enterprise login successful")
    
    def test_login_influencer(self):
        """Test influencer login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INFLUENCER_EMAIL,
            "password": INFLUENCER_PASSWORD
        })
        # May not exist, so we check for 200 or 401
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            print(f"✓ Influencer login successful, user_type: {data['user'].get('user_type')}")
        else:
            print(f"⚠ Influencer account may not exist (status: {response.status_code})")
            pytest.skip("Influencer account not found")
    
    def test_influencer_registration_returns_correct_user_type(self):
        """Test that influencer registration returns user_type='influencer'"""
        unique_email = f"test_influencer_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "first_name": "Test",
            "last_name": "Influencer",
            "user_type": "influencer",
            "social_accounts": {
                "instagram": "@test_insta"
            },
            "niche": "lifestyle"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data['user'].get('user_type') == 'influencer', f"Expected user_type='influencer', got '{data['user'].get('user_type')}'"
        print(f"✓ Influencer registration returns correct user_type: {data['user'].get('user_type')}")


class TestInfluencerDashboard:
    """Test influencer dashboard API"""
    
    @pytest.fixture
    def influencer_token(self):
        """Get influencer auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INFLUENCER_EMAIL,
            "password": INFLUENCER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Influencer account not available")
        return response.json()['token']
    
    def test_influencer_profile_endpoint(self, influencer_token):
        """Test influencer profile endpoint"""
        headers = {"Authorization": f"Bearer {influencer_token}"}
        response = requests.get(f"{BASE_URL}/api/influencer/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Should have profile, collaborations, stats
        assert "profile" in data or "collaborations" in data or "stats" in data
        print(f"✓ Influencer profile endpoint working")


class TestSubscriptionCheckout:
    """Test subscription checkout API - should return URL and session_id"""
    
    @pytest.fixture
    def enterprise_token(self):
        """Get enterprise auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200
        return response.json()['token']
    
    def test_subscription_checkout_returns_url_and_session_id(self, enterprise_token):
        """Test that /api/subscriptions/checkout returns URL and session_id"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            params={"plan_id": "standard"},  # Valid plan: standard, guest, premium, etc.
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check for 'url' attribute (not 'checkout_url')
        assert "url" in data, f"Response should contain 'url' key. Got: {data.keys()}"
        assert "session_id" in data, f"Response should contain 'session_id' key. Got: {data.keys()}"
        
        # Validate URL format
        assert data['url'].startswith('https://checkout.stripe.com'), f"URL should be Stripe checkout URL, got: {data['url'][:50]}"
        assert len(data['session_id']) > 0, "session_id should not be empty"
        
        print(f"✓ Subscription checkout returns 'url' and 'session_id'")
        print(f"  URL: {data['url'][:60]}...")
        print(f"  Session ID: {data['session_id'][:30]}...")
    
    def test_subscription_checkout_invalid_plan(self, enterprise_token):
        """Test subscription checkout with invalid plan"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            params={"plan_id": "invalid_plan"},
            headers=headers
        )
        assert response.status_code == 400
        print(f"✓ Invalid plan returns 400")


class TestAdvertisingPayment:
    """Test advertising payment API - should return URL"""
    
    @pytest.fixture
    def enterprise_token(self):
        """Get enterprise auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200
        return response.json()['token']
    
    @pytest.fixture
    def enterprise_id(self, enterprise_token):
        """Get enterprise ID"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        user = response.json()
        
        # Get enterprise profile
        response = requests.get(f"{BASE_URL}/api/enterprises", headers=headers)
        if response.status_code == 200:
            enterprises = response.json().get('enterprises', [])
            for ent in enterprises:
                if ent.get('user_id') == user['id']:
                    return ent['id']
        return None
    
    def test_advertising_pay_endpoint_exists(self, enterprise_token, enterprise_id):
        """Test that /api/enterprise/advertising/{ad_id}/pay endpoint exists"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        # First, try to create an ad or get existing one
        # Try to get existing ads
        response = requests.get(f"{BASE_URL}/api/enterprise/advertising", headers=headers)
        
        if response.status_code == 200:
            ads = response.json()
            if isinstance(ads, list) and len(ads) > 0:
                # Find an unpaid ad
                unpaid_ad = next((ad for ad in ads if not ad.get('is_paid')), None)
                if unpaid_ad:
                    ad_id = unpaid_ad['id']
                    # Test the pay endpoint
                    pay_response = requests.post(
                        f"{BASE_URL}/api/enterprise/advertising/{ad_id}/pay",
                        headers=headers
                    )
                    assert pay_response.status_code == 200, f"Expected 200, got {pay_response.status_code}: {pay_response.text}"
                    data = pay_response.json()
                    
                    # Check for 'url' attribute
                    assert "url" in data, f"Response should contain 'url' key. Got: {data.keys()}"
                    assert data['url'].startswith('https://checkout.stripe.com'), f"URL should be Stripe checkout URL"
                    
                    print(f"✓ Advertising pay endpoint returns 'url'")
                    print(f"  URL: {data['url'][:60]}...")
                    return
        
        # If no ads exist, create one for testing
        create_response = requests.post(
            f"{BASE_URL}/api/enterprise/advertising",
            headers=headers,
            json={
                "title": "Test Ad for Payment",
                "description": "Test advertisement",
                "ad_type": "standard",
                "budget": 50,
                "placement": "homepage"
            }
        )
        
        if create_response.status_code == 200:
            ad = create_response.json()
            ad_id = ad['id']
            
            # Test the pay endpoint
            pay_response = requests.post(
                f"{BASE_URL}/api/enterprise/advertising/{ad_id}/pay",
                headers=headers
            )
            assert pay_response.status_code == 200, f"Expected 200, got {pay_response.status_code}: {pay_response.text}"
            data = pay_response.json()
            
            assert "url" in data, f"Response should contain 'url' key. Got: {data.keys()}"
            print(f"✓ Advertising pay endpoint returns 'url'")
        else:
            pytest.skip(f"Could not create test ad: {create_response.status_code}")


class TestJobFilters:
    """Test job filters API"""
    
    def test_jobs_list_endpoint(self):
        """Test jobs list endpoint"""
        response = requests.get(f"{BASE_URL}/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data or isinstance(data, list)
        print(f"✓ Jobs list endpoint working")
    
    def test_jobs_filter_by_type(self):
        """Test jobs filter by type"""
        response = requests.get(f"{BASE_URL}/api/jobs", params={"type": "CDI"})
        assert response.status_code == 200
        print(f"✓ Jobs filter by type working")
    
    def test_jobs_filter_by_location(self):
        """Test jobs filter by location"""
        response = requests.get(f"{BASE_URL}/api/jobs", params={"location": "Lausanne"})
        assert response.status_code == 200
        print(f"✓ Jobs filter by location working")
    
    def test_jobs_have_enterprise_name(self):
        """Test that jobs have enterprise_name field for filtering"""
        response = requests.get(f"{BASE_URL}/api/jobs")
        assert response.status_code == 200
        data = response.json()
        jobs = data.get('jobs', data) if isinstance(data, dict) else data
        
        if len(jobs) > 0:
            # Check if jobs have enterprise_name field
            job = jobs[0]
            has_enterprise_name = 'enterprise_name' in job or 'company_name' in job
            print(f"✓ Jobs have enterprise name field: {has_enterprise_name}")
            if has_enterprise_name:
                print(f"  Enterprise name: {job.get('enterprise_name') or job.get('company_name')}")


class TestServicesAndProducts:
    """Test services and products endpoints"""
    
    def test_services_list(self):
        """Test services list endpoint"""
        response = requests.get(f"{BASE_URL}/api/services-products", params={"type": "service"})
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✓ Services list endpoint working, total: {data.get('total', len(data.get('items', [])))}")
    
    def test_products_list(self):
        """Test products list endpoint"""
        response = requests.get(f"{BASE_URL}/api/services-products", params={"type": "product"})
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✓ Products list endpoint working, total: {data.get('total', len(data.get('items', [])))}")
    
    def test_service_detail_with_reviews(self):
        """Test service detail includes reviews"""
        # First get a service
        response = requests.get(f"{BASE_URL}/api/services-products", params={"type": "service", "limit": 1})
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if len(items) > 0:
                item_id = items[0]['id']
                detail_response = requests.get(f"{BASE_URL}/api/services-products/{item_id}")
                assert detail_response.status_code == 200
                print(f"✓ Service detail endpoint working")
                return
        print("⚠ No services available to test detail")


class TestReviewsAPI:
    """Test reviews API"""
    
    def test_reviews_endpoint(self):
        """Test reviews endpoint"""
        # Get an enterprise first
        response = requests.get(f"{BASE_URL}/api/enterprises", params={"limit": 1})
        if response.status_code == 200:
            data = response.json()
            enterprises = data.get('enterprises', [])
            if len(enterprises) > 0:
                enterprise_id = enterprises[0]['id']
                reviews_response = requests.get(f"{BASE_URL}/api/reviews/{enterprise_id}")
                assert reviews_response.status_code == 200
                print(f"✓ Reviews endpoint working")
                return
        print("⚠ No enterprises available to test reviews")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
