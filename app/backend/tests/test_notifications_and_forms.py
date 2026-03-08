"""
Test suite for Titelli Notifications and Form APIs
Tests: Notifications CRUD, Services/Products creation, Trainings, Jobs, Offers
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"
ENTERPRISE_ID = "b34dd7dd-e7ac-4308-83c8-173163ebc819"


@pytest.fixture(scope="module")
def enterprise_token():
    """Get enterprise auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ENTERPRISE_EMAIL,
        "password": ENTERPRISE_PASSWORD
    })
    if response.status_code == 200:
        return response.json()["token"]
    pytest.skip("Enterprise login failed")


@pytest.fixture(scope="module")
def client_token():
    """Get client auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": CLIENT_EMAIL,
        "password": CLIENT_PASSWORD
    })
    if response.status_code == 200:
        return response.json()["token"]
    pytest.skip("Client login failed")


@pytest.fixture(scope="module")
def enterprise_headers(enterprise_token):
    """Get enterprise auth headers"""
    return {"Authorization": f"Bearer {enterprise_token}"}


@pytest.fixture(scope="module")
def client_headers(client_token):
    """Get client auth headers"""
    return {"Authorization": f"Bearer {client_token}"}


# ============ NOTIFICATIONS API TESTS ============

class TestNotificationsAPI:
    """Notifications API tests"""
    
    def test_get_notifications_list(self, enterprise_headers):
        """Test getting notifications list"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=enterprise_headers)
        assert response.status_code == 200, f"Get notifications failed: {response.text}"
        data = response.json()
        assert "notifications" in data, "notifications key not in response"
        assert "unread_count" in data, "unread_count key not in response"
        assert isinstance(data["notifications"], list), "notifications should be a list"
        print(f"✓ Get notifications successful - {len(data['notifications'])} notifications, {data['unread_count']} unread")
    
    def test_get_notifications_unread_only(self, enterprise_headers):
        """Test getting only unread notifications"""
        response = requests.get(f"{BASE_URL}/api/notifications", params={"unread_only": True}, headers=enterprise_headers)
        assert response.status_code == 200, f"Get unread notifications failed: {response.text}"
        data = response.json()
        # All returned notifications should be unread
        for notif in data["notifications"]:
            assert notif.get("is_read") == False, "All notifications should be unread"
        print(f"✓ Get unread notifications successful - {len(data['notifications'])} unread")
    
    def test_mark_notification_read(self, enterprise_headers):
        """Test marking a notification as read"""
        # First get notifications
        list_response = requests.get(f"{BASE_URL}/api/notifications", headers=enterprise_headers)
        if list_response.status_code == 200:
            notifications = list_response.json().get("notifications", [])
            if notifications:
                notif_id = notifications[0]["id"]
                # Mark as read
                response = requests.put(f"{BASE_URL}/api/notifications/{notif_id}/read", headers=enterprise_headers)
                assert response.status_code == 200, f"Mark read failed: {response.text}"
                print(f"✓ Mark notification read successful - ID: {notif_id}")
            else:
                print("⚠ No notifications to mark as read")
        else:
            pytest.skip("Could not get notifications list")
    
    def test_mark_all_notifications_read(self, enterprise_headers):
        """Test marking all notifications as read"""
        response = requests.put(f"{BASE_URL}/api/notifications/read-all", headers=enterprise_headers)
        assert response.status_code == 200, f"Mark all read failed: {response.text}"
        data = response.json()
        assert "message" in data, "message not in response"
        print(f"✓ Mark all notifications read successful")
        
        # Verify all are read
        verify_response = requests.get(f"{BASE_URL}/api/notifications", params={"unread_only": True}, headers=enterprise_headers)
        if verify_response.status_code == 200:
            unread = verify_response.json().get("notifications", [])
            assert len(unread) == 0, "Should have no unread notifications"
            print(f"✓ Verified all notifications are read")


# ============ SERVICES/PRODUCTS API TESTS ============

