"""
Iteration 26 - Comprehensive Notification System Tests
Tests for:
- Notifications CRUD (list, mark read, mark all read, delete)
- Automatic notifications on orders, reviews, trainings, jobs
- Notifications for both client and enterprise users
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"


class TestAuthAndSetup:
    """Authentication tests to get tokens for subsequent tests"""
    
    @pytest.fixture(scope="class")
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Client login failed: {response.text}")
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Enterprise login failed: {response.text}")
        return response.json().get("token")
    
    def test_client_login(self):
        """Test client can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200, f"Client login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "client"
        print(f"✓ Client login successful: {data['user']['email']}")
    
    def test_enterprise_login(self):
        """Test enterprise can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200, f"Enterprise login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "entreprise"
        print(f"✓ Enterprise login successful: {data['user']['email']}")


class TestNotificationsCRUD:
    """Test notification CRUD operations"""
    
    @pytest.fixture(scope="class")
    def client_auth(self):
        """Get client auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Client login failed")
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture(scope="class")
    def enterprise_auth(self):
        """Get enterprise auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Enterprise login failed")
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_client_notifications(self, client_auth):
        """Test GET /api/notifications for client"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=client_auth)
        assert response.status_code == 200, f"Failed to get notifications: {response.text}"
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        assert isinstance(data["notifications"], list)
        assert isinstance(data["unread_count"], int)
        print(f"✓ Client notifications: {len(data['notifications'])} total, {data['unread_count']} unread")
    
    def test_get_enterprise_notifications(self, enterprise_auth):
        """Test GET /api/notifications for enterprise"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=enterprise_auth)
        assert response.status_code == 200, f"Failed to get notifications: {response.text}"
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        print(f"✓ Enterprise notifications: {len(data['notifications'])} total, {data['unread_count']} unread")
    
    def test_get_unread_only_notifications(self, client_auth):
        """Test GET /api/notifications with unread_only filter"""
        response = requests.get(f"{BASE_URL}/api/notifications", 
                               params={"unread_only": True}, 
                               headers=client_auth)
        assert response.status_code == 200
        data = response.json()
        # All returned notifications should be unread
        for notif in data["notifications"]:
            assert notif.get("is_read") == False, "Found read notification in unread_only query"
        print(f"✓ Unread only filter works: {len(data['notifications'])} unread notifications")
    
    def test_mark_notification_read(self, client_auth):
        """Test PUT /api/notifications/{id}/read"""
        # First get notifications
        response = requests.get(f"{BASE_URL}/api/notifications", headers=client_auth)
        assert response.status_code == 200
        notifications = response.json().get("notifications", [])
        
        if not notifications:
            pytest.skip("No notifications to mark as read")
        
        # Find an unread notification or use the first one
        notif_id = notifications[0]["id"]
        
        # Mark as read
        response = requests.put(f"{BASE_URL}/api/notifications/{notif_id}/read", headers=client_auth)
        assert response.status_code == 200, f"Failed to mark notification as read: {response.text}"
        print(f"✓ Marked notification {notif_id[:8]}... as read")
    
    def test_mark_all_notifications_read(self, client_auth):
        """Test PUT /api/notifications/read-all"""
        response = requests.put(f"{BASE_URL}/api/notifications/read-all", headers=client_auth)
        assert response.status_code == 200, f"Failed to mark all as read: {response.text}"
        
        # Verify all are read
        response = requests.get(f"{BASE_URL}/api/notifications", headers=client_auth)
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 0, f"Expected 0 unread, got {data['unread_count']}"
        print("✓ All notifications marked as read")
    
    def test_delete_notification(self, client_auth):
        """Test DELETE /api/notifications/{id}"""
        # First get notifications
        response = requests.get(f"{BASE_URL}/api/notifications", headers=client_auth)
        assert response.status_code == 200
        notifications = response.json().get("notifications", [])
        
        if not notifications:
            pytest.skip("No notifications to delete")
        
        notif_id = notifications[0]["id"]
        initial_count = len(notifications)
        
        # Delete notification
        response = requests.delete(f"{BASE_URL}/api/notifications/{notif_id}", headers=client_auth)
        assert response.status_code == 200, f"Failed to delete notification: {response.text}"
        
        # Verify deletion
        response = requests.get(f"{BASE_URL}/api/notifications", headers=client_auth)
        new_count = len(response.json().get("notifications", []))
        assert new_count == initial_count - 1, "Notification count should decrease by 1"
        print(f"✓ Deleted notification {notif_id[:8]}...")
    
    def test_delete_nonexistent_notification(self, client_auth):
        """Test DELETE /api/notifications/{id} with invalid ID"""
        fake_id = str(uuid.uuid4())
        response = requests.delete(f"{BASE_URL}/api/notifications/{fake_id}", headers=client_auth)
        assert response.status_code == 404, "Should return 404 for nonexistent notification"
        print("✓ Correctly returns 404 for nonexistent notification")


class TestOrderNotifications:
    """Test automatic notifications when creating orders"""
    
    # Known enterprise ID from seed data
    ENTERPRISE_ID = "b34dd7dd-e7ac-4308-83c8-173163ebc819"  # Spa Luxury Lausanne
    
    @pytest.fixture(scope="class")
    def client_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Client login failed")
        token = response.json().get("token")
        user = response.json().get("user")
        return {"headers": {"Authorization": f"Bearer {token}"}, "user": user}
    
    @pytest.fixture(scope="class")
    def enterprise_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Enterprise login failed")
        token = response.json().get("token")
        user = response.json().get("user")
        return {"headers": {"Authorization": f"Bearer {token}"}, "user": user}
    
    def test_order_creates_client_notification(self, client_auth, enterprise_auth):
        """Test that creating an order generates notification for client"""
        # Get initial notification count
        response = requests.get(f"{BASE_URL}/api/notifications", headers=client_auth["headers"])
        initial_count = len(response.json().get("notifications", []))
        
        # Create order using known enterprise ID
        order_data = {
            "enterprise_id": self.ENTERPRISE_ID,
            "items": [
                {
                    "service_product_id": "test-product-1",
                    "name": "TEST_Service Notification Test",
                    "price": 50.0,
                    "quantity": 1
                }
            ],
            "delivery_address": "Test Address",
            "notes": "Test order for notification testing"
        }
        
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=client_auth["headers"])
        assert response.status_code == 200, f"Failed to create order: {response.text}"
        order = response.json()
        print(f"✓ Created order: {order['id'][:8]}...")
        
        # Check client received notification
        response = requests.get(f"{BASE_URL}/api/notifications", headers=client_auth["headers"])
        assert response.status_code == 200
        notifications = response.json().get("notifications", [])
        
        # Find order notification
        order_notifs = [n for n in notifications if n.get("notification_type") in ["order_placed", "cashback_earned"]]
        assert len(order_notifs) > 0, "Client should receive order notification"
        print(f"✓ Client received {len(order_notifs)} order-related notifications")
    
    def test_order_creates_enterprise_notification(self, client_auth, enterprise_auth):
        """Test that creating an order generates notification for enterprise"""
        # Get initial enterprise notification count
        response = requests.get(f"{BASE_URL}/api/notifications", headers=enterprise_auth["headers"])
        initial_notifs = response.json().get("notifications", [])
        
        # Create order using known enterprise ID
        order_data = {
            "enterprise_id": self.ENTERPRISE_ID,
            "items": [
                {
                    "service_product_id": "test-product-2",
                    "name": "TEST_Service Enterprise Notif Test",
                    "price": 75.0,
                    "quantity": 1
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=client_auth["headers"])
        assert response.status_code == 200, f"Failed to create order: {response.text}"
        
        # Check enterprise received notification
        response = requests.get(f"{BASE_URL}/api/notifications", headers=enterprise_auth["headers"])
        assert response.status_code == 200
        new_notifs = response.json().get("notifications", [])
        
        # Find new order notification
        new_order_notifs = [n for n in new_notifs if n.get("notification_type") in ["new_order", "order"]]
        assert len(new_order_notifs) > 0, "Enterprise should receive order notification"
        print(f"✓ Enterprise has {len(new_notifs)} total notifications, {len(new_order_notifs)} order notifications")


class TestReviewNotifications:
    """Test automatic notifications when creating reviews"""
    
    # Known enterprise ID from seed data
    ENTERPRISE_ID = "b34dd7dd-e7ac-4308-83c8-173163ebc819"  # Spa Luxury Lausanne
    
    @pytest.fixture(scope="class")
    def client_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Client login failed")
        return {"Authorization": f"Bearer {response.json().get('token')}"}
    
    @pytest.fixture(scope="class")
    def enterprise_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Enterprise login failed")
        return {"Authorization": f"Bearer {response.json().get('token')}"}
    
    def test_review_creates_enterprise_notification(self, client_auth, enterprise_auth):
        """Test that creating a review generates notification for enterprise"""
        # Create review using known enterprise ID
        review_data = {
            "enterprise_id": self.ENTERPRISE_ID,
            "rating": 5,
            "comment": "TEST_Excellent service for notification testing!"
        }
        
        response = requests.post(f"{BASE_URL}/api/reviews", json=review_data, headers=client_auth)
        assert response.status_code == 200, f"Failed to create review: {response.text}"
        review = response.json()
        print(f"✓ Created review: {review['id'][:8]}...")
        
        # Check enterprise received notification
        response = requests.get(f"{BASE_URL}/api/notifications", headers=enterprise_auth)
        assert response.status_code == 200
        notifications = response.json().get("notifications", [])
        
        # Find review notification
        review_notifs = [n for n in notifications if n.get("notification_type") == "new_review"]
        assert len(review_notifs) > 0, "Enterprise should receive review notification"
        print(f"✓ Enterprise received {len(review_notifs)} review notifications")


class TestTrainingsAPI:
    """Test trainings list and enrollment"""
    
    @pytest.fixture(scope="class")
    def client_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Client login failed")
        return {"Authorization": f"Bearer {response.json().get('token')}"}
    
    def test_list_trainings(self, client_auth):
        """Test GET /api/trainings"""
        response = requests.get(f"{BASE_URL}/api/trainings")
        assert response.status_code == 200, f"Failed to list trainings: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Trainings should be a list"
        print(f"✓ Listed {len(data)} trainings")
    
    def test_get_client_trainings(self, client_auth):
        """Test GET /api/client/trainings"""
        response = requests.get(f"{BASE_URL}/api/client/trainings", headers=client_auth)
        assert response.status_code == 200, f"Failed to get client trainings: {response.text}"
        print("✓ Client trainings endpoint works")


class TestJobsAPI:
    """Test jobs list and applications"""
    
    @pytest.fixture(scope="class")
    def client_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Client login failed")
        return {"Authorization": f"Bearer {response.json().get('token')}"}
    
    @pytest.fixture(scope="class")
    def enterprise_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Enterprise login failed")
        return {"Authorization": f"Bearer {response.json().get('token')}"}
    
    def test_list_jobs(self):
        """Test GET /api/jobs"""
        response = requests.get(f"{BASE_URL}/api/jobs")
        assert response.status_code == 200, f"Failed to list jobs: {response.text}"
        data = response.json()
        # Jobs API returns a list directly
        assert isinstance(data, list), "Response should be a list of jobs"
        print(f"✓ Listed {len(data)} jobs")
    
    def test_get_client_job_applications(self, client_auth):
        """Test GET /api/client/job-applications"""
        response = requests.get(f"{BASE_URL}/api/client/job-applications", headers=client_auth)
        assert response.status_code == 200, f"Failed to get job applications: {response.text}"
        data = response.json()
        assert "applications" in data
        print(f"✓ Client has {len(data['applications'])} job applications")


class TestActivityFeed:
    """Test activity feed for client and enterprise"""
    
    @pytest.fixture(scope="class")
    def client_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Client login failed")
        return {"Authorization": f"Bearer {response.json().get('token')}"}
    
    @pytest.fixture(scope="class")
    def enterprise_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Enterprise login failed")
        return {"Authorization": f"Bearer {response.json().get('token')}"}
    
    def test_client_activity_feed(self, client_auth):
        """Test GET /api/client/activity-feed"""
        response = requests.get(f"{BASE_URL}/api/client/activity-feed", headers=client_auth)
        assert response.status_code == 200, f"Failed to get client activity feed: {response.text}"
        data = response.json()
        assert "activities" in data
        print(f"✓ Client activity feed: {len(data['activities'])} activities")
    
    def test_enterprise_activity_feed(self, enterprise_auth):
        """Test GET /api/enterprise/activity-feed"""
        response = requests.get(f"{BASE_URL}/api/enterprise/activity-feed", headers=enterprise_auth)
        assert response.status_code == 200, f"Failed to get enterprise activity feed: {response.text}"
        data = response.json()
        assert "activities" in data
        print(f"✓ Enterprise activity feed: {len(data['activities'])} activities")


class TestPaymentsAPI:
    """Test payments checkout API"""
    
    @pytest.fixture(scope="class")
    def client_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Client login failed")
        return {"Authorization": f"Bearer {response.json().get('token')}"}
    
    @pytest.fixture(scope="class")
    def enterprise_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Enterprise login failed")
        return {"Authorization": f"Bearer {response.json().get('token')}"}
    
    def test_subscription_checkout_creates_stripe_url(self, enterprise_auth):
        """Test POST /api/subscriptions/checkout for subscription returns valid Stripe URL"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            params={"plan_id": "premium"},
            headers=enterprise_auth
        )
        assert response.status_code == 200, f"Failed to create checkout: {response.text}"
        data = response.json()
        assert "url" in data, "Response should contain Stripe URL"
        assert "session_id" in data, "Response should contain session_id"
        assert data["url"].startswith("https://checkout.stripe.com"), f"URL should be Stripe checkout: {data['url']}"
        print(f"✓ Stripe checkout URL generated: {data['url'][:50]}...")
    
    def test_payment_status_invalid_session(self, client_auth):
        """Test GET /api/payments/status/{session_id} with invalid session"""
        response = requests.get(f"{BASE_URL}/api/payments/status/test123", headers=client_auth)
        assert response.status_code == 200, f"Unexpected status: {response.text}"
        data = response.json()
        # Should return error info for invalid session
        assert data.get("status") == "invalid" or "error" in data or data.get("payment_status") == "not_found"
        print("✓ Invalid session handled correctly")


class TestNotificationTypes:
    """Test that notification types are properly configured"""
    
    @pytest.fixture(scope="class")
    def client_auth(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Client login failed")
        return {"Authorization": f"Bearer {response.json().get('token')}"}
    
    def test_notification_structure(self, client_auth):
        """Test that notifications have proper structure"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=client_auth)
        assert response.status_code == 200
        notifications = response.json().get("notifications", [])
        
        if not notifications:
            pytest.skip("No notifications to verify structure")
        
        # Check first notification has required fields
        notif = notifications[0]
        required_fields = ["id", "user_id", "title", "message", "is_read", "created_at"]
        for field in required_fields:
            assert field in notif, f"Notification missing required field: {field}"
        
        # Check optional but expected fields
        expected_fields = ["notification_type", "link", "data"]
        present_fields = [f for f in expected_fields if f in notif]
        print(f"✓ Notification structure valid. Fields present: {present_fields}")


# Cleanup fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Cleanup TEST_ prefixed data after all tests"""
    yield
    # Note: In production, implement cleanup logic here
    print("\n✓ Test session completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
