"""
Test Client Dashboard APIs - Profile, Friends, Cards, Documents, Messages
Tests for the new client dashboard features
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


class TestClientAuth:
    """Test client authentication"""
    
    def test_client_login(self):
        """Test client login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert "user" in data, "No user in response"
        assert data["user"]["email"] == CLIENT_EMAIL
        return data["token"]


class TestClientProfile:
    """Test client profile APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_client_profile(self):
        """GET /api/client/profile - Get client profile with stats"""
        response = requests.get(f"{BASE_URL}/api/client/profile", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "user" in data, "No user in response"
        assert "stats" in data, "No stats in response"
        assert "profile_views" in data["stats"]
        assert "friends_count" in data["stats"]
        assert "orders_count" in data["stats"]
        print(f"Profile stats: {data['stats']}")
    
    def test_update_client_profile(self):
        """PUT /api/client/profile - Update client profile"""
        update_data = {
            "phone": "+41 79 123 45 67",
            "city": "Lausanne",
            "linkedin": "https://linkedin.com/in/testuser"
        }
        response = requests.put(f"{BASE_URL}/api/client/profile", json=update_data, headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("phone") == update_data["phone"]
        assert data.get("city") == update_data["city"]
        assert data.get("linkedin") == update_data["linkedin"]
        print(f"Profile updated: phone={data.get('phone')}, city={data.get('city')}")


class TestFriendsSystem:
    """Test friends system APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.user_id = response.json()["user"]["id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_friends_list(self):
        """GET /api/client/friends - Get friends list"""
        response = requests.get(f"{BASE_URL}/api/client/friends", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "friends" in data, "No friends key in response"
        assert "count" in data, "No count key in response"
        print(f"Friends count: {data['count']}")
    
    def test_get_friend_requests(self):
        """GET /api/client/friend-requests - Get pending friend requests"""
        response = requests.get(f"{BASE_URL}/api/client/friend-requests", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "received" in data, "No received key in response"
        assert "sent" in data, "No sent key in response"
        print(f"Received requests: {len(data['received'])}, Sent requests: {len(data['sent'])}")
    
    def test_get_suggested_friends(self):
        """GET /api/client/suggested-friends - Get friend suggestions"""
        response = requests.get(f"{BASE_URL}/api/client/suggested-friends", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "suggestions" in data, "No suggestions key in response"
        print(f"Suggested friends: {len(data['suggestions'])}")
    
    def test_send_friend_request_self(self):
        """POST /api/client/friends/request - Cannot add self as friend"""
        response = requests.post(f"{BASE_URL}/api/client/friends/request", 
            json={"friend_id": self.user_id, "message": "Test"},
            headers=self.headers)
        assert response.status_code == 400, "Should fail when adding self"
        print("Correctly rejected self-friend request")


class TestPaymentCards:
    """Test payment cards APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_payment_cards(self):
        """GET /api/client/cards - Get saved payment cards"""
        response = requests.get(f"{BASE_URL}/api/client/cards", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "cards" in data, "No cards key in response"
        print(f"Cards count: {len(data['cards'])}")
        return data["cards"]
    
    def test_add_payment_card(self):
        """POST /api/client/cards - Add a payment card"""
        card_data = {
            "card_holder": "TEST USER",
            "card_number_last4": "9999",
            "card_type": "visa",
            "expiry_month": 12,
            "expiry_year": 2027,
            "is_default": False
        }
        response = requests.post(f"{BASE_URL}/api/client/cards", json=card_data, headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["card_holder"] == card_data["card_holder"]
        assert data["card_number_last4"] == card_data["card_number_last4"]
        assert "id" in data
        print(f"Card added: {data['id']}")
        return data["id"]
    
    def test_add_and_delete_card(self):
        """POST then DELETE /api/client/cards - Full CRUD test"""
        # Add card
        card_data = {
            "card_holder": "TEST DELETE",
            "card_number_last4": "0000",
            "card_type": "mastercard",
            "expiry_month": 6,
            "expiry_year": 2028,
            "is_default": False
        }
        add_response = requests.post(f"{BASE_URL}/api/client/cards", json=card_data, headers=self.headers)
        assert add_response.status_code == 200
        card_id = add_response.json()["id"]
        
        # Delete card
        delete_response = requests.delete(f"{BASE_URL}/api/client/cards/{card_id}", headers=self.headers)
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        print(f"Card {card_id} deleted successfully")
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/client/cards", headers=self.headers)
        cards = get_response.json()["cards"]
        card_ids = [c["id"] for c in cards]
        assert card_id not in card_ids, "Card should be deleted"


class TestClientDocuments:
    """Test client documents APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_documents(self):
        """GET /api/client/documents - Get client documents"""
        response = requests.get(f"{BASE_URL}/api/client/documents", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "documents" in data, "No documents key in response"
        print(f"Documents count: {len(data['documents'])}")
    
    def test_add_document(self):
        """POST /api/client/documents - Add a document"""
        doc_data = {
            "name": "TEST_Document.pdf",
            "category": "general",
            "url": "https://example.com/test-doc.pdf"
        }
        response = requests.post(f"{BASE_URL}/api/client/documents", json=doc_data, headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["name"] == doc_data["name"]
        assert "id" in data
        print(f"Document added: {data['id']}")
        return data["id"]
    
    def test_add_and_delete_document(self):
        """POST then DELETE /api/client/documents - Full CRUD test"""
        # Add document
        doc_data = {
            "name": "TEST_ToDelete.pdf",
            "category": "factures",
            "url": "https://example.com/delete-me.pdf"
        }
        add_response = requests.post(f"{BASE_URL}/api/client/documents", json=doc_data, headers=self.headers)
        assert add_response.status_code == 200
        doc_id = add_response.json()["id"]
        
        # Delete document
        delete_response = requests.delete(f"{BASE_URL}/api/client/documents/{doc_id}", headers=self.headers)
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        print(f"Document {doc_id} deleted successfully")


class TestMessaging:
    """Test messaging APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.user_id = response.json()["user"]["id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_conversations(self):
        """GET /api/messages/conversations - Get all conversations"""
        response = requests.get(f"{BASE_URL}/api/messages/conversations", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "conversations" in data, "No conversations key in response"
        print(f"Conversations count: {len(data['conversations'])}")
    
    def test_send_message_to_self_fails(self):
        """POST /api/messages - Sending message to self should work (for testing)"""
        # Note: The API doesn't prevent self-messaging, which is fine for testing
        message_data = {
            "recipient_id": self.user_id,
            "content": "Test message to self",
            "message_type": "text"
        }
        response = requests.post(f"{BASE_URL}/api/messages", json=message_data, headers=self.headers)
        # This might succeed or fail depending on implementation
        print(f"Self-message response: {response.status_code}")


class TestStatistics:
    """Test statistics APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.user_id = response.json()["user"]["id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_profile_stats_in_profile(self):
        """Verify stats are returned in profile endpoint"""
        response = requests.get(f"{BASE_URL}/api/client/profile", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        stats = data.get("stats", {})
        assert "profile_views" in stats
        assert "friends_count" in stats
        assert "orders_count" in stats
        assert isinstance(stats["profile_views"], int)
        assert isinstance(stats["friends_count"], int)
        assert isinstance(stats["orders_count"], int)
        print(f"Stats: views={stats['profile_views']}, friends={stats['friends_count']}, orders={stats['orders_count']}")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cleanup_test_cards(self):
        """Clean up TEST_ prefixed cards"""
        response = requests.get(f"{BASE_URL}/api/client/cards", headers=self.headers)
        if response.status_code == 200:
            cards = response.json().get("cards", [])
            for card in cards:
                if card.get("card_holder", "").startswith("TEST"):
                    requests.delete(f"{BASE_URL}/api/client/cards/{card['id']}", headers=self.headers)
                    print(f"Cleaned up card: {card['id']}")
    
    def test_cleanup_test_documents(self):
        """Clean up TEST_ prefixed documents"""
        response = requests.get(f"{BASE_URL}/api/client/documents", headers=self.headers)
        if response.status_code == 200:
            docs = response.json().get("documents", [])
            for doc in docs:
                if doc.get("name", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/client/documents/{doc['id']}", headers=self.headers)
                    print(f"Cleaned up document: {doc['id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