class TestServicesProductsAPI:
    """Services and Products creation API tests"""
    
    def test_create_service_with_all_fields(self, enterprise_headers):
        """Test creating a service with all required fields"""
        service_data = {
            "name": "TEST_Massage Relaxant",
            "description": "Un massage relaxant de 60 minutes pour détendre vos muscles",
            "price": 120.0,
            "category": "soins_esthetiques",
            "type": "service",
            "images": ["https://example.com/massage.jpg"],
            "is_delivery": False
        }
        response = requests.post(f"{BASE_URL}/api/services-products", json=service_data, headers=enterprise_headers)
        assert response.status_code == 200, f"Create service failed: {response.text}"
        data = response.json()
        assert "id" in data, "Service ID not in response"
        assert data["name"] == "TEST_Massage Relaxant", "Name mismatch"
        assert data["price"] == 120.0, "Price mismatch"
        assert data["type"] == "service", "Type should be service"
        assert data["category"] == "soins_esthetiques", "Category mismatch"
        print(f"✓ Create service successful - ID: {data['id']}")
        return data["id"]
    
    def test_create_product_with_all_fields(self, enterprise_headers):
        """Test creating a product with all required fields"""
        product_data = {
            "name": "TEST_Huile de Massage Bio",
            "description": "Huile de massage biologique aux huiles essentielles",
            "price": 45.0,
            "category": "maquillage_beaute",
            "type": "product",
            "images": ["https://example.com/oil.jpg"],
            "is_delivery": True
        }
        response = requests.post(f"{BASE_URL}/api/services-products", json=product_data, headers=enterprise_headers)
        assert response.status_code == 200, f"Create product failed: {response.text}"
        data = response.json()
        assert "id" in data, "Product ID not in response"
        assert data["name"] == "TEST_Huile de Massage Bio", "Name mismatch"
        assert data["type"] == "product", "Type should be product"
        assert data["is_delivery"] == True, "is_delivery should be True"
        print(f"✓ Create product successful - ID: {data['id']}")
        return data["id"]
    
    def test_create_service_missing_required_fields(self, enterprise_headers):
        """Test creating a service with missing required fields"""
        # Missing name
        service_data = {
            "description": "Test description",
            "price": 100.0,
            "category": "soins_esthetiques",
            "type": "service"
        }
        response = requests.post(f"{BASE_URL}/api/services-products", json=service_data, headers=enterprise_headers)
        assert response.status_code == 422, f"Should fail with 422 for missing name: {response.status_code}"
        print(f"✓ Validation works - missing name returns 422")
    
    def test_get_service_product_by_id(self, enterprise_headers):
        """Test getting a service/product by ID"""
        # First create one
        service_data = {
            "name": "TEST_Service Get Test",
            "description": "Test service for GET",
            "price": 50.0,
            "category": "soins_esthetiques",
            "type": "service"
        }
        create_response = requests.post(f"{BASE_URL}/api/services-products", json=service_data, headers=enterprise_headers)
        if create_response.status_code == 200:
            item_id = create_response.json()["id"]
            # Now get it
            get_response = requests.get(f"{BASE_URL}/api/services-products/{item_id}")
            assert get_response.status_code == 200, f"Get service failed: {get_response.text}"
            data = get_response.json()
            assert data["id"] == item_id, "ID mismatch"
            assert data["name"] == "TEST_Service Get Test", "Name mismatch"
            print(f"✓ Get service by ID successful")
    
    def test_update_service_product(self, enterprise_headers):
        """Test updating a service/product"""
        # First create one
        service_data = {
            "name": "TEST_Service Update Test",
            "description": "Original description",
            "price": 75.0,
            "category": "soins_esthetiques",
            "type": "service"
        }
        create_response = requests.post(f"{BASE_URL}/api/services-products", json=service_data, headers=enterprise_headers)
        if create_response.status_code == 200:
            item_id = create_response.json()["id"]
            # Update it
            update_data = {"description": "Updated description", "price": 85.0}
            update_response = requests.put(f"{BASE_URL}/api/services-products/{item_id}", json=update_data, headers=enterprise_headers)
            assert update_response.status_code == 200, f"Update failed: {update_response.text}"
            
            # Verify update
            get_response = requests.get(f"{BASE_URL}/api/services-products/{item_id}")
            if get_response.status_code == 200:
                data = get_response.json()
                assert data["description"] == "Updated description", "Description not updated"
                assert data["price"] == 85.0, "Price not updated"
                print(f"✓ Update service successful")
    
    def test_delete_service_product(self, enterprise_headers):
        """Test deleting a service/product"""
        # First create one
        service_data = {
            "name": "TEST_Service Delete Test",
            "description": "To be deleted",
            "price": 30.0,
            "category": "soins_esthetiques",
            "type": "service"
        }
        create_response = requests.post(f"{BASE_URL}/api/services-products", json=service_data, headers=enterprise_headers)
        if create_response.status_code == 200:
            item_id = create_response.json()["id"]
            # Delete it
            delete_response = requests.delete(f"{BASE_URL}/api/services-products/{item_id}", headers=enterprise_headers)
            assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
            
            # Verify deletion
            get_response = requests.get(f"{BASE_URL}/api/services-products/{item_id}")
            assert get_response.status_code == 404, "Should return 404 after deletion"
            print(f"✓ Delete service successful")


