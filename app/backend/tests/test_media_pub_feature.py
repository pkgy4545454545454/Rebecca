"""
Test Media Pub Feature - Pub Média / Canva-style Ad Creation
Tests for:
- Templates listing and filtering
- Order creation (standard and sur mesure)
- Order status retrieval
- Admin order management
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMediaPubTemplates:
    """Tests for Media Pub templates endpoints"""
    
    def test_get_all_templates(self):
        """Test GET /api/media-pub/templates returns templates list"""
        response = requests.get(f"{BASE_URL}/api/media-pub/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert "categories" in data
        assert "by_category" in data
        assert "total" in data
        
        # Verify templates structure
        assert len(data["templates"]) > 0
        template = data["templates"][0]
        assert "id" in template
        assert "name" in template
        assert "category" in template
        assert "price" in template
        assert "preview_url" in template
        assert "format" in template
        
        print(f"✅ Found {data['total']} templates across {len(data['categories'])} categories")
    
    def test_templates_have_required_categories(self):
        """Test that templates include expected categories"""
        response = requests.get(f"{BASE_URL}/api/media-pub/templates")
        assert response.status_code == 200
        
        data = response.json()
        categories = data["categories"]
        
        # Expected categories based on the code
        expected_categories = [
            "Réseaux Sociaux",
            "Bannières Web",
            "Restauration",
            "Flyers & Affiches",
            "Email Marketing",
            "Vidéo",
            "Print"
        ]
        
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
        
        print(f"✅ All expected categories present: {categories}")
    
    def test_filter_templates_by_category(self):
        """Test filtering templates by category"""
        response = requests.get(f"{BASE_URL}/api/media-pub/templates?category=Restauration")
        assert response.status_code == 200
        
        data = response.json()
        # All returned templates should be in Restauration category
        for template in data["templates"]:
            assert template["category"] == "Restauration"
        
        print(f"✅ Filtered to {len(data['templates'])} Restauration templates")
    
    def test_get_template_detail(self):
        """Test GET /api/media-pub/templates/{template_id}"""
        # First get a template ID
        response = requests.get(f"{BASE_URL}/api/media-pub/templates")
        template_id = response.json()["templates"][0]["id"]
        
        # Get detail
        response = requests.get(f"{BASE_URL}/api/media-pub/templates/{template_id}")
        assert response.status_code == 200
        
        template = response.json()
        assert template["id"] == template_id
        assert "name" in template
        assert "price" in template
        
        print(f"✅ Template detail retrieved: {template['name']}")
    
    def test_get_nonexistent_template(self):
        """Test 404 for non-existent template"""
        response = requests.get(f"{BASE_URL}/api/media-pub/templates/nonexistent_template_xyz")
        assert response.status_code == 404
        print("✅ Correctly returns 404 for non-existent template")


class TestMediaPubOrders:
    """Tests for Media Pub order endpoints"""
    
    def test_create_order_standard_template(self):
        """Test POST /api/media-pub/orders with standard template"""
        order_data = {
            "template_id": "social_promo_1",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Slogan Publicitaire",
            "product_name": "TEST_Mon Produit",
            "description": "Description du produit test",
            "brand_colors": ["#0066CC", "#FFFFFF"],
            "additional_notes": "Notes de test"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/media-pub/orders",
            json=order_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["status"] == "processing"
        assert "message" in data
        assert "estimated_time" in data
        
        print(f"✅ Order created: {data['id']} - Status: {data['status']}")
        return data["id"]
    
    def test_create_order_sur_mesure(self):
        """Test POST /api/media-pub/orders with sur_mesure template"""
        order_data = {
            "template_id": "sur_mesure",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Création personnalisée pour restaurant italien",
            "product_name": "Création Sur Mesure",
            "description": "Couleurs: Rouge bordeaux, doré\nStyle: Élégant italien\nInfos: Pour pizzeria",
            "brand_colors": ["#8B0000", "#FFD700"],
            "additional_notes": "Style trattoria authentique"
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
    
    def test_create_order_invalid_template(self):
        """Test order creation with invalid template returns 404"""
        order_data = {
            "template_id": "invalid_template_xyz",
            "enterprise_id": "demo-enterprise",
            "slogan": "Test",
            "product_name": "Test"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/media-pub/orders",
            json=order_data
        )
        assert response.status_code == 404
        print("✅ Correctly returns 404 for invalid template")
    
    def test_get_order_detail(self):
        """Test GET /api/media-pub/orders/{order_id}"""
        # Use the existing completed order
        order_id = "fb314c13"
        
        response = requests.get(f"{BASE_URL}/api/media-pub/orders/{order_id}")
        assert response.status_code == 200
        
        order = response.json()
        assert order["id"] == order_id
        assert "status" in order
        assert "template_name" in order
        assert "slogan" in order
        assert "product_name" in order
        assert "price" in order
        
        # Check if completed order has image_url
        if order["status"] == "completed":
            assert "image_url" in order
            assert order["image_url"] is not None
            print(f"✅ Completed order has image: {order['image_url'][:50]}...")
        else:
            print(f"✅ Order status: {order['status']}")
    
    def test_get_nonexistent_order(self):
        """Test 404 for non-existent order"""
        response = requests.get(f"{BASE_URL}/api/media-pub/orders/nonexistent_order_xyz")
        assert response.status_code == 404
        print("✅ Correctly returns 404 for non-existent order")
    
    def test_get_enterprise_orders(self):
        """Test GET /api/media-pub/orders?enterprise_id=demo-enterprise"""
        response = requests.get(f"{BASE_URL}/api/media-pub/orders?enterprise_id=demo-enterprise")
        assert response.status_code == 200
        
        data = response.json()
        assert "orders" in data
        assert "total" in data
        
        # All orders should belong to demo-enterprise
        for order in data["orders"]:
            assert order["enterprise_id"] == "demo-enterprise"
        
        print(f"✅ Found {data['total']} orders for demo-enterprise")


class TestMediaPubAdminRoutes:
    """Tests for Media Pub admin endpoints"""
    
    def test_admin_get_all_orders(self):
        """Test GET /api/media-pub/admin/orders"""
        response = requests.get(f"{BASE_URL}/api/media-pub/admin/orders")
        assert response.status_code == 200
        
        data = response.json()
        assert "orders" in data
        assert "stats" in data
        assert "pagination" in data
        
        # Check stats structure
        stats = data["stats"]
        assert "total" in stats
        assert "processing" in stats
        assert "completed" in stats
        assert "failed" in stats
        assert "total_revenue" in stats
        
        print(f"✅ Admin stats: {stats['total']} total orders, {stats['completed']} completed, Revenue: {stats['total_revenue']} CHF")
    
    def test_admin_filter_by_status(self):
        """Test admin orders filtering by status"""
        response = requests.get(f"{BASE_URL}/api/media-pub/admin/orders?status=completed")
        assert response.status_code == 200
        
        data = response.json()
        for order in data["orders"]:
            assert order["status"] == "completed"
        
        print(f"✅ Filtered to {len(data['orders'])} completed orders")


class TestMediaPubDataValidation:
    """Tests for data validation and edge cases"""
    
    def test_order_with_minimal_data(self):
        """Test order creation with only required fields"""
        order_data = {
            "template_id": "social_promo_1",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Minimal",
            "product_name": "TEST_Minimal Product"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/media-pub/orders",
            json=order_data
        )
        assert response.status_code == 200
        print("✅ Order created with minimal required data")
    
    def test_order_with_custom_colors(self):
        """Test order with custom brand colors"""
        order_data = {
            "template_id": "menu_elegant_1",
            "enterprise_id": "demo-enterprise",
            "slogan": "TEST_Restaurant Gastronomique",
            "product_name": "TEST_Le Gourmet",
            "brand_colors": ["#2C3E50", "#E74C3C", "#ECF0F1"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/media-pub/orders",
            json=order_data
        )
        assert response.status_code == 200
        
        # Verify order was created
        order_id = response.json()["id"]
        detail_response = requests.get(f"{BASE_URL}/api/media-pub/orders/{order_id}")
        order = detail_response.json()
        
        assert order["brand_colors"] == ["#2C3E50", "#E74C3C", "#ECF0F1"]
        print("✅ Order created with custom brand colors")
    
    def test_templates_have_valid_prices(self):
        """Test that all templates have valid prices"""
        response = requests.get(f"{BASE_URL}/api/media-pub/templates")
        templates = response.json()["templates"]
        
        for template in templates:
            assert isinstance(template["price"], (int, float))
            assert template["price"] > 0
            assert template["price"] < 1000  # Reasonable price range
        
        print(f"✅ All {len(templates)} templates have valid prices")
    
    def test_templates_have_valid_preview_urls(self):
        """Test that all templates have valid preview URLs"""
        response = requests.get(f"{BASE_URL}/api/media-pub/templates")
        templates = response.json()["templates"]
        
        for template in templates:
            assert "preview_url" in template
            assert template["preview_url"].startswith("http")
        
        print(f"✅ All templates have valid preview URLs")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
