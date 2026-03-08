"""
Iteration 24 - Global Audit Test Suite
Tests all major features of Titelli marketplace:
- Stripe payment system (subscriptions, client premium, training purchase, advertising)
- Enterprise content creation (services/products, trainings, jobs)
- Client activity feed with friends algorithm
- Enterprise activity feed with tier-based algorithm
- Client lifestyle (wishlist, personal providers)
- Cashback system with subscription-based rates
- Enterprise subscription status with available plans
- Enterprise suggestions based on tier
- Enterprise favorites
- Wishlist activity generation
"""

import pytest
import requests
import os
import time
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"

class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ API health check passed")

class TestAuthentication:
    """Authentication tests"""
    
    def test_client_login(self):
        """Test client login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "client"
        print(f"✅ Client login successful: {data['user']['email']}")
        return data["token"]
    
    def test_enterprise_login(self):
        """Test enterprise login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "entreprise"
        print(f"✅ Enterprise login successful: {data['user']['email']}")
        return data["token"]


class TestStripePayments:
    """Stripe payment system tests"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_enterprise_subscription_checkout_premium(self, enterprise_token):
        """Test enterprise subscription checkout for premium plan"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout?plan_id=premium",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "checkout.stripe.com" in data["url"]
        print(f"✅ Enterprise premium subscription checkout URL: {data['url'][:80]}...")
    
    def test_enterprise_subscription_checkout_standard(self, enterprise_token):
        """Test enterprise subscription checkout for standard plan"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout?plan_id=standard",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "checkout.stripe.com" in data["url"]
        print(f"✅ Enterprise standard subscription checkout URL generated")
    
    def test_enterprise_subscription_checkout_guest(self, enterprise_token):
        """Test enterprise subscription checkout for guest plan"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout?plan_id=guest",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "checkout.stripe.com" in data["url"]
        print(f"✅ Enterprise guest subscription checkout URL generated")
    
    def test_enterprise_subscription_checkout_invalid_plan(self, enterprise_token):
        """Test enterprise subscription checkout with invalid plan"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout?plan_id=invalid_plan",
            headers=headers
        )
        assert response.status_code == 400
        print("✅ Invalid plan correctly rejected with 400")
    
    def test_client_premium_checkout(self, client_token):
        """Test client premium subscription checkout"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(
            f"{BASE_URL}/api/payments/checkout?package_type=premium",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "checkout.stripe.com" in data["url"]
        print(f"✅ Client premium checkout URL: {data['url'][:80]}...")
    
    def test_client_vip_checkout(self, client_token):
        """Test client VIP subscription checkout"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(
            f"{BASE_URL}/api/payments/checkout?package_type=vip",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "checkout.stripe.com" in data["url"]
        print(f"✅ Client VIP checkout URL generated")
    
    def test_training_purchase(self, client_token):
        """Test training purchase checkout"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        # First get available trainings
        trainings_response = requests.get(f"{BASE_URL}/api/trainings")
        assert trainings_response.status_code == 200
        trainings = trainings_response.json()
        
        if trainings and len(trainings) > 0:
            training_id = trainings[0]["id"]
            response = requests.post(
                f"{BASE_URL}/api/trainings/{training_id}/purchase",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "url" in data
            assert "checkout.stripe.com" in data["url"]
            print(f"✅ Training purchase checkout URL: {data['url'][:80]}...")
        else:
            print("⚠️ No trainings available to test purchase")
    
    def test_advertising_payment(self, enterprise_token):
        """Test advertising payment checkout"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        # Create an ad first
        ad_data = {
            "title": "TEST_Ad_Audit",
            "description": "Test advertisement for audit",
            "placement": "homepage",
            "budget": 100.0,
            "duration_days": 7
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/advertising",
            headers=headers,
            json=ad_data
        )
        
        if create_response.status_code == 200:
            ad = create_response.json()
            ad_id = ad.get("id")
            
            # Try to pay for the ad
            pay_response = requests.post(
                f"{BASE_URL}/api/advertising/{ad_id}/pay",
                headers=headers
            )
            
            if pay_response.status_code == 200:
                data = pay_response.json()
                if "url" in data:
                    assert "checkout.stripe.com" in data["url"]
                    print(f"✅ Advertising payment checkout URL generated")
                else:
                    print(f"✅ Advertising payment processed: {data}")
            else:
                print(f"⚠️ Advertising payment endpoint returned: {pay_response.status_code}")
        else:
            print(f"⚠️ Could not create ad for payment test: {create_response.status_code}")


class TestEnterpriseContentCreation:
    """Enterprise content creation tests"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_create_service_product(self, enterprise_token):
        """Test creating a service/product"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        service_data = {
            "name": f"TEST_Service_Audit_{int(time.time())}",
            "description": "Test service for global audit",
            "price": 99.99,
            "category": "soins_esthetiques",
            "type": "service",
            "images": [],
            "is_delivery": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/services-products",
            headers=headers,
            json=service_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == service_data["name"]
        assert data["price"] == service_data["price"]
        assert "id" in data
        print(f"✅ Service created: {data['name']} (ID: {data['id']})")
        return data["id"]
    
    def test_create_training(self, enterprise_token):
        """Test creating a training"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        training_data = {
            "title": f"TEST_Training_Audit_{int(time.time())}",
            "description": "Test training for global audit",
            "price": 299.99,
            "category": "business",
            "duration": "2 heures",
            "training_type": "online",
            "certificate": True,
            "max_participants": 20
        }
        
        response = requests.post(
            f"{BASE_URL}/api/enterprise/trainings",
            headers=headers,
            json=training_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == training_data["title"]
        assert data["price"] == training_data["price"]
        assert "id" in data
        print(f"✅ Training created: {data['title']} (ID: {data['id']})")
        return data["id"]
    
    def test_create_job(self, enterprise_token):
        """Test creating a job offer"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        job_data = {
            "title": f"TEST_Job_Audit_{int(time.time())}",
            "description": "Test job offer for global audit",
            "type": "CDI",
            "location": "Lausanne",
            "salary": "5000-7000 CHF",
            "requirements": ["Experience required", "Team player"],
            "is_active": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/enterprise/jobs",
            headers=headers,
            json=job_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == job_data["title"]
        assert data["type"] == job_data["type"]
        assert "id" in data
        print(f"✅ Job created: {data['title']} (ID: {data['id']})")
        return data["id"]
    
    def test_list_enterprise_services(self, enterprise_token):
        """Test listing enterprise services"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/services-products?type=service&limit=10",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✅ Listed {len(data['items'])} services")
    
    def test_list_enterprise_trainings(self, enterprise_token):
        """Test listing enterprise trainings"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/enterprise/trainings",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Listed {len(data)} enterprise trainings")
    
    def test_list_enterprise_jobs(self, enterprise_token):
        """Test listing enterprise jobs"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/enterprise/jobs",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Listed {len(data)} enterprise jobs")


class TestClientActivityFeed:
    """Client activity feed tests with friends algorithm"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_client_activity_feed(self, client_token):
        """Test client activity feed endpoint"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/client/activity-feed?limit=10",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        print(f"✅ Client activity feed returned {len(data['activities'])} activities")
    
    def test_client_my_feed(self, client_token):
        """Test client personalized feed (my-feed)"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/client/my-feed?limit=10",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        print(f"✅ Client my-feed returned {len(data['activities'])} activities")
        
        # Check algorithm sources
        if "algorithm_sources" in data:
            print(f"   Algorithm sources: {data['algorithm_sources']}")


class TestEnterpriseActivityFeed:
    """Enterprise activity feed tests with tier-based algorithm"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_enterprise_activity_feed(self, enterprise_token):
        """Test enterprise activity feed with tier-based features"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/enterprise/activity-feed",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        print(f"✅ Enterprise activity feed returned {len(data['activities'])} activities")
        
        # Check tier-based features
        if "features_available" in data:
            features = data["features_available"]
            print(f"   Features available: {features}")
            assert "partner_posts" in features
            assert "competitor_offers" in features
    
    def test_enterprise_activity_post(self, enterprise_token):
        """Test creating an enterprise activity post"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        post_data = {
            "activity_type": "news",
            "title": f"TEST_Activity_Audit_{int(time.time())}",
            "content": "Test activity post for global audit"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/enterprise/activity-post",
            headers=headers,
            json=post_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == post_data["title"]
        print(f"✅ Enterprise activity post created: {data['title']}")


class TestClientLifestyle:
    """Client lifestyle tests (wishlist, personal providers)"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_lifestyle(self, client_token):
        """Test getting client lifestyle data"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/client/lifestyle",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "wishlist" in data
        assert "personal_providers" in data
        print(f"✅ Client lifestyle: {len(data['wishlist'])} wishlist items, {len(data['personal_providers'])} providers")
    
    def test_get_wishlist(self, client_token):
        """Test getting client wishlist"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/client/wishlist",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Client wishlist returned {len(data)} items")
    
    def test_add_to_wishlist(self, client_token):
        """Test adding item to wishlist"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        # First get a service/product to add
        services_response = requests.get(f"{BASE_URL}/api/services-products?type=service&limit=1")
        if services_response.status_code == 200:
            services = services_response.json()
            if services.get("items") and len(services["items"]) > 0:
                item = services["items"][0]
                
                wishlist_data = {
                    "item_type": "service",
                    "item_id": item["id"],
                    "item_name": item["name"],
                    "item_price": item.get("price", 0),
                    "item_image": item.get("images", [""])[0] if item.get("images") else ""
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/client/wishlist",
                    headers=headers,
                    json=wishlist_data
                )
                
                # 200 = added, 400 = already exists (both are valid)
                assert response.status_code in [200, 400]
                if response.status_code == 200:
                    print(f"✅ Added to wishlist: {item['name']}")
                else:
                    print(f"✅ Item already in wishlist (expected behavior)")
            else:
                print("⚠️ No services available to add to wishlist")
        else:
            print("⚠️ Could not fetch services for wishlist test")
    
    def test_get_personal_providers(self, client_token):
        """Test getting personal providers"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/client/personal-providers",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Personal providers returned {len(data)} providers")


class TestCashbackSystem:
    """Cashback system tests with subscription-based rates"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_cashback_balance(self, client_token):
        """Test getting cashback balance"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/cashback/balance",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        print(f"✅ Cashback balance: {data['balance']} CHF")
        
        # Check for rate info
        if "cashback_rate" in data:
            print(f"   Cashback rate: {data['cashback_rate']}")
    
    def test_get_cashback_history(self, client_token):
        """Test getting cashback history"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/cashback/history",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Cashback history returned {len(data.get('transactions', data))} transactions")


class TestEnterpriseSubscriptionStatus:
    """Enterprise subscription status tests"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_subscription_status(self, enterprise_token):
        """Test getting enterprise subscription status"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/enterprise/subscription-status",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "tier" in data
        assert "available_plans" in data
        
        print(f"✅ Enterprise subscription status:")
        print(f"   Tier: {data['tier']}")
        print(f"   Has subscription: {data.get('has_subscription', False)}")
        print(f"   Available plans: {len(data['available_plans'])}")
        
        # Verify tier values
        valid_tiers = ["free", "basic", "premium", "optimisation"]
        assert data["tier"] in valid_tiers
        
        # Check features
        if "features" in data:
            print(f"   Features: {data['features']}")


class TestEnterpriseSuggestions:
    """Enterprise suggestions tests based on tier"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_suggestions(self, enterprise_token):
        """Test getting enterprise suggestions"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/enterprise/suggestions",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        print(f"✅ Enterprise suggestions returned {len(data)} suggestions")
        
        # Check suggestion structure
        if len(data) > 0:
            suggestion = data[0]
            assert "business_name" in suggestion or "id" in suggestion
            if "reason" in suggestion:
                print(f"   Sample reason: {suggestion['reason']}")


class TestEnterpriseFavorites:
    """Enterprise favorites (partners) tests"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_favorites(self, enterprise_token):
        """Test getting enterprise favorites"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/enterprise/favorites",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Enterprise favorites returned {len(data)} partners")
    
    def test_add_favorite(self, enterprise_token):
        """Test adding enterprise to favorites"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        # Get list of enterprises to add as favorite
        enterprises_response = requests.get(f"{BASE_URL}/api/enterprises?limit=5")
        if enterprises_response.status_code == 200:
            enterprises = enterprises_response.json().get("enterprises", [])
            
            # Find an enterprise that's not the current one
            for enterprise in enterprises:
                if enterprise.get("email") != ENTERPRISE_EMAIL:
                    response = requests.post(
                        f"{BASE_URL}/api/enterprise/favorites",
                        headers=headers,
                        json={"enterprise_id": enterprise["id"]}
                    )
                    
                    # 200 = added, 400 = already exists
                    assert response.status_code in [200, 400]
                    if response.status_code == 200:
                        print(f"✅ Added favorite: {enterprise.get('business_name', enterprise['id'])}")
                    else:
                        print(f"✅ Enterprise already in favorites (expected)")
                    break
            else:
                print("⚠️ No other enterprises available to add as favorite")
        else:
            print("⚠️ Could not fetch enterprises for favorites test")


class TestHomepageSections:
    """Homepage sections tests (tendances, guests, premium, jobs, trainings)"""
    
    def test_get_tendances(self):
        """Test getting tendances (labeled enterprises)"""
        response = requests.get(f"{BASE_URL}/api/featured/tendances")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Tendances returned {len(data)} enterprises")
    
    def test_get_guests(self):
        """Test getting guests (certified enterprises)"""
        response = requests.get(f"{BASE_URL}/api/featured/guests")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Guests returned {len(data)} enterprises")
    
    def test_get_premium(self):
        """Test getting premium enterprises"""
        response = requests.get(f"{BASE_URL}/api/featured/premium")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Premium returned {len(data)} enterprises")
    
    def test_get_offres(self):
        """Test getting current offers"""
        response = requests.get(f"{BASE_URL}/api/featured/offres")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Offres returned {len(data)} items")
    
    def test_list_all_jobs(self):
        """Test listing all jobs"""
        response = requests.get(f"{BASE_URL}/api/jobs")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Jobs returned {len(data)} job offers")
    
    def test_list_all_trainings(self):
        """Test listing all trainings"""
        response = requests.get(f"{BASE_URL}/api/trainings")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Trainings returned {len(data)} trainings")


class TestCategories:
    """Category endpoints tests"""
    
    def test_get_product_categories(self):
        """Test getting product categories"""
        response = requests.get(f"{BASE_URL}/api/categories/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        print(f"✅ Product categories returned {len(data)} categories")
    
    def test_get_service_categories(self):
        """Test getting service categories"""
        response = requests.get(f"{BASE_URL}/api/categories/services")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        print(f"✅ Service categories returned {len(data)} categories")


class TestEnterprisesList:
    """Enterprises listing tests"""
    
    def test_list_enterprises(self):
        """Test listing all enterprises"""
        response = requests.get(f"{BASE_URL}/api/enterprises?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "enterprises" in data
        assert "total" in data
        print(f"✅ Enterprises: {len(data['enterprises'])} of {data['total']} total")
    
    def test_filter_certified_enterprises(self):
        """Test filtering certified enterprises"""
        response = requests.get(f"{BASE_URL}/api/enterprises?is_certified=true&limit=10")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Certified enterprises: {len(data['enterprises'])}")
    
    def test_filter_premium_enterprises(self):
        """Test filtering premium enterprises"""
        response = requests.get(f"{BASE_URL}/api/enterprises?is_premium=true&limit=10")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Premium enterprises: {len(data['enterprises'])}")


class TestClientPremiumStatus:
    """Client premium status tests"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_premium_status(self, client_token):
        """Test getting client premium status"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/client/premium-status",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        print(f"✅ Client premium status:")
        print(f"   Current plan: {data.get('current_plan', 'free')}")
        print(f"   Is premium: {data.get('is_premium', False)}")
        
        if "benefits" in data:
            print(f"   Benefits: {data['benefits']}")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_cleanup_test_data(self, enterprise_token):
        """Clean up TEST_ prefixed data created during tests"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        # Get and delete test services
        services_response = requests.get(f"{BASE_URL}/api/services-products?limit=100")
        if services_response.status_code == 200:
            items = services_response.json().get("items", [])
            deleted_count = 0
            for item in items:
                if item.get("name", "").startswith("TEST_"):
                    delete_response = requests.delete(
                        f"{BASE_URL}/api/services-products/{item['id']}",
                        headers=headers
                    )
                    if delete_response.status_code == 200:
                        deleted_count += 1
            print(f"✅ Cleaned up {deleted_count} test services/products")
        
        print("✅ Test cleanup completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