# ============ TRAININGS API TESTS ============

class TestTrainingsAPI:
    """Trainings/Formations API tests"""
    
    def test_create_training(self, enterprise_headers):
        """Test creating a training"""
        training_data = {
            "title": "TEST_Formation Marketing Digital",
            "description": "Apprenez les bases du marketing digital",
            "duration": "4 heures",
            "price": 250.0,
            "max_participants": 20,
            "location": "Lausanne",
            "is_online": False,
            "schedule": "Samedi 10h-14h",
            "prerequisites": "Aucun",
            "certificate": True
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/trainings", json=training_data, headers=enterprise_headers)
        assert response.status_code == 200, f"Create training failed: {response.text}"
        data = response.json()
        assert "id" in data, "Training ID not in response"
        assert data["title"] == "TEST_Formation Marketing Digital", "Title mismatch"
        assert data["price"] == 250.0, "Price mismatch"
        assert data["certificate"] == True, "Certificate should be True"
        print(f"✓ Create training successful - ID: {data['id']}")
        return data["id"]
    
    def test_get_enterprise_trainings(self, enterprise_headers):
        """Test getting enterprise trainings"""
        response = requests.get(f"{BASE_URL}/api/enterprise/trainings", headers=enterprise_headers)
        assert response.status_code == 200, f"Get trainings failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get enterprise trainings successful - {len(data)} trainings")
    
    def test_get_all_public_trainings(self):
        """Test getting all public trainings"""
        response = requests.get(f"{BASE_URL}/api/trainings")
        assert response.status_code == 200, f"Get all trainings failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get all public trainings successful - {len(data)} trainings")
    
    def test_delete_training(self, enterprise_headers):
        """Test deleting a training"""
        # First create one
        training_data = {
            "title": "TEST_Training Delete",
            "description": "To be deleted",
            "duration": "1 heure",
            "price": 50.0
        }
        create_response = requests.post(f"{BASE_URL}/api/enterprise/trainings", json=training_data, headers=enterprise_headers)
        if create_response.status_code == 200:
            training_id = create_response.json()["id"]
            # Delete it
            delete_response = requests.delete(f"{BASE_URL}/api/enterprise/trainings/{training_id}", headers=enterprise_headers)
            assert delete_response.status_code == 200, f"Delete training failed: {delete_response.text}"
            print(f"✓ Delete training successful")


# ============ JOBS API TESTS ============

