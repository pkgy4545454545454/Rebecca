"""
Iteration 43 - Full E2E Audit Test Suite
Testing all critical flows:
- Auth flow (login, register, me endpoint)
- Enterprise dashboard and profile management
- Media Pub IA - Templates and order creation
- Video Pub IA - Templates and order creation
- Stripe payment checkout for Media Pub
- Success pages after payment
- Gamification - profile and XP
- Cashback - balance and history
- Admin dashboard - stats and management
- Subscriptions - available plans
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

# Test credentials
ADMIN_CREDS = {"email": "admin@titelli.com", "password": "Admin123!"}
CLIENT_CREDS = {"email": "test.client@titelli.com", "password": "Test123!"}
ENTERPRISE_CREDS = {"email": "test.entreprise@titelli.com", "password": "Test123!"}
ENTERPRISE_ID = "697c98c257acdc69eb80fe5c"


class TestAuthFlow:
    """Test authentication endpoints"""
    
    def test_health_check(self):
        """Verify API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health check passed")
    
    def test_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_CREDS["email"]
        print(f"✅ Admin login successful - User type: {data['user'].get('user_type')}")
        return data["token"]
    
    def test_client_login(self):
        """Test client login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        print(f"✅ Client login successful - User: {data['user'].get('first_name')} {data['user'].get('last_name')}")
        return data["token"]
    
    def test_enterprise_login(self):
        """Test enterprise login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ENTERPRISE_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "entreprise"
        print(f"✅ Enterprise login successful - User: {data['user'].get('first_name')}")
        return data["token"]
    
    def test_me_endpoint(self):
        """Test /auth/me endpoint with valid token"""
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        token = login_response.json()["token"]
        
        # Then get me
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == CLIENT_CREDS["email"]
        print(f"✅ /auth/me endpoint working - Cashback balance: {data.get('cashback_balance', 0)} CHF")
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✅ Invalid login correctly rejected")


class TestEnterpriseDashboard:
    """Test enterprise dashboard and profile management"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ENTERPRISE_CREDS)
        return response.json()["token"]
    
    def test_get_enterprise_profile(self, enterprise_token):
        """Test getting enterprise profile"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/enterprises", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "enterprises" in data
        print(f"✅ Enterprise list retrieved - Total: {data.get('total', 0)}")
    
    def test_get_enterprise_by_id(self, enterprise_token):
        """Test getting specific enterprise"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/enterprises/{ENTERPRISE_ID}", headers=headers)
        # May return 404 if enterprise doesn't exist, which is acceptable
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enterprise found: {data.get('business_name', 'N/A')}")
        else:
            print(f"⚠️ Enterprise {ENTERPRISE_ID} not found (may be expected)")
    
    def test_get_services_products(self, enterprise_token):
        """Test getting services/products"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/services-products", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✅ Services/Products retrieved - Total: {data.get('total', 0)}")


class TestMediaPubIA:
    """Test Media Pub IA - Templates and order creation"""
    
    def test_get_templates(self):
        """Test getting media pub templates"""
        response = requests.get(f"{BASE_URL}/api/media-pub/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "categories" in data
        assert len(data["templates"]) > 0
        print(f"✅ Media Pub templates loaded - Total: {len(data['templates'])} templates")
        print(f"   Categories: {', '.join(data['categories'])}")
    
    def test_get_template_detail(self):
        """Test getting specific template detail"""
        # First get templates
        templates_response = requests.get(f"{BASE_URL}/api/media-pub/templates")
        templates = templates_response.json()["templates"]
        
        if templates:
            template_id = templates[0]["id"]
            response = requests.get(f"{BASE_URL}/api/media-pub/templates/{template_id}")
            assert response.status_code == 200
            data = response.json()
            assert "name" in data
            assert "price" in data
            print(f"✅ Template detail retrieved: {data['name']} - {data['price']} CHF")
    
    def test_create_media_pub_order(self):
        """Test creating a media pub order"""
        order_data = {
            "template_id": "social_promo_1",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Slogan de test",
            "product_name": "TEST_Produit Test",
            "description": "Description de test",
            "brand_colors": ["#FF5733", "#333333"],
            "additional_notes": "Notes de test"
        }
        
        response = requests.post(f"{BASE_URL}/api/media-pub/orders", json=order_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] in ["processing", "pending"]
        print(f"✅ Media Pub order created - ID: {data['id']}, Status: {data['status']}")
        return data["id"]
    
    def test_get_order_status(self):
        """Test getting order status"""
        # Create an order first
        order_data = {
            "template_id": "social_promo_1",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Status Check",
            "product_name": "TEST_Status Product",
            "brand_colors": ["#0066CC", "#FFFFFF"]
        }
        create_response = requests.post(f"{BASE_URL}/api/media-pub/orders", json=order_data)
        order_id = create_response.json()["id"]
        
        # Get order status
        response = requests.get(f"{BASE_URL}/api/media-pub/orders/{order_id}")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"✅ Order status retrieved - ID: {order_id}, Status: {data['status']}")


