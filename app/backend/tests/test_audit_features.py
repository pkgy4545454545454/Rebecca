"""
Comprehensive test suite for Titelli Marketplace Audit
Tests: Enterprise Dashboard features, Client Dashboard, Service/Product detail, Cart, Orders, Notifications
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com').rstrip('/')

# Test credentials
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"


class TestAuth:
    """Authentication tests"""
    
    def test_enterprise_login(self):
        """Test enterprise user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "entreprise"
        print(f"✓ Enterprise login successful: {data['user']['email']}")
        return data["token"]
    
    def test_client_login(self):
        """Test client user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200, f"Client login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["user_type"] == "client"
        print(f"✓ Client login successful: {data['user']['email']}")
        return data["token"]


class TestEnterpriseServicesProducts:
    """Test Enterprise Dashboard - Services/Products CRUD with image upload"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get enterprise token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_ids = []
    
    def teardown_method(self):
        """Cleanup created test data"""
        for item_id in self.created_ids:
            try:
                requests.delete(f"{BASE_URL}/api/services-products/{item_id}", headers=self.headers)
            except:
                pass
    
    def test_create_service_with_image(self):
        """Test creating a service with image URL"""
        service_data = {
            "name": "TEST_Service Massage Relaxant",
            "description": "Un massage relaxant de 60 minutes",
            "price": 120.0,
            "category": "soins_esthetiques",
            "type": "service",
            "images": ["https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=800"],
            "is_delivery": False
        }
        response = requests.post(f"{BASE_URL}/api/services-products", json=service_data, headers=self.headers)
        assert response.status_code == 200, f"Create service failed: {response.text}"
        data = response.json()
        assert data["name"] == service_data["name"]
        assert data["price"] == service_data["price"]
        assert len(data["images"]) == 1
        self.created_ids.append(data["id"])
        print(f"✓ Service created with image: {data['id']}")
        
        # Verify persistence
        get_response = requests.get(f"{BASE_URL}/api/services-products/{data['id']}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["name"] == service_data["name"]
        print(f"✓ Service persisted and retrieved successfully")
    
    def test_create_product_with_delivery(self):
        """Test creating a product with delivery option"""
        product_data = {
            "name": "TEST_Crème Hydratante Bio",
            "description": "Crème hydratante naturelle pour le visage",
            "price": 45.0,
            "category": "maquillage_beaute",
            "type": "product",
            "images": ["https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800"],
            "is_delivery": True
        }
        response = requests.post(f"{BASE_URL}/api/services-products", json=product_data, headers=self.headers)
        assert response.status_code == 200, f"Create product failed: {response.text}"
        data = response.json()
        assert data["is_delivery"] == True
        self.created_ids.append(data["id"])
        print(f"✓ Product created with delivery: {data['id']}")
    
    def test_delete_service_product(self):
        """Test deleting a service/product"""
        # First create
        service_data = {
            "name": "TEST_Service to Delete",
            "description": "This will be deleted",
            "price": 50.0,
            "category": "restauration",
            "type": "service"
        }
        create_response = requests.post(f"{BASE_URL}/api/services-products", json=service_data, headers=self.headers)
        assert create_response.status_code == 200
        item_id = create_response.json()["id"]
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/services-products/{item_id}", headers=self.headers)
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        print(f"✓ Service deleted: {item_id}")
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/services-products/{item_id}")
        assert get_response.status_code == 404
        print(f"✓ Deletion verified - item not found")


class TestEnterpriseLogoUpload:
    """Test Enterprise logo upload functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get enterprise profile
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        self.user = me_response.json()
    
    def test_update_enterprise_logo(self):
        """Test updating enterprise logo URL"""
        # Get enterprise
        enterprises_response = requests.get(f"{BASE_URL}/api/enterprises")
        enterprises = enterprises_response.json()["enterprises"]
        
        # Find enterprise for current user
        enterprise = None
        for ent in enterprises:
            if ent.get("user_id") == self.user.get("id"):
                enterprise = ent
                break
        
        if not enterprise:
            pytest.skip("No enterprise found for user")
        
        # Update logo
        logo_url = "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=200"
        update_response = requests.put(
            f"{BASE_URL}/api/enterprises/{enterprise['id']}", 
            json={"logo": logo_url},
            headers=self.headers
        )
        assert update_response.status_code == 200, f"Update logo failed: {update_response.text}"
        print(f"✓ Enterprise logo updated")
        
        # Verify
        get_response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise['id']}")
        assert get_response.status_code == 200
        updated = get_response.json()
        assert updated.get("logo") == logo_url
        print(f"✓ Logo URL persisted: {logo_url[:50]}...")


class TestEnterpriseOffers:
    """Test Enterprise promotional offers"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_ids = []
    
    def teardown_method(self):
        for offer_id in self.created_ids:
            try:
                requests.delete(f"{BASE_URL}/api/enterprise/offers/{offer_id}", headers=self.headers)
            except:
                pass
    
    def test_create_promotional_offer(self):
        """Test creating a promotional offer"""
        offer_data = {
            "title": "TEST_Promo Été -20%",
            "description": "Réduction de 20% sur tous les soins",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "start_date": "2025-01-01",
            "end_date": "2025-03-31",
            "min_purchase": 50.0
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/offers", json=offer_data, headers=self.headers)
        assert response.status_code == 200, f"Create offer failed: {response.text}"
        data = response.json()
        assert data["title"] == offer_data["title"]
        assert data["discount_value"] == 20.0
        self.created_ids.append(data["id"])
        print(f"✓ Promotional offer created: {data['id']}")
        
        # Verify in list
        list_response = requests.get(f"{BASE_URL}/api/enterprise/offers", headers=self.headers)
        assert list_response.status_code == 200
        offers = list_response.json()
        assert any(o["id"] == data["id"] for o in offers)
        print(f"✓ Offer appears in list")


class TestEnterpriseJobs:
    """Test Enterprise job postings"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_ids = []
    
    def teardown_method(self):
        for job_id in self.created_ids:
            try:
                requests.delete(f"{BASE_URL}/api/enterprise/jobs/{job_id}", headers=self.headers)
            except:
                pass
    
    def test_create_job_posting(self):
        """Test creating a job posting"""
        job_data = {
            "title": "TEST_Esthéticienne Confirmée",
            "description": "Nous recherchons une esthéticienne avec 3 ans d'expérience",
            "job_type": "full_time",
            "salary_min": 4000.0,
            "salary_max": 5500.0,
            "salary_type": "monthly",
            "location": "Lausanne",
            "remote": False,
            "requirements": "CAP Esthétique, 3 ans d'expérience minimum",
            "benefits": "Assurance maladie, 5 semaines de vacances"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/jobs", json=job_data, headers=self.headers)
        assert response.status_code == 200, f"Create job failed: {response.text}"
        data = response.json()
        assert data["title"] == job_data["title"]
        assert data["job_type"] == "full_time"
        self.created_ids.append(data["id"])
        print(f"✓ Job posting created: {data['id']}")
        
        # Verify in public list
        public_response = requests.get(f"{BASE_URL}/api/jobs")
        assert public_response.status_code == 200
        jobs = public_response.json()
        assert any(j["id"] == data["id"] for j in jobs)
        print(f"✓ Job appears in public list")


class TestEnterpriseAgenda:
    """Test Enterprise agenda/events"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_ids = []
    
    def teardown_method(self):
        for event_id in self.created_ids:
            try:
                requests.delete(f"{BASE_URL}/api/enterprise/agenda/{event_id}", headers=self.headers)
            except:
                pass
    
    def test_create_agenda_event(self):
        """Test creating an agenda event"""
        event_data = {
            "title": "TEST_Journée Portes Ouvertes",
            "description": "Venez découvrir nos nouveaux soins",
            "event_type": "appointment",
            "start_datetime": "2025-02-15T10:00:00",
            "end_datetime": "2025-02-15T18:00:00",
            "location": "Spa Luxury Lausanne"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/agenda", json=event_data, headers=self.headers)
        assert response.status_code == 200, f"Create event failed: {response.text}"
        data = response.json()
        assert data["title"] == event_data["title"]
        self.created_ids.append(data["id"])
        print(f"✓ Agenda event created: {data['id']}")


class TestEnterpriseTeam:
    """Test Enterprise team management"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_ids = []
    
    def teardown_method(self):
        for member_id in self.created_ids:
            try:
                requests.delete(f"{BASE_URL}/api/enterprise/team/{member_id}", headers=self.headers)
            except:
                pass
    
    def test_add_team_member(self):
        """Test adding a team member"""
        member_data = {
            "first_name": "TEST_Marie",
            "last_name": "Dupont",
            "role": "Esthéticienne Senior",
            "email": "marie.test@spa.com",
            "phone": "+41 79 123 45 67"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/team", json=member_data, headers=self.headers)
        assert response.status_code == 200, f"Add team member failed: {response.text}"
        data = response.json()
        assert data["first_name"] == member_data["first_name"]
        self.created_ids.append(data["id"])
        print(f"✓ Team member added: {data['id']}")
        
        # Verify in list
        list_response = requests.get(f"{BASE_URL}/api/enterprise/team", headers=self.headers)
        assert list_response.status_code == 200
        team = list_response.json()
        assert any(m["id"] == data["id"] for m in team)
        print(f"✓ Team member appears in list")


class TestClientDashboard:
    """Test Client Dashboard sections"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user = response.json()["user"]
    
    def test_get_cashback_balance(self):
        """Test getting cashback balance"""
        response = requests.get(f"{BASE_URL}/api/cashback/balance", headers=self.headers)
        assert response.status_code == 200, f"Get cashback failed: {response.text}"
        data = response.json()
        assert "balance" in data
        print(f"✓ Cashback balance: {data['balance']} CHF")
    
    def test_get_client_orders(self):
        """Test getting client orders"""
        response = requests.get(f"{BASE_URL}/api/orders", headers=self.headers)
        assert response.status_code == 200, f"Get orders failed: {response.text}"
        orders = response.json()
        print(f"✓ Client orders retrieved: {len(orders)} orders")
    
    def test_get_user_profile(self):
        """Test getting user profile (for settings)"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert response.status_code == 200, f"Get profile failed: {response.text}"
        data = response.json()
        assert data["email"] == CLIENT_EMAIL
        print(f"✓ User profile retrieved: {data['email']}")


class TestServiceProductDetail:
    """Test Service/Product detail page and cart"""
    
    def test_get_service_product_detail(self):
        """Test getting service/product detail"""
        # First get list of items
        list_response = requests.get(f"{BASE_URL}/api/services-products?limit=5")
        assert list_response.status_code == 200
        items = list_response.json()["items"]
        
        if not items:
            pytest.skip("No services/products available")
        
        item = items[0]
        detail_response = requests.get(f"{BASE_URL}/api/services-products/{item['id']}")
        assert detail_response.status_code == 200, f"Get detail failed: {detail_response.text}"
        data = detail_response.json()
        assert data["id"] == item["id"]
        assert "name" in data
        assert "price" in data
        print(f"✓ Service/Product detail retrieved: {data['name']} - {data['price']} CHF")
    
    def test_get_enterprise_for_item(self):
        """Test getting enterprise info for a service/product"""
        # Get an item
        list_response = requests.get(f"{BASE_URL}/api/services-products?limit=5")
        items = list_response.json()["items"]
        
        if not items:
            pytest.skip("No services/products available")
        
        item = items[0]
        if not item.get("enterprise_id"):
            pytest.skip("Item has no enterprise_id")
        
        # Get enterprise
        ent_response = requests.get(f"{BASE_URL}/api/enterprises/{item['enterprise_id']}")
        assert ent_response.status_code == 200, f"Get enterprise failed: {ent_response.text}"
        data = ent_response.json()
        assert "business_name" in data
        print(f"✓ Enterprise info retrieved: {data['business_name']}")


class TestOrderCreation:
    """Test order creation flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        # Login as client
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_order_ids = []
    
    def test_create_order(self):
        """Test creating an order"""
        # Get an item to order
        list_response = requests.get(f"{BASE_URL}/api/services-products?limit=5")
        items = list_response.json()["items"]
        
        if not items:
            pytest.skip("No services/products available")
        
        item = items[0]
        
        order_data = {
            "enterprise_id": item["enterprise_id"],
            "items": [{
                "service_product_id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "quantity": 1
            }],
            "delivery_address": "Rue de Test 123, 1000 Lausanne",
            "notes": "TEST_Order - Please ignore"
        }
        
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=self.headers)
        assert response.status_code == 200, f"Create order failed: {response.text}"
        data = response.json()
        assert data["status"] == "pending"
        assert data["total"] == item["price"]
        self.created_order_ids.append(data["id"])
        print(f"✓ Order created: {data['id']} - Total: {data['total']} CHF")
        
        # Verify order appears in list
        orders_response = requests.get(f"{BASE_URL}/api/orders", headers=self.headers)
        assert orders_response.status_code == 200
        orders = orders_response.json()
        assert any(o["id"] == data["id"] for o in orders)
        print(f"✓ Order appears in client orders list")


class TestNotifications:
    """Test notifications system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        # Login as enterprise to check notifications
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_notifications(self):
        """Test getting notifications list"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=self.headers)
        assert response.status_code == 200, f"Get notifications failed: {response.text}"
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        print(f"✓ Notifications retrieved: {len(data['notifications'])} total, {data['unread_count']} unread")
    
    def test_mark_all_read(self):
        """Test marking all notifications as read"""
        response = requests.put(f"{BASE_URL}/api/notifications/read-all", headers=self.headers)
        assert response.status_code == 200, f"Mark all read failed: {response.text}"
        print(f"✓ All notifications marked as read")
        
        # Verify
        check_response = requests.get(f"{BASE_URL}/api/notifications", headers=self.headers)
        data = check_response.json()
        assert data["unread_count"] == 0
        print(f"✓ Unread count is now 0")


class TestImageUpload:
    """Test image upload endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_upload_base64_image(self):
        """Test uploading a base64 image"""
        # Small test image (1x1 red pixel PNG)
        base64_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
        
        response = requests.post(
            f"{BASE_URL}/api/upload/image-base64",
            json={"image": base64_image, "filename": "test_image.png"},
            headers=self.headers
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        assert "url" in data
        print(f"✓ Image uploaded: {data['url']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