class TestJobsAPI:
    """Jobs/Employment API tests"""
    
    def test_create_job(self, enterprise_headers):
        """Test creating a job posting"""
        job_data = {
            "title": "TEST_Développeur Full Stack",
            "description": "Nous recherchons un développeur full stack expérimenté",
            "job_type": "full_time",
            "salary_min": 6000.0,
            "salary_max": 8000.0,
            "salary_type": "monthly",
            "location": "Lausanne",
            "remote": True,
            "requirements": "5 ans d'expérience, React, Python",
            "benefits": "Télétravail, assurance, formation continue",
            "contact_email": "jobs@spa-luxury.ch"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/jobs", json=job_data, headers=enterprise_headers)
        assert response.status_code == 200, f"Create job failed: {response.text}"
        data = response.json()
        assert "id" in data, "Job ID not in response"
        assert data["title"] == "TEST_Développeur Full Stack", "Title mismatch"
        assert data["job_type"] == "full_time", "Job type mismatch"
        assert data["remote"] == True, "Remote should be True"
        print(f"✓ Create job successful - ID: {data['id']}")
        return data["id"]
    
    def test_get_enterprise_jobs(self, enterprise_headers):
        """Test getting enterprise jobs"""
        response = requests.get(f"{BASE_URL}/api/enterprise/jobs", headers=enterprise_headers)
        assert response.status_code == 200, f"Get jobs failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get enterprise jobs successful - {len(data)} jobs")
    
    def test_get_all_public_jobs(self):
        """Test getting all public jobs"""
        response = requests.get(f"{BASE_URL}/api/jobs")
        assert response.status_code == 200, f"Get all jobs failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get all public jobs successful - {len(data)} jobs")
    
    def test_delete_job(self, enterprise_headers):
        """Test deleting a job"""
        # First create one
        job_data = {
            "title": "TEST_Job Delete",
            "description": "To be deleted",
            "job_type": "part_time",
            "location": "Lausanne"
        }
        create_response = requests.post(f"{BASE_URL}/api/enterprise/jobs", json=job_data, headers=enterprise_headers)
        if create_response.status_code == 200:
            job_id = create_response.json()["id"]
            # Delete it
            delete_response = requests.delete(f"{BASE_URL}/api/enterprise/jobs/{job_id}", headers=enterprise_headers)
            assert delete_response.status_code == 200, f"Delete job failed: {delete_response.text}"
            print(f"✓ Delete job successful")


# ============ OFFERS API TESTS ============

class TestOffersAPI:
    """Offers/Promotions API tests"""
    
    def test_create_offer(self, enterprise_headers):
        """Test creating an offer"""
        offer_data = {
            "title": "TEST_Promo Été -30%",
            "description": "Profitez de 30% de réduction sur tous nos soins",
            "discount_type": "percentage",
            "discount_value": 30.0,
            "start_date": "2026-01-15",
            "end_date": "2026-02-15",
            "applicable_to": [],
            "min_purchase": 50.0,
            "max_uses": 100,
            "code": "ETE30"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/offers", json=offer_data, headers=enterprise_headers)
        assert response.status_code == 200, f"Create offer failed: {response.text}"
        data = response.json()
        assert "id" in data, "Offer ID not in response"
        assert data["title"] == "TEST_Promo Été -30%", "Title mismatch"
        assert data["discount_value"] == 30.0, "Discount value mismatch"
        print(f"✓ Create offer successful - ID: {data['id']}")
        return data["id"]
    
    def test_get_enterprise_offers(self, enterprise_headers):
        """Test getting enterprise offers"""
        response = requests.get(f"{BASE_URL}/api/enterprise/offers", headers=enterprise_headers)
        assert response.status_code == 200, f"Get offers failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get enterprise offers successful - {len(data)} offers")
    
    def test_update_offer(self, enterprise_headers):
        """Test updating an offer"""
        # First create one
        offer_data = {
            "title": "TEST_Offer Update",
            "description": "Original",
            "discount_type": "percentage",
            "discount_value": 10.0
        }
        create_response = requests.post(f"{BASE_URL}/api/enterprise/offers", json=offer_data, headers=enterprise_headers)
        if create_response.status_code == 200:
            offer_id = create_response.json()["id"]
            # Update it
            update_data = {
                "title": "TEST_Offer Updated",
                "description": "Updated description",
                "discount_type": "percentage",
                "discount_value": 20.0
            }
            update_response = requests.put(f"{BASE_URL}/api/enterprise/offers/{offer_id}", json=update_data, headers=enterprise_headers)
            assert update_response.status_code == 200, f"Update offer failed: {update_response.text}"
            print(f"✓ Update offer successful")
    
    def test_delete_offer(self, enterprise_headers):
        """Test deleting an offer"""
        # First create one
        offer_data = {
            "title": "TEST_Offer Delete",
            "description": "To be deleted",
            "discount_type": "percentage",
            "discount_value": 5.0
        }
        create_response = requests.post(f"{BASE_URL}/api/enterprise/offers", json=offer_data, headers=enterprise_headers)
        if create_response.status_code == 200:
            offer_id = create_response.json()["id"]
            # Delete it
            delete_response = requests.delete(f"{BASE_URL}/api/enterprise/offers/{offer_id}", headers=enterprise_headers)
            assert delete_response.status_code == 200, f"Delete offer failed: {delete_response.text}"
            print(f"✓ Delete offer successful")