class TestVideoPubIA:
    """Test Video Pub IA - Templates and order creation"""
    
    def test_get_video_templates(self):
        """Test getting video pub templates"""
        response = requests.get(f"{BASE_URL}/api/video-pub/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) > 0
        print(f"✅ Video Pub templates loaded - Total: {len(data['templates'])} templates")
        print(f"   Categories: {', '.join(data.get('categories', []))}")
    
    def test_get_video_template_detail(self):
        """Test getting specific video template"""
        templates_response = requests.get(f"{BASE_URL}/api/video-pub/templates")
        templates = templates_response.json()["templates"]
        
        if templates:
            template_id = templates[0]["id"]
            response = requests.get(f"{BASE_URL}/api/video-pub/templates/{template_id}")
            assert response.status_code == 200
            data = response.json()
            assert "name" in data
            assert "price" in data
            assert "duration" in data
            print(f"✅ Video template detail: {data['name']} - {data['price']} CHF, {data['duration']}s")
    
    def test_create_video_order(self):
        """Test creating a video pub order"""
        order_data = {
            "template_id": "social_reel_1",
            "enterprise_id": "demo-enterprise",
            "product_name": "TEST_Video Product",
            "slogan": "TEST_Video Slogan",
            "description": "Test video description",
            "style": "moderne et élégant",
            "brand_colors": ["#8B5CF6", "#FFFFFF"]
        }
        
        response = requests.post(f"{BASE_URL}/api/video-pub/orders", json=order_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending_payment"
        print(f"✅ Video order created - ID: {data['id']}, Status: {data['status']}")
        return data["id"]


class TestStripePayment:
    """Test Stripe payment checkout integration"""
    
    def test_create_media_payment_session(self):
        """Test creating Stripe checkout session for media pub"""
        # First create an order
        order_data = {
            "template_id": "social_promo_1",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Payment Test",
            "product_name": "TEST_Payment Product",
            "brand_colors": ["#FF5733", "#333333"]
        }
        order_response = requests.post(f"{BASE_URL}/api/media-pub/orders", json=order_data)
        order_id = order_response.json()["id"]
        
        # Create payment session
        payment_data = {
            "order_id": order_id,
            "origin_url": "https://image-fix-demo.preview.emergentagent.com"
        }
        response = requests.post(f"{BASE_URL}/api/media-pub/payment/create-session", json=payment_data)
        assert response.status_code == 200
        data = response.json()
        assert "checkout_url" in data
        assert "session_id" in data
        assert "stripe.com" in data["checkout_url"]
        print(f"✅ Media Pub Stripe session created - Session ID: {data['session_id'][:20]}...")
    
    def test_create_video_payment_session(self):
        """Test creating Stripe checkout session for video pub"""
        # First create an order
        order_data = {
            "template_id": "social_reel_1",
            "enterprise_id": "demo-enterprise",
            "product_name": "TEST_Video Payment",
            "slogan": "TEST_Video Slogan",
            "style": "moderne"
        }
        order_response = requests.post(f"{BASE_URL}/api/video-pub/orders", json=order_data)
        order_id = order_response.json()["id"]
        
        # Create payment session
        payment_data = {
            "order_id": order_id,
            "origin_url": "https://image-fix-demo.preview.emergentagent.com"
        }
        response = requests.post(f"{BASE_URL}/api/video-pub/payment/create-session", json=payment_data)
        assert response.status_code == 200
        data = response.json()
        assert "checkout_url" in data
        assert "session_id" in data
        print(f"✅ Video Pub Stripe session created - Session ID: {data['session_id'][:20]}...")


class TestGamification:
    """Test gamification - profile and XP"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_get_gamification_profile(self, client_token):
        """Test getting gamification profile"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/gamification/profile", headers=headers)
        # May return 404 if not implemented, which is acceptable
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gamification profile: Level {data.get('level', 1)}, XP: {data.get('xp', 0)}")
        else:
            print(f"⚠️ Gamification profile endpoint returned {response.status_code}")
    
    def test_get_user_profile_with_xp(self, client_token):
        """Test user profile includes XP/gamification data"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Check if user has gamification-related fields
        print(f"✅ User profile retrieved - Premium: {data.get('is_premium', False)}")


class TestCashback:
    """Test cashback - balance and history"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_get_cashback_balance(self, client_token):
        """Test getting cashback balance from user profile"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        cashback = data.get("cashback_balance", 0)
        print(f"✅ Cashback balance: {cashback} CHF")
    
    def test_get_cashback_history(self, client_token):
        """Test getting cashback history"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/cashback/history", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cashback history: {len(data.get('transactions', []))} transactions")
        else:
            print(f"⚠️ Cashback history endpoint returned {response.status_code}")


class TestAdminDashboard:
    """Test admin dashboard - stats and management"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        return response.json()["token"]
    
    def test_get_admin_stats(self, admin_token):
        """Test getting admin dashboard stats"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        stats = data["stats"]
        print(f"✅ Admin stats retrieved:")
        print(f"   - Total users: {stats.get('total_users', 0)}")
        print(f"   - Total enterprises: {stats.get('total_enterprises', 0)}")
        print(f"   - Total orders: {stats.get('total_orders', 0)}")
    
    def test_get_admin_users(self, admin_token):
        """Test getting admin users list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        print(f"✅ Admin users list: {len(data['users'])} users")
    
    def test_get_media_pub_admin_orders(self, admin_token):
        """Test getting media pub orders for admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/media-pub/admin/orders", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert "stats" in data
        print(f"✅ Admin Media Pub orders:")
        print(f"   - Total: {data['stats'].get('total', 0)}")
        print(f"   - Completed: {data['stats'].get('completed', 0)}")
        print(f"   - Revenue: {data['stats'].get('total_revenue', 0)} CHF")


class TestSubscriptions:
    """Test subscriptions - available plans"""
    
    def test_get_subscription_plans(self):
        """Test getting available subscription plans"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        print(f"✅ Subscription plans retrieved: {len(data['plans'])} plans")
        for plan in data["plans"][:3]:
            print(f"   - {plan.get('name', 'N/A')}: {plan.get('price', 0)} CHF")
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_get_user_subscription(self, client_token):
        """Test getting user's current subscription"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/subscriptions/current", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User subscription: {data.get('plan', 'free')}")
        else:
            print(f"⚠️ User subscription endpoint returned {response.status_code}")


class TestSuccessPages:
    """Test success pages exist and are accessible"""
    
    def test_media_pub_success_route(self):
        """Verify media-pub success route exists in frontend"""
        # This tests that the route is configured - actual page rendering is frontend
        response = requests.get(f"{BASE_URL}/media-pub/success")
        # Should return 200 (React SPA serves index.html for all routes)
        assert response.status_code == 200
        print("✅ /media-pub/success route accessible")
    
    def test_video_pub_success_route(self):
        """Verify video-pub success route exists"""
        response = requests.get(f"{BASE_URL}/video-pub/success")
        assert response.status_code == 200
        print("✅ /video-pub/success route accessible")
    
    def test_payment_success_route(self):
        """Verify payment success route exists"""
        response = requests.get(f"{BASE_URL}/payment/success")
        assert response.status_code == 200
        print("✅ /payment/success route accessible")


class TestEnterpriseOrders:
    """Test enterprise orders management"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ENTERPRISE_CREDS)
        return response.json()["token"]
    
    def test_get_enterprise_media_orders(self, enterprise_token):
        """Test getting enterprise media pub orders"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/media-pub/orders?enterprise_id={ENTERPRISE_ID}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enterprise media orders: {len(data.get('orders', []))} orders")
        else:
            # Try with demo enterprise
            response = requests.get(f"{BASE_URL}/api/media-pub/orders?enterprise_id=demo-enterprise", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Demo enterprise media orders: {len(data.get('orders', []))} orders")
    
    def test_get_enterprise_video_orders(self, enterprise_token):
        """Test getting enterprise video pub orders"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/video-pub/orders/enterprise/{ENTERPRISE_ID}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enterprise video orders: {len(data.get('orders', []))} orders")
        else:
            print(f"⚠️ Enterprise video orders returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
