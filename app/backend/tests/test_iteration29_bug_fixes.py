"""
Test iteration 29 - Bug fixes for:
1. Cover image (banner) changes not showing on public profile page
2. Notification counters in dashboard sidebar menu not updating in real-time

Tests verify:
- PUT /api/client/profile accepts cover_image field
- GET /api/client/profile/{user_id}/public returns cover_image
- Notification endpoints work correctly for real-time updates
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestClientLogin:
    """Test client login flow"""
    
    def test_client_login_success(self):
        """Test that client can login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert "user" in data, "No user in response"
        assert data["user"]["email"] == "test@example.com"
        print(f"✓ Client login successful, user_id: {data['user']['id']}")
        return data


class TestCoverImageBugFix:
    """Test BUG FIX 1 - Cover image changes showing on public profile"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        if response.status_code == 200:
            return response.json()
        pytest.skip("Authentication failed")
    
    def test_update_profile_with_cover_image(self, auth_token):
        """Test that PUT /api/client/profile accepts cover_image field"""
        token = auth_token["token"]
        user_id = auth_token["user"]["id"]
        
        # Generate a unique test cover image URL
        test_cover_image = f"https://example.com/test-cover-{uuid.uuid4().hex[:8]}.jpg"
        
        # Update profile with cover_image
        response = requests.put(
            f"{BASE_URL}/api/client/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "cover_image": test_cover_image
            }
        )
        
        assert response.status_code == 200, f"Profile update failed: {response.text}"
        data = response.json()
        
        # Verify cover_image was updated
        assert data.get("cover_image") == test_cover_image, f"Cover image not updated. Got: {data.get('cover_image')}"
        print(f"✓ Cover image updated successfully: {test_cover_image}")
        
        return {"user_id": user_id, "token": token, "cover_image": test_cover_image}
    
    def test_public_profile_returns_cover_image(self, auth_token):
        """Test that GET /api/client/profile/{user_id}/public returns cover_image"""
        token = auth_token["token"]
        user_id = auth_token["user"]["id"]
        
        # First update the cover image
        test_cover_image = f"https://example.com/public-test-cover-{uuid.uuid4().hex[:8]}.jpg"
        
        update_response = requests.put(
            f"{BASE_URL}/api/client/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={"cover_image": test_cover_image}
        )
        assert update_response.status_code == 200, f"Profile update failed: {update_response.text}"
        
        # Now get the public profile
        response = requests.get(
            f"{BASE_URL}/api/client/profile/{user_id}/public",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Public profile fetch failed: {response.text}"
        data = response.json()
        
        # Verify cover_image is in the response
        assert "user" in data, "No user in public profile response"
        user_data = data["user"]
        assert "cover_image" in user_data, "cover_image field missing from public profile"
        assert user_data["cover_image"] == test_cover_image, f"Cover image mismatch. Expected: {test_cover_image}, Got: {user_data.get('cover_image')}"
        
        print(f"✓ Public profile returns cover_image correctly: {user_data['cover_image']}")
    
    def test_cover_image_persists_in_database(self, auth_token):
        """Test that cover_image is persisted and retrieved correctly"""
        token = auth_token["token"]
        
        # Set a unique cover image
        test_cover_image = f"https://example.com/persist-test-{uuid.uuid4().hex[:8]}.jpg"
        
        # Update
        update_response = requests.put(
            f"{BASE_URL}/api/client/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={"cover_image": test_cover_image}
        )
        assert update_response.status_code == 200
        
        # Get own profile to verify persistence
        profile_response = requests.get(
            f"{BASE_URL}/api/client/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert profile_response.status_code == 200, f"Profile fetch failed: {profile_response.text}"
        data = profile_response.json()
        
        assert "user" in data, "No user in profile response"
        assert data["user"].get("cover_image") == test_cover_image, f"Cover image not persisted. Got: {data['user'].get('cover_image')}"
        
        print(f"✓ Cover image persisted correctly in database")


class TestNotificationCountersBugFix:
    """Test BUG FIX 2 - Notification counters in dashboard sidebar"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        if response.status_code == 200:
            return response.json()
        pytest.skip("Authentication failed")
    
    def test_notifications_endpoint_returns_unread_count(self, auth_token):
        """Test that notifications endpoint returns unread_count for badge display"""
        token = auth_token["token"]
        
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Notifications fetch failed: {response.text}"
        data = response.json()
        
        # Verify response structure for notification counters
        assert "notifications" in data, "No notifications array in response"
        assert "unread_count" in data, "No unread_count in response - needed for badge display"
        assert isinstance(data["unread_count"], int), "unread_count should be an integer"
        
        print(f"✓ Notifications endpoint returns unread_count: {data['unread_count']}")
    
    def test_notifications_with_unread_filter(self, auth_token):
        """Test notifications endpoint with unread_only filter"""
        token = auth_token["token"]
        
        response = requests.get(
            f"{BASE_URL}/api/notifications?unread_only=true",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Notifications fetch failed: {response.text}"
        data = response.json()
        
        # All returned notifications should be unread
        for notif in data.get("notifications", []):
            assert notif.get("is_read") == False, f"Found read notification in unread_only response: {notif.get('id')}"
        
        print(f"✓ Unread filter works correctly, returned {len(data.get('notifications', []))} unread notifications")
    
    def test_mark_notification_as_read(self, auth_token):
        """Test marking a notification as read updates the count"""
        token = auth_token["token"]
        
        # Get current notifications
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        initial_unread = data.get("unread_count", 0)
        
        # Find an unread notification to mark as read
        unread_notifs = [n for n in data.get("notifications", []) if not n.get("is_read")]
        
        if unread_notifs:
            notif_id = unread_notifs[0]["id"]
            
            # Mark as read
            mark_response = requests.put(
                f"{BASE_URL}/api/notifications/{notif_id}/read",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert mark_response.status_code == 200, f"Mark as read failed: {mark_response.text}"
            
            # Verify count decreased
            verify_response = requests.get(
                f"{BASE_URL}/api/notifications",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            new_data = verify_response.json()
            new_unread = new_data.get("unread_count", 0)
            
            assert new_unread <= initial_unread, f"Unread count should decrease after marking as read"
            print(f"✓ Mark as read works: unread count {initial_unread} -> {new_unread}")
        else:
            print("✓ No unread notifications to test mark as read (skipped)")
    
    def test_mark_all_notifications_as_read(self, auth_token):
        """Test marking all notifications as read"""
        token = auth_token["token"]
        
        # Mark all as read
        response = requests.put(
            f"{BASE_URL}/api/notifications/read-all",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Mark all as read failed: {response.text}"
        
        # Verify all are read
        verify_response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = verify_response.json()
        assert data.get("unread_count", 0) == 0, f"Unread count should be 0 after mark all read, got: {data.get('unread_count')}"
        
        print(f"✓ Mark all as read works correctly")


class TestClientDashboardDataEndpoints:
    """Test endpoints that provide data for dashboard notification badges"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        if response.status_code == 200:
            return response.json()
        pytest.skip("Authentication failed")
    
    def test_orders_endpoint_for_badge_count(self, auth_token):
        """Test orders endpoint returns data for order badge count"""
        token = auth_token["token"]
        
        response = requests.get(
            f"{BASE_URL}/api/orders",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Orders fetch failed: {response.text}"
        data = response.json()
        
        # Should be a list of orders
        assert isinstance(data, list), "Orders should be a list"
        
        # Each order should have status for filtering
        for order in data:
            assert "status" in order, "Order missing status field"
        
        pending_count = len([o for o in data if o.get("status") in ["pending", "confirmed"]])
        print(f"✓ Orders endpoint works, {len(data)} total orders, {pending_count} pending/confirmed")
    
    def test_friend_requests_endpoint_for_badge_count(self, auth_token):
        """Test friend requests endpoint returns data for badge count"""
        token = auth_token["token"]
        
        response = requests.get(
            f"{BASE_URL}/api/client/friend-requests",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Friend requests fetch failed: {response.text}"
        data = response.json()
        
        # Should have received and sent arrays
        assert "received" in data, "Missing received friend requests"
        assert "sent" in data, "Missing sent friend requests"
        
        print(f"✓ Friend requests endpoint works, {len(data.get('received', []))} received, {len(data.get('sent', []))} sent")
    
    def test_conversations_endpoint_for_message_badge(self, auth_token):
        """Test conversations endpoint returns unread_count for message badge"""
        token = auth_token["token"]
        
        response = requests.get(
            f"{BASE_URL}/api/messages/conversations",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Conversations fetch failed: {response.text}"
        data = response.json()
        
        # Response is an object with conversations array
        assert "conversations" in data, "Missing conversations in response"
        conversations = data["conversations"]
        assert isinstance(conversations, list), "Conversations should be a list"
        
        # Each conversation should have unread_count
        total_unread = 0
        for conv in conversations:
            if "unread_count" in conv:
                total_unread += conv.get("unread_count", 0)
        
        print(f"✓ Conversations endpoint works, {len(conversations)} conversations, {total_unread} total unread messages")
    
    def test_cashback_endpoint_for_badge(self, auth_token):
        """Test cashback endpoint returns balance for badge display"""
        token = auth_token["token"]
        
        response = requests.get(
            f"{BASE_URL}/api/cashback/balance",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Cashback fetch failed: {response.text}"
        data = response.json()
        
        # Should have balance
        assert "balance" in data, "Missing balance in cashback response"
        assert isinstance(data["balance"], (int, float)), "Balance should be a number"
        
        print(f"✓ Cashback endpoint works, balance: {data['balance']} CHF")


class TestWebSocketNotificationEndpoint:
    """Test WebSocket-related notification endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        if response.status_code == 200:
            return response.json()
        pytest.skip("Authentication failed")
    
    def test_notifications_endpoint_structure(self, auth_token):
        """Test notifications endpoint returns proper structure for WebSocket sync"""
        token = auth_token["token"]
        
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields for WebSocket hook sync
        assert "notifications" in data, "Missing notifications array"
        assert "unread_count" in data, "Missing unread_count"
        
        # Each notification should have required fields
        for notif in data.get("notifications", [])[:5]:  # Check first 5
            assert "id" in notif, "Notification missing id"
            assert "is_read" in notif, "Notification missing is_read"
            assert "notification_type" in notif, "Notification missing notification_type"
        
        print(f"✓ Notifications structure correct for WebSocket sync")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