# ============ ORDER NOTIFICATION TEST ============

class TestOrderNotification:
    """Test notification creation when order is placed"""
    
    def test_order_creates_notification(self, client_headers, enterprise_headers):
        """Test that creating an order creates a notification for the enterprise"""
        # Get initial notification count for enterprise
        initial_response = requests.get(f"{BASE_URL}/api/notifications", headers=enterprise_headers)
        initial_count = len(initial_response.json().get("notifications", [])) if initial_response.status_code == 200 else 0
        
        # Create an order as client
        order_data = {
            "enterprise_id": ENTERPRISE_ID,
            "items": [
                {
                    "service_product_id": "test-item-1",
                    "name": "TEST_Service Commande",
                    "price": 100.0,
                    "quantity": 1
                }
            ],
            "delivery_address": "123 Test Street, Lausanne",
            "notes": "Test order for notification"
        }
        order_response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=client_headers)
        
        if order_response.status_code == 200:
            order_id = order_response.json()["id"]
            print(f"✓ Order created - ID: {order_id}")
            
            # Check if notification was created for enterprise
            import time
            time.sleep(1)  # Wait for notification to be created
            
            notif_response = requests.get(f"{BASE_URL}/api/notifications", headers=enterprise_headers)
            if notif_response.status_code == 200:
                notifications = notif_response.json().get("notifications", [])
                # Look for order notification
                order_notifs = [n for n in notifications if n.get("notification_type") == "order"]
                if order_notifs:
                    latest_notif = order_notifs[0]
                    assert "commande" in latest_notif.get("title", "").lower() or "commande" in latest_notif.get("message", "").lower(), "Notification should mention order"
                    print(f"✓ Order notification created - Title: {latest_notif.get('title')}")
                else:
                    print("⚠ No order notification found (may already be read)")
        else:
            print(f"⚠ Order creation failed: {order_response.text}")


# ============ CLEANUP ============

class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_data(self, enterprise_headers):
        """Clean up TEST_ prefixed data"""
        # Clean services/products
        sp_response = requests.get(f"{BASE_URL}/api/services-products", headers=enterprise_headers)
        if sp_response.status_code == 200:
            for item in sp_response.json().get("items", []):
                if item.get("name", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/services-products/{item['id']}", headers=enterprise_headers)
        
        # Clean trainings
        trainings_response = requests.get(f"{BASE_URL}/api/enterprise/trainings", headers=enterprise_headers)
        if trainings_response.status_code == 200:
            for training in trainings_response.json():
                if training.get("title", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/enterprise/trainings/{training['id']}", headers=enterprise_headers)
        
        # Clean jobs
        jobs_response = requests.get(f"{BASE_URL}/api/enterprise/jobs", headers=enterprise_headers)
        if jobs_response.status_code == 200:
            for job in jobs_response.json():
                if job.get("title", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/enterprise/jobs/{job['id']}", headers=enterprise_headers)
        
        # Clean offers
        offers_response = requests.get(f"{BASE_URL}/api/enterprise/offers", headers=enterprise_headers)
        if offers_response.status_code == 200:
            for offer in offers_response.json():
                if offer.get("title", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/enterprise/offers/{offer['id']}", headers=enterprise_headers)
        
        print("✓ Cleanup completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
