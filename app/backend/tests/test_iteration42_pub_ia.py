"""
Iteration 42 - Pub IA Features Testing
Tests for:
- Media Pub (Images IA) API endpoints
- Video Pub (Vidéos IA) API endpoints
- Enterprise dashboard Commandes Titelli
- Admin dashboard Pub Média IA tab
- Stripe payment session creation
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

# Test credentials
ENTERPRISE_EMAIL = "test.entreprise@titelli.com"
ENTERPRISE_PASSWORD = "Test123!"
ADMIN_EMAIL = "admin@titelli.com"
ADMIN_PASSWORD = "Admin123!"

# Known enterprise ID from test data
TEST_ENTERPRISE_ID = "697c98c257acdc69eb80fe5c"


class TestMediaPubAPI:
    """Tests for Media Pub (Images IA) API"""
    
    def test_get_templates(self):
        """Test GET /api/media-pub/templates returns all templates"""
        response = requests.get(f"{BASE_URL}/api/media-pub/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert "categories" in data
        assert "by_category" in data
        assert "total" in data
        
        # Should have 34 templates
        assert data["total"] >= 30
        
        # Should have expected categories
        expected_categories = ["Réseaux Sociaux", "Bannières Web", "Restauration"]
        for cat in expected_categories:
            assert cat in data["categories"]
        
        print(f"✅ Found {data['total']} templates across {len(data['categories'])} categories")
    
    def test_get_template_detail(self):
        """Test GET /api/media-pub/templates/{id} returns template details"""
        template_id = "social_promo_1"
        response = requests.get(f"{BASE_URL}/api/media-pub/templates/{template_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == template_id
        assert "name" in data
        assert "category" in data
        assert "price" in data
        assert "format" in data
        
        print(f"✅ Template detail: {data['name']} - {data['price']} CHF")
    
    def test_get_template_not_found(self):
        """Test GET /api/media-pub/templates/{id} returns 404 for invalid ID"""
        response = requests.get(f"{BASE_URL}/api/media-pub/templates/invalid_template_id")
        assert response.status_code == 404
        print("✅ Invalid template returns 404")
    
    def test_create_order(self):
        """Test POST /api/media-pub/orders creates a new order"""
        order_data = {
            "template_id": "social_promo_1",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Slogan Iteration 42",
            "product_name": "TEST_Product Iteration 42",
            "description": "Test description for iteration 42",
            "brand_colors": ["#FF5733", "#333333"],
            "additional_notes": "Test notes"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/media-pub/orders",
            json=order_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["status"] == "processing"
        assert "estimated_time" in data
        
        print(f"✅ Order created: {data['id']} - Status: {data['status']}")
        return data["id"]
    
    def test_create_sur_mesure_order(self):
        """Test POST /api/media-pub/orders with sur_mesure template"""
        order_data = {
            "template_id": "sur_mesure",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Custom creation",
            "product_name": "TEST_Sur Mesure Product",
            "description": "Custom design request",
            "brand_colors": ["#0047AB", "#FFFFFF"],
            "additional_notes": "Please create a unique design"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/media-pub/orders",
            json=order_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["status"] == "processing"
        
        print(f"✅ Sur Mesure order created: {data['id']}")
    
    def test_get_order_detail(self):
        """Test GET /api/media-pub/orders/{id} returns order details"""
        # First create an order
        order_data = {
            "template_id": "menu_elegant_1",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Menu Slogan",
            "product_name": "TEST_Restaurant Menu",
            "brand_colors": ["#D4AF37", "#000000"]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/media-pub/orders",
            json=order_data
        )
        order_id = create_response.json()["id"]
        
        # Get order detail
        response = requests.get(f"{BASE_URL}/api/media-pub/orders/{order_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == order_id
        assert "template_name" in data
        assert "status" in data
        assert "price" in data
        
        print(f"✅ Order detail: {data['template_name']} - {data['status']}")
    
    def test_get_enterprise_orders(self):
        """Test GET /api/media-pub/orders/enterprise/{id} returns enterprise orders"""
        response = requests.get(f"{BASE_URL}/api/media-pub/orders/enterprise/{TEST_ENTERPRISE_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "orders" in data
        assert "total" in data
        
        print(f"✅ Enterprise has {data['total']} media orders")
    
    def test_admin_get_all_orders(self):
        """Test GET /api/media-pub/admin/orders returns all orders with stats"""
        response = requests.get(f"{BASE_URL}/api/media-pub/admin/orders")
        assert response.status_code == 200
        
        data = response.json()
        assert "orders" in data
        assert "stats" in data
        
        stats = data["stats"]
        assert "total" in stats
        assert "completed" in stats
        assert "processing" in stats
        assert "failed" in stats
        assert "total_revenue" in stats
        
        print(f"✅ Admin stats: {stats['total']} total, {stats['completed']} completed, {stats['total_revenue']} CHF revenue")


class TestVideoPubAPI:
    """Tests for Video Pub (Vidéos IA) API"""
    
    def test_get_video_templates(self):
        """Test GET /api/video-pub/templates returns all video templates"""
        response = requests.get(f"{BASE_URL}/api/video-pub/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert "categories" in data
        assert "by_category" in data
        assert "total" in data
        
        # Should have video templates
        assert data["total"] >= 10
        
        # Check template structure
        if data["templates"]:
            template = data["templates"][0]
            assert "id" in template
            assert "name" in template
            assert "duration" in template
            assert "size" in template
            assert "price" in template
        
        print(f"✅ Found {data['total']} video templates across {len(data['categories'])} categories")
    
    def test_get_video_template_detail(self):
        """Test GET /api/video-pub/templates/{id} returns template details"""
        template_id = "social_reel_1"
        response = requests.get(f"{BASE_URL}/api/video-pub/templates/{template_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == template_id
        assert "name" in data
        assert "duration" in data
        assert "price" in data
        
        print(f"✅ Video template: {data['name']} - {data['duration']}s - {data['price']} CHF")
    
    def test_create_video_order(self):
        """Test POST /api/video-pub/orders creates a new video order"""
        order_data = {
            "template_id": "social_reel_1",
            "enterprise_id": "demo-enterprise",
            "product_name": "TEST_Video Product",
            "slogan": "TEST_Video Slogan",
            "description": "Test video description",
            "style": "moderne et élégant",
            "brand_colors": ["#8B5CF6", "#FFFFFF"],
            "additional_notes": "Test video notes"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/video-pub/orders",
            json=order_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending_payment"
        assert "price" in data
        assert "estimated_time" in data
        
        print(f"✅ Video order created: {data['id']} - {data['price']} CHF")
        return data["id"]
    
    def test_get_video_order_detail(self):
        """Test GET /api/video-pub/orders/{id} returns order details"""
        # First create an order
        order_data = {
            "template_id": "ad_hero",
            "enterprise_id": "demo-enterprise",
            "product_name": "TEST_Hero Video",
            "slogan": "Premium Quality",
            "style": "luxueux et sophistiqué"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/video-pub/orders",
            json=order_data
        )
        order_id = create_response.json()["id"]
        
        # Get order detail
        response = requests.get(f"{BASE_URL}/api/video-pub/orders/{order_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == order_id
        assert "template_name" in data
        assert "status" in data
        assert "duration" in data
        
        print(f"✅ Video order detail: {data['template_name']} - {data['status']}")
    
    def test_get_enterprise_video_orders(self):
        """Test GET /api/video-pub/orders/enterprise/{id} returns enterprise video orders"""
        response = requests.get(f"{BASE_URL}/api/video-pub/orders/enterprise/{TEST_ENTERPRISE_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "orders" in data
        assert "total" in data
        
        print(f"✅ Enterprise has {data['total']} video orders")
    
    def test_admin_get_video_orders(self):
        """Test GET /api/video-pub/admin/orders returns all video orders"""
        response = requests.get(f"{BASE_URL}/api/video-pub/admin/orders")
        assert response.status_code == 200
        
        data = response.json()
        assert "orders" in data
        assert "stats" in data
        
        stats = data["stats"]
        assert "total" in stats
        assert "completed" in stats
        assert "generating" in stats
        
        print(f"✅ Admin video stats: {stats['total']} total, {stats['completed']} completed")


class TestStripePaymentIntegration:
    """Tests for Stripe payment session creation"""
    
    def test_create_media_payment_session(self):
        """Test POST /api/media-pub/payment/create-session creates Stripe session"""
        # First create an order
        order_data = {
            "template_id": "social_promo_1",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Payment Test",
            "product_name": "TEST_Payment Product",
            "brand_colors": ["#FF5733", "#FFFFFF"]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/media-pub/orders",
            json=order_data
        )
        order_id = create_response.json()["id"]
        
        # Create payment session
        payment_data = {
            "order_id": order_id,
            "origin_url": "https://image-fix-demo.preview.emergentagent.com"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/media-pub/payment/create-session",
            json=payment_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "checkout_url" in data
        assert "session_id" in data
        assert "stripe.com" in data["checkout_url"]
        
        print(f"✅ Stripe session created: {data['session_id'][:20]}...")
    
    def test_create_video_payment_session(self):
        """Test POST /api/video-pub/payment/create-session creates Stripe session"""
        # First create a video order
        order_data = {
            "template_id": "social_reel_1",
            "enterprise_id": "demo-enterprise",
            "product_name": "TEST_Video Payment",
            "slogan": "Payment Test",
            "style": "moderne"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/video-pub/orders",
            json=order_data
        )
        order_id = create_response.json()["id"]
        
        # Create payment session
        payment_data = {
            "order_id": order_id,
            "origin_url": "https://image-fix-demo.preview.emergentagent.com"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/video-pub/payment/create-session",
            json=payment_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "checkout_url" in data
        assert "session_id" in data
        
        print(f"✅ Video Stripe session created: {data['session_id'][:20]}...")


class TestAuthentication:
    """Tests for authentication flow"""
    
    def test_enterprise_login(self):
        """Test enterprise user login"""
        login_data = {
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "entreprise"
        
        print(f"✅ Enterprise login successful: {data['user']['email']}")
        return data["token"]
    
    def test_admin_login(self):
        """Test admin user login"""
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        
        print(f"✅ Admin login successful: {data['user']['email']}")
        return data["token"]
    
    def test_client_login(self):
        """Test client user login"""
        login_data = {
            "email": "test.client@titelli.com",
            "password": "Test123!"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert data["user"]["user_type"] == "client"
        
        print(f"✅ Client login successful: {data['user']['email']}")


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        
        print("✅ API is healthy")
    
    def test_frontend_loads(self):
        """Test frontend homepage loads"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        assert "Titelli" in response.text
        
        print("✅ Frontend loads successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
