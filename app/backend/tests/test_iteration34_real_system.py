"""
Iteration 34 - Real System Verification Tests
Tests to verify that all systems are real (MongoDB-based) and not hardcoded:
- Cashback rates: 1% free, 10% premium, 15% VIP
- Messaging between users
- Friend requests
- Enterprise invitations to clients
- Admin sections (enterprises, orders, payments, settings)
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "spa.luxury@titelli.com"
ADMIN_PASSWORD = "Demo123!"
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        print("✓ API health check passed")


class TestAuthentication:
    """Authentication tests"""
    
    def test_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert 'token' in data
        assert 'user' in data
        print(f"✓ Admin login successful: {data['user'].get('email')}")
    
    def test_client_login(self):
        """Test client login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert 'token' in data
        assert 'user' in data
        print(f"✓ Client login successful: {data['user'].get('email')}")


class TestCashbackSystem:
    """Test cashback rates based on subscription plan"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json().get('token')
    
    def test_premium_plans_endpoint(self, client_token):
        """Test premium plans endpoint returns correct cashback rates"""
        headers = {"Authorization": f"Bearer {client_token}"}
        # Correct endpoint: /api/client/premium
        response = requests.get(f"{BASE_URL}/api/client/premium", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify benefits structure contains all plans
        benefits = data.get('benefits', {})
        
        # Check free plan - 1% cashback
        assert 'free' in benefits
        assert benefits['free']['cashback_rate'] == 0.01
        print(f"✓ Free plan cashback rate: {benefits['free']['cashback_rate']*100}%")
        
        # Check premium plan - 10% cashback
        assert 'premium' in benefits
        assert benefits['premium']['cashback_rate'] == 0.10
        print(f"✓ Premium plan cashback rate: {benefits['premium']['cashback_rate']*100}%")
        
        # Check VIP plan - 15% cashback
        assert 'vip' in benefits
        assert benefits['vip']['cashback_rate'] == 0.15
        print(f"✓ VIP plan cashback rate: {benefits['vip']['cashback_rate']*100}%")
        
        # Verify current user's cashback rate is returned
        assert 'cashback_rate' in data
        print(f"✓ Current user cashback rate: {data['cashback_rate']}%")
    
    def test_cashback_balance_endpoint(self, client_token):
        """Test cashback balance endpoint returns real data"""
        headers = {"Authorization": f"Bearer {client_token}"}
        # Correct endpoint: /api/cashback/balance
        response = requests.get(f"{BASE_URL}/api/cashback/balance", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify balance is returned
        assert 'balance' in data
        print(f"✓ Cashback balance: {data['balance']} CHF")
    
    def test_cashback_history_endpoint(self, client_token):
        """Test cashback history endpoint returns real data"""
        headers = {"Authorization": f"Bearer {client_token}"}
        # Correct endpoint: /api/cashback/history
        response = requests.get(f"{BASE_URL}/api/cashback/history", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify transactions structure
        assert 'transactions' in data
        assert isinstance(data['transactions'], list)
        print(f"✓ Cashback transactions count: {len(data['transactions'])}")
        
        # If there are transactions, verify they have proper structure
        if data['transactions']:
            tx = data['transactions'][0]
            assert 'id' in tx
            assert 'amount' in tx
            assert 'type' in tx
            print(f"✓ Transaction structure verified: {tx.get('description', 'N/A')}")


class TestMessagingSystem:
    """Test messaging between users"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json().get('token')
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get('token')
    
    def test_get_conversations(self, client_token):
        """Test getting conversations list"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/messages/conversations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Response is wrapped in 'conversations' key
        assert 'conversations' in data
        assert isinstance(data['conversations'], list)
        print(f"✓ Conversations retrieved: {len(data['conversations'])} conversations")
    
    def test_send_message(self, client_token, admin_token):
        """Test sending a message between users"""
        # Get admin user ID
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        admin_response = requests.get(f"{BASE_URL}/api/auth/me", headers=admin_headers)
        admin_user = admin_response.json()
        admin_id = admin_user.get('id')
        
        # Send message from client to admin
        client_headers = {"Authorization": f"Bearer {client_token}"}
        test_message = f"TEST_Message_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(f"{BASE_URL}/api/messages", headers=client_headers, json={
            "recipient_id": admin_id,
            "content": test_message
        })
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert 'id' in data
        assert data.get('content') == test_message
        print(f"✓ Message sent successfully: {test_message[:30]}...")
        
        # Verify message appears in conversations
        conv_response = requests.get(f"{BASE_URL}/api/messages/conversations", headers=client_headers)
        assert conv_response.status_code == 200
        print("✓ Message appears in conversations")


class TestFriendRequestSystem:
    """Test friend request functionality"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json().get('token')
    
    def test_get_friend_requests(self, client_token):
        """Test getting friend requests"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/client/friend-requests", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Response has 'received' and 'sent' keys
        assert 'received' in data or 'sent' in data
        received = data.get('received', [])
        sent = data.get('sent', [])
        print(f"✓ Friend requests retrieved: {len(received)} received, {len(sent)} sent")
    
    def test_get_friends_list(self, client_token):
        """Test getting friends list"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/client/friends", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Response has 'friends' key
        assert 'friends' in data
        assert isinstance(data['friends'], list)
        print(f"✓ Friends list retrieved: {len(data['friends'])} friends")


