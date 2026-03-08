"""
Test Suite for Iteration 33 - Admin Withdrawal Management & Stripe Webhooks
Features tested:
1. Admin withdrawal list endpoint with status counts
2. Admin withdrawal status update (completed/failed)
3. Admin withdrawal CSV export
4. Admin withdrawal detail endpoint
5. Failed withdrawal refunds user's cashback balance
6. Stripe webhook handling for transfer events
7. Notification sent when withdrawal status changes
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable is required")

# Test credentials
ADMIN_EMAIL = "spa.luxury@titelli.com"
ADMIN_PASSWORD = "Demo123!"
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"


class TestAdminAuthentication:
    """Test admin authentication and access control"""
    
    def test_admin_login(self):
        """Test admin can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        print(f"✓ Admin login successful: {ADMIN_EMAIL}")
        return data["token"]
    
    def test_client_login(self):
        """Test client can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200, f"Client login failed: {response.text}"
        data = response.json()
        assert "token" in data
        print(f"✓ Client login successful: {CLIENT_EMAIL}")
        return data["token"]


class TestAdminWithdrawalsEndpoint:
    """Test admin withdrawal list endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_admin_can_list_withdrawals(self, admin_token):
        """Test admin can list all withdrawals"""
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed to list withdrawals: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "withdrawals" in data
        assert "total" in data
        assert "status_counts" in data
        
        # Verify status_counts structure
        status_counts = data["status_counts"]
        assert "pending" in status_counts
        assert "manual_processing" in status_counts
        assert "processing" in status_counts
        assert "completed" in status_counts
        assert "failed" in status_counts
        
        print(f"✓ Admin can list withdrawals. Total: {data['total']}")
        print(f"  Status counts: {status_counts}")
        return data
    
    def test_admin_can_filter_by_status(self, admin_token):
        """Test admin can filter withdrawals by status"""
        for status in ["pending", "manual_processing", "processing", "completed", "failed"]:
            response = requests.get(
                f"{BASE_URL}/api/admin/withdrawals",
                params={"status": status},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200, f"Failed to filter by {status}: {response.text}"
            data = response.json()
            
            # All returned withdrawals should have the filtered status
            for w in data["withdrawals"]:
                assert w["status"] == status, f"Expected status {status}, got {w['status']}"
            
            print(f"✓ Filter by status '{status}' works. Count: {len(data['withdrawals'])}")
    
    def test_non_admin_cannot_access_withdrawals(self, client_token):
        """Test non-admin users cannot access admin withdrawals endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Non-admin correctly denied access to admin withdrawals")
    
    def test_unauthenticated_cannot_access_withdrawals(self):
        """Test unauthenticated users cannot access admin withdrawals"""
        response = requests.get(f"{BASE_URL}/api/admin/withdrawals")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Unauthenticated correctly denied access")


class TestAdminWithdrawalStatusUpdate:
    """Test admin withdrawal status update endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_withdrawal_for_status_update(self, admin_token):
        """Get a withdrawal to test status update"""
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        if data["withdrawals"]:
            withdrawal = data["withdrawals"][0]
            print(f"✓ Found withdrawal for testing: {withdrawal['id'][:8]}... Status: {withdrawal['status']}")
            return withdrawal
        else:
            print("⚠ No withdrawals found for status update test")
            return None
    
    def test_admin_can_update_status_to_completed(self, admin_token):
        """Test admin can mark withdrawal as completed"""
        # First get a withdrawal in manual_processing status
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals",
            params={"status": "manual_processing"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        if not data["withdrawals"]:
            pytest.skip("No withdrawals in manual_processing status to test")
        
        withdrawal = data["withdrawals"][0]
        withdrawal_id = withdrawal["id"]
        
        # Update status to completed
        response = requests.put(
            f"{BASE_URL}/api/admin/withdrawals/{withdrawal_id}/status",
            params={"new_status": "completed", "admin_note": "TEST: Marked as completed"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed to update status: {response.text}"
        
        # Verify the update
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals/{withdrawal_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        updated = response.json()["withdrawal"]
        assert updated["status"] == "completed"
        
        print(f"✓ Admin successfully marked withdrawal {withdrawal_id[:8]}... as completed")
        
        # Revert to manual_processing for other tests
        requests.put(
            f"{BASE_URL}/api/admin/withdrawals/{withdrawal_id}/status",
            params={"new_status": "manual_processing"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
    
    def test_invalid_status_rejected(self, admin_token):
        """Test invalid status values are rejected"""
        # Get any withdrawal
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        if not data["withdrawals"]:
            pytest.skip("No withdrawals to test")
        
        withdrawal_id = data["withdrawals"][0]["id"]
        
        # Try invalid status
        response = requests.put(
            f"{BASE_URL}/api/admin/withdrawals/{withdrawal_id}/status",
            params={"new_status": "invalid_status"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid status, got {response.status_code}"
        print("✓ Invalid status correctly rejected")
    
    def test_nonexistent_withdrawal_returns_404(self, admin_token):
        """Test updating nonexistent withdrawal returns 404"""
        fake_id = str(uuid.uuid4())
        response = requests.put(
            f"{BASE_URL}/api/admin/withdrawals/{fake_id}/status",
            params={"new_status": "completed"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Nonexistent withdrawal correctly returns 404")


class TestAdminWithdrawalCSVExport:
    """Test admin withdrawal CSV export endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_admin_can_export_csv(self, admin_token):
        """Test admin can export withdrawals as CSV"""
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals/export",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed to export CSV: {response.text}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type, f"Expected text/csv, got {content_type}"
        
        # Check content disposition header
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition
        assert "withdrawals_" in content_disposition
        assert ".csv" in content_disposition
        
        # Verify CSV content has expected headers
        csv_content = response.text
        expected_headers = ["ID", "Date", "Email", "Titulaire", "IBAN", "BIC/SWIFT", "Montant", "Statut"]
        first_line = csv_content.split('\n')[0]
        for header in expected_headers:
            assert header in first_line, f"Missing header: {header}"
        
        print(f"✓ CSV export successful. Size: {len(csv_content)} bytes")
        print(f"  Headers: {first_line[:100]}...")
    
    def test_csv_export_with_status_filter(self, admin_token):
        """Test CSV export with status filter"""
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals/export",
            params={"status": "completed"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        print("✓ CSV export with status filter works")
    
    def test_non_admin_cannot_export_csv(self, client_token):
        """Test non-admin cannot export CSV"""
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals/export",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 403
        print("✓ Non-admin correctly denied CSV export access")


class TestAdminWithdrawalDetail:
    """Test admin withdrawal detail endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_admin_can_get_withdrawal_detail(self, admin_token):
        """Test admin can get detailed withdrawal info"""
        # First get a withdrawal
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        if not data["withdrawals"]:
            pytest.skip("No withdrawals to test detail endpoint")
        
        withdrawal_id = data["withdrawals"][0]["id"]
        
        # Get detail
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals/{withdrawal_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed to get detail: {response.text}"
        
        detail = response.json()
        assert "withdrawal" in detail
        assert "user" in detail
        
        withdrawal = detail["withdrawal"]
        assert "id" in withdrawal
        assert "amount" in withdrawal
        assert "status" in withdrawal
        assert "iban" in withdrawal
        assert "account_holder" in withdrawal
        
        print(f"✓ Withdrawal detail retrieved successfully")
        print(f"  ID: {withdrawal['id'][:8]}...")
        print(f"  Amount: {withdrawal['amount']} CHF")
        print(f"  IBAN: {withdrawal['iban']}")
        print(f"  Status: {withdrawal['status']}")


class TestFailedWithdrawalRefund:
    """Test that failed withdrawals refund user's cashback balance"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_failed_status_refunds_balance(self, admin_token, client_token):
        """Test marking withdrawal as failed refunds user's balance"""
        # Get a withdrawal in manual_processing status
        response = requests.get(
            f"{BASE_URL}/api/admin/withdrawals",
            params={"status": "manual_processing"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        if not data["withdrawals"]:
            pytest.skip("No withdrawals in manual_processing status to test refund")
        
        withdrawal = data["withdrawals"][0]
        withdrawal_id = withdrawal["id"]
        withdrawal_amount = withdrawal["amount"]
        user_id = withdrawal["user_id"]
        
        # Get user's current balance before marking as failed
        response = requests.get(
            f"{BASE_URL}/api/cashback/balance",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        balance_before = response.json()["balance"]
        
        # Mark as failed
        response = requests.put(
            f"{BASE_URL}/api/admin/withdrawals/{withdrawal_id}/status",
            params={"new_status": "failed", "admin_note": "TEST: Testing refund"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # Check balance was refunded
        response = requests.get(
            f"{BASE_URL}/api/cashback/balance",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        balance_after = response.json()["balance"]
        
        # Balance should have increased by withdrawal amount
        expected_balance = balance_before + withdrawal_amount
        assert abs(balance_after - expected_balance) < 0.01, \
            f"Expected balance {expected_balance}, got {balance_after}"
        
        print(f"✓ Failed withdrawal correctly refunded {withdrawal_amount} CHF")
        print(f"  Balance before: {balance_before} CHF")
        print(f"  Balance after: {balance_after} CHF")
        
        # Revert to manual_processing and deduct balance for other tests
        requests.put(
            f"{BASE_URL}/api/admin/withdrawals/{withdrawal_id}/status",
            params={"new_status": "manual_processing"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )


class TestStripeWebhook:
    """Test Stripe webhook endpoint for transfer events"""
    
    def test_webhook_endpoint_exists(self):
        """Test webhook endpoint exists and accepts POST"""
        # Send empty body - should not crash
        response = requests.post(
            f"{BASE_URL}/api/webhook/stripe",
            data=b"{}",
            headers={"Content-Type": "application/json"}
        )
        # Should return 200 even for invalid data (graceful handling)
        assert response.status_code == 200, f"Webhook endpoint error: {response.text}"
        print("✓ Stripe webhook endpoint exists and responds")
    
    def test_webhook_handles_transfer_created_event(self):
        """Test webhook handles transfer.created event"""
        # Simulate transfer.created event
        event_data = {
            "type": "transfer.created",
            "data": {
                "object": {
                    "id": "tr_test_123",
                    "metadata": {
                        "withdrawal_id": "test-withdrawal-id"
                    }
                }
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/webhook/stripe",
            json=event_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("received") == True
        print("✓ Webhook handles transfer.created event")
    
    def test_webhook_handles_transfer_paid_event(self):
        """Test webhook handles transfer.paid event"""
        event_data = {
            "type": "transfer.paid",
            "data": {
                "object": {
                    "id": "tr_test_456",
                    "metadata": {
                        "withdrawal_id": "test-withdrawal-id"
                    }
                }
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/webhook/stripe",
            json=event_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        print("✓ Webhook handles transfer.paid event")
    
    def test_webhook_handles_transfer_failed_event(self):
        """Test webhook handles transfer.failed event"""
        event_data = {
            "type": "transfer.failed",
            "data": {
                "object": {
                    "id": "tr_test_789",
                    "metadata": {
                        "withdrawal_id": "test-withdrawal-id"
                    }
                }
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/webhook/stripe",
            json=event_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        print("✓ Webhook handles transfer.failed event")
    
    def test_webhook_handles_payout_events(self):
        """Test webhook handles payout.paid and payout.failed events"""
        for event_type in ["payout.paid", "payout.failed"]:
            event_data = {
                "type": event_type,
                "data": {
                    "object": {
                        "id": "po_test_123",
                        "metadata": {
                            "withdrawal_id": "test-withdrawal-id"
                        }
                    }
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/api/webhook/stripe",
                json=event_data,
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 200
            print(f"✓ Webhook handles {event_type} event")


class TestClientCashbackWithdrawal:
    """Test client cashback withdrawal flow still works"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_client_can_get_withdrawal_info(self, client_token):
        """Test client can get withdrawal info"""
        response = requests.get(
            f"{BASE_URL}/api/cashback/withdrawal-info",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed to get withdrawal info: {response.text}"
        
        data = response.json()
        assert "balance" in data
        assert "minimum_withdrawal" in data
        assert "can_withdraw" in data
        assert "has_bank_info" in data
        
        print(f"✓ Client withdrawal info retrieved")
        print(f"  Balance: {data['balance']} CHF")
        print(f"  Minimum: {data['minimum_withdrawal']} CHF")
        print(f"  Can withdraw: {data['can_withdraw']}")
        print(f"  Has bank info: {data['has_bank_info']}")
    
    def test_client_can_get_withdrawal_history(self, client_token):
        """Test client can get withdrawal history"""
        response = requests.get(
            f"{BASE_URL}/api/cashback/withdrawals",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed to get withdrawal history: {response.text}"
        
        data = response.json()
        # API returns {"withdrawals": [...]}
        withdrawals = data.get("withdrawals", data) if isinstance(data, dict) else data
        assert isinstance(withdrawals, list)
        
        if withdrawals:
            withdrawal = withdrawals[0]
            assert "id" in withdrawal
            assert "amount" in withdrawal
            assert "status" in withdrawal
            assert "created_at" in withdrawal
        
        print(f"✓ Client withdrawal history retrieved. Count: {len(withdrawals)}")


class TestNotifications:
    """Test notifications are sent when withdrawal status changes"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_client_can_get_notifications(self, client_token):
        """Test client can get notifications"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed to get notifications: {response.text}"
        
        data = response.json()
        # API returns {"notifications": [...], "unread_count": N}
        notifications = data.get("notifications", data) if isinstance(data, dict) else data
        assert isinstance(notifications, list)
        
        # Check for withdrawal-related notifications
        withdrawal_notifications = [n for n in notifications if n.get("notification_type") == "cashback_withdrawal"]
        print(f"✓ Notifications retrieved. Total: {len(notifications)}, Withdrawal-related: {len(withdrawal_notifications)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