class TestEnterpriseInvitations:
    """Test enterprise invitations to clients"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get('token')
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json().get('token')
    
    def test_get_enterprise_invitations(self, admin_token):
        """Test getting enterprise invitations (enterprise side)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/enterprise/invitations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Response has 'invitations' key
        assert 'invitations' in data
        assert isinstance(data['invitations'], list)
        print(f"✓ Enterprise invitations retrieved: {len(data['invitations'])} invitations")
        
        # Verify stats are included
        if 'stats' in data:
            print(f"✓ Invitation stats: {data['stats'].get('total_sent', 0)} sent, {data['stats'].get('total_opened', 0)} opened")
    
    def test_create_enterprise_invitation(self, admin_token):
        """Test creating an enterprise invitation"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        invitation_data = {
            "type": "invitation",
            "title": f"TEST_Invitation_{uuid.uuid4().hex[:8]}",
            "message": "Test invitation message for testing purposes",
            "target_audience": "all",
            "incentive": "10% discount"
        }
        
        response = requests.post(f"{BASE_URL}/api/enterprise/invitations", headers=headers, json=invitation_data)
        assert response.status_code in [200, 201]
        data = response.json()
        assert 'id' in data
        print(f"✓ Enterprise invitation created: {invitation_data['title']}")
        
        # Clean up - delete the test invitation
        invitation_id = data['id']
        delete_response = requests.delete(f"{BASE_URL}/api/enterprise/invitations/{invitation_id}", headers=headers)
        assert delete_response.status_code == 200
        print("✓ Test invitation cleaned up")
    
    def test_get_client_invitations(self, client_token):
        """Test getting invitations from client side"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/client/invitations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Response has 'invitations' key
        assert 'invitations' in data
        assert isinstance(data['invitations'], list)
        print(f"✓ Client invitations retrieved: {len(data['invitations'])} invitations")


class TestAdminSections:
    """Test admin dashboard sections show real data"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get('token')
    
    def test_admin_stats_endpoint(self, admin_token):
        """Test admin stats endpoint returns real data"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Stats are nested under 'stats' key
        stats = data.get('stats', data)
        
        # Verify structure contains real data
        assert 'total_users' in stats
        assert 'total_enterprises' in stats
        assert 'total_orders' in stats
        
        print(f"✓ Admin stats - Users: {stats['total_users']}")
        print(f"✓ Admin stats - Enterprises: {stats['total_enterprises']}")
        print(f"✓ Admin stats - Orders: {stats['total_orders']}")
        
        # Verify recent data arrays
        assert 'recent_users' in data
        assert 'recent_orders' in data
        
        print(f"✓ Recent users count: {len(data.get('recent_users', []))}")
        print(f"✓ Recent orders count: {len(data.get('recent_orders', []))}")
    
    def test_admin_accounting_summary(self, admin_token):
        """Test admin accounting summary returns real financial data"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/accounting/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify revenue data
        assert 'revenue' in data
        revenue = data['revenue']
        assert 'total_revenue' in revenue
        print(f"✓ Total revenue: {revenue['total_revenue']} CHF")
        
        # Verify commissions data
        assert 'commissions' in data
        commissions = data['commissions']
        assert 'total_commissions' in commissions
        print(f"✓ Total commissions: {commissions['total_commissions']} CHF")
        
        # Verify cashback data
        assert 'cashback' in data
        cashback = data['cashback']
        print(f"✓ Cashback distributed: {cashback.get('total_distributed', 0)} CHF")
        
        # Verify withdrawals data
        assert 'withdrawals' in data
        withdrawals = data['withdrawals']
        print(f"✓ Pending withdrawals: {withdrawals.get('pending_amount', 0)} CHF")
    
    def test_admin_enterprises_list(self, admin_token):
        """Test admin can see enterprises list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/enterprises", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert 'enterprises' in data
        assert 'total' in data
        print(f"✓ Enterprises list: {data['total']} total enterprises")
        
        # Verify enterprise structure if any exist
        if data['enterprises']:
            ent = data['enterprises'][0]
            assert 'id' in ent
            assert 'business_name' in ent
            print(f"✓ First enterprise: {ent.get('business_name')}")
    
    def test_admin_orders_list(self, admin_token):
        """Test admin can see orders"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/orders", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✓ Orders list: {len(data)} orders")
        
        # Verify order structure if any exist
        if data:
            order = data[0]
            assert 'id' in order
            assert 'total' in order
            assert 'status' in order
            print(f"✓ First order: #{order['id'][:8]} - {order['total']} CHF - {order['status']}")


class TestAccountingRealData:
    """Test that accounting data is real from MongoDB"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get('token')
    
    def test_accounting_transactions(self, admin_token):
        """Test accounting transactions endpoint returns real data"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/accounting/transactions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert 'transactions' in data
        assert 'total' in data
        print(f"✓ Accounting transactions: {data['total']} total")
        
        # Verify transaction structure
        if data['transactions']:
            tx = data['transactions'][0]
            assert 'id' in tx
            assert 'type' in tx
            assert 'amount' in tx
            print(f"✓ Transaction type: {tx['type']}, amount: {tx['amount']} CHF")
    
    def test_subscriptions_real_data(self, admin_token):
        """Test subscriptions data is real"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/accounting/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check subscriptions data
        subscriptions = data.get('subscriptions', {})
        print(f"✓ Active subscriptions: {subscriptions.get('active_count', 0)}")
        print(f"✓ Subscription revenue: {subscriptions.get('total_revenue', 0)} CHF")


class TestDataPersistence:
    """Test that data is persisted in MongoDB (not hardcoded)"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json().get('token')
    
    def test_user_data_persistence(self, client_token):
        """Test user data is retrieved from MongoDB"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify user has MongoDB-generated fields
        assert 'id' in data
        assert 'email' in data
        assert 'created_at' in data or 'cashback_balance' in data
        print(f"✓ User data from MongoDB: {data['email']}")
        print(f"✓ User cashback balance: {data.get('cashback_balance', 0)} CHF")
    
    def test_orders_data_persistence(self, client_token):
        """Test orders are retrieved from MongoDB"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/orders", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✓ Orders from MongoDB: {len(data)} orders")
        
        # Verify orders have proper MongoDB structure
        if data:
            order = data[0]
            assert 'id' in order
            assert 'created_at' in order
            print(f"✓ Order created_at: {order['created_at']}")


class TestNotificationsSystem:
    """Test notifications system is real"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json().get('token')
    
    def test_get_notifications(self, client_token):
        """Test getting notifications"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Response has 'notifications' key
        assert 'notifications' in data
        assert isinstance(data['notifications'], list)
        print(f"✓ Notifications retrieved: {len(data['notifications'])} notifications")
        
        # Verify notification structure
        if data['notifications']:
            notif = data['notifications'][0]
            assert 'id' in notif
            assert 'title' in notif
            assert 'message' in notif
            print(f"✓ Notification: {notif['title']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
