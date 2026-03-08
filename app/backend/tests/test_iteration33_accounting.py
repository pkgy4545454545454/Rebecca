"""
Iteration 33 - Admin Accounting System Tests
Tests for:
- GET /api/admin/accounting/summary - Complete financial data
- GET /api/admin/accounting/transactions - All transaction types with filters
- GET /api/admin/accounting/export/excel - Excel export
- GET /api/admin/accounting/export/pdf - PDF export
- Admin withdrawals management
- Stripe webhook endpoint
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

# Admin credentials
ADMIN_EMAIL = "spa.luxury@titelli.com"
ADMIN_PASSWORD = "Demo123!"

# Test client credentials
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"


class TestAdminAccountingSystem:
    """Test suite for admin accounting endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.admin_token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        else:
            pytest.skip(f"Admin login failed: {response.status_code}")
    
    # ===== ACCOUNTING SUMMARY TESTS =====
    
    def test_accounting_summary_returns_200(self):
        """Test GET /api/admin/accounting/summary returns 200"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/summary")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Accounting summary endpoint returns 200")
    
    def test_accounting_summary_has_revenue_data(self):
        """Test summary contains revenue breakdown"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "revenue" in data, "Missing 'revenue' in response"
        revenue = data["revenue"]
        assert "total_orders_revenue" in revenue, "Missing total_orders_revenue"
        assert "subscription_revenue" in revenue, "Missing subscription_revenue"
        assert "total_revenue" in revenue, "Missing total_revenue"
        
        # Verify values are numeric
        assert isinstance(revenue["total_revenue"], (int, float)), "total_revenue should be numeric"
        print(f"✓ Revenue data: {revenue['total_revenue']:.2f} CHF total")
    
    def test_accounting_summary_has_commissions_data(self):
        """Test summary contains commissions breakdown"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "commissions" in data, "Missing 'commissions' in response"
        commissions = data["commissions"]
        assert "order_commissions_5pct" in commissions, "Missing order_commissions_5pct"
        assert "management_fees" in commissions, "Missing management_fees"
        assert "investment_commissions_12pct" in commissions, "Missing investment_commissions_12pct"
        assert "total_commissions" in commissions, "Missing total_commissions"
        
        print(f"✓ Commissions data: {commissions['total_commissions']:.2f} CHF total")
    
    def test_accounting_summary_has_cashback_data(self):
        """Test summary contains cashback statistics"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "cashback" in data, "Missing 'cashback' in response"
        cashback = data["cashback"]
        assert "total_distributed" in cashback, "Missing total_distributed"
        assert "total_used" in cashback, "Missing total_used"
        assert "total_withdrawn" in cashback, "Missing total_withdrawn"
        assert "net_liability" in cashback, "Missing net_liability"
        
        print(f"✓ Cashback data: {cashback['net_liability']:.2f} CHF liability")
    
    def test_accounting_summary_has_orders_data(self):
        """Test summary contains orders statistics"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "orders" in data, "Missing 'orders' in response"
        orders = data["orders"]
        assert "total_count" in orders, "Missing total_count"
        assert "average_order_value" in orders, "Missing average_order_value"
        assert "by_status" in orders, "Missing by_status"
        
        print(f"✓ Orders data: {orders['total_count']} orders, avg {orders['average_order_value']:.2f} CHF")
    
    def test_accounting_summary_has_subscriptions_data(self):
        """Test summary contains subscriptions data"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "subscriptions" in data, "Missing 'subscriptions' in response"
        subs = data["subscriptions"]
        assert "active_count" in subs, "Missing active_count"
        assert "total_revenue" in subs, "Missing total_revenue"
        
        print(f"✓ Subscriptions data: {subs['active_count']} active")
    
    def test_accounting_summary_has_withdrawals_data(self):
        """Test summary contains withdrawals data"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "withdrawals" in data, "Missing 'withdrawals' in response"
        withdrawals = data["withdrawals"]
        assert "pending_amount" in withdrawals, "Missing pending_amount"
        assert "completed_amount" in withdrawals, "Missing completed_amount"
        
        print(f"✓ Withdrawals data: {withdrawals['pending_amount']:.2f} CHF pending")
    
    def test_accounting_summary_with_date_filter(self):
        """Test summary with date range filter"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/summary", params={
            "start_date": "2024-01-01",
            "end_date": "2025-12-31"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "period" in data, "Missing period info"
        assert data["period"]["start_date"] == "2024-01-01"
        assert data["period"]["end_date"] == "2025-12-31"
        print("✓ Date filter works correctly")
    
    # ===== TRANSACTIONS ENDPOINT TESTS =====
    
    def test_transactions_returns_200(self):
        """Test GET /api/admin/accounting/transactions returns 200"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/transactions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Transactions endpoint returns 200")
    
    def test_transactions_returns_list(self):
        """Test transactions returns list with proper structure"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/transactions")
        assert response.status_code == 200
        data = response.json()
        
        assert "transactions" in data, "Missing 'transactions' in response"
        assert "total" in data, "Missing 'total' in response"
        assert isinstance(data["transactions"], list), "transactions should be a list"
        
        print(f"✓ Transactions list: {data['total']} total transactions")
    
    def test_transactions_structure(self):
        """Test each transaction has required fields"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/transactions", params={"limit": 10})
        assert response.status_code == 200
        data = response.json()
        
        if data["transactions"]:
            tx = data["transactions"][0]
            required_fields = ["id", "type", "date", "description", "amount", "status"]
            for field in required_fields:
                assert field in tx, f"Missing field '{field}' in transaction"
            print(f"✓ Transaction structure valid: {tx['type']} - {tx['description'][:30]}...")
        else:
            print("⚠ No transactions found to validate structure")
    
    def test_transactions_filter_by_order(self):
        """Test filtering transactions by type=order"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/transactions", params={
            "transaction_type": "order"
        })
        assert response.status_code == 200
        data = response.json()
        
        for tx in data["transactions"]:
            assert tx["type"] == "order", f"Expected type 'order', got '{tx['type']}'"
        
        print(f"✓ Order filter works: {len(data['transactions'])} orders")
    
    def test_transactions_filter_by_subscription(self):
        """Test filtering transactions by type=subscription"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/transactions", params={
            "transaction_type": "subscription"
        })
        assert response.status_code == 200
        data = response.json()
        
        for tx in data["transactions"]:
            assert tx["type"] == "subscription", f"Expected type 'subscription', got '{tx['type']}'"
        
        print(f"✓ Subscription filter works: {len(data['transactions'])} subscriptions")
    
    def test_transactions_filter_by_cashback(self):
        """Test filtering transactions by type=cashback"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/transactions", params={
            "transaction_type": "cashback"
        })
        assert response.status_code == 200
        data = response.json()
        
        for tx in data["transactions"]:
            assert tx["type"] == "cashback", f"Expected type 'cashback', got '{tx['type']}'"
        
        print(f"✓ Cashback filter works: {len(data['transactions'])} cashback transactions")
    
    def test_transactions_filter_by_withdrawal(self):
        """Test filtering transactions by type=withdrawal"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/transactions", params={
            "transaction_type": "withdrawal"
        })
        assert response.status_code == 200
        data = response.json()
        
        for tx in data["transactions"]:
            assert tx["type"] == "withdrawal", f"Expected type 'withdrawal', got '{tx['type']}'"
        
        print(f"✓ Withdrawal filter works: {len(data['transactions'])} withdrawals")
    
    def test_transactions_pagination(self):
        """Test transactions pagination"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/transactions", params={
            "limit": 5,
            "skip": 0
        })
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["transactions"]) <= 5, "Limit not respected"
        assert "limit" in data and data["limit"] == 5
        assert "skip" in data and data["skip"] == 0
        
        print(f"✓ Pagination works: {len(data['transactions'])} of {data['total']}")
    
    # ===== EXPORT TESTS =====
    
    def test_export_excel_returns_file(self):
        """Test GET /api/admin/accounting/export/excel returns Excel file"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/export/excel")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheet" in content_type or "excel" in content_type.lower() or "octet-stream" in content_type, \
            f"Expected Excel content type, got: {content_type}"
        
        # Check content disposition
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, "Missing attachment header"
        assert ".xlsx" in content_disp, "Missing .xlsx extension"
        
        # Check file size
        assert len(response.content) > 1000, "Excel file seems too small"
        
        print(f"✓ Excel export works: {len(response.content)} bytes")
    
    def test_export_pdf_returns_file(self):
        """Test GET /api/admin/accounting/export/pdf returns PDF file"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/export/pdf")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "pdf" in content_type.lower() or "octet-stream" in content_type, \
            f"Expected PDF content type, got: {content_type}"
        
        # Check content disposition
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, "Missing attachment header"
        assert ".pdf" in content_disp, "Missing .pdf extension"
        
        # Check file size
        assert len(response.content) > 1000, "PDF file seems too small"
        
        # Check PDF magic bytes
        assert response.content[:4] == b'%PDF', "Not a valid PDF file"
        
        print(f"✓ PDF export works: {len(response.content)} bytes")
    
    def test_export_excel_with_date_filter(self):
        """Test Excel export with date range"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/export/excel", params={
            "start_date": "2024-01-01",
            "end_date": "2025-12-31"
        })
        assert response.status_code == 200
        assert len(response.content) > 1000
        print("✓ Excel export with date filter works")
    
    def test_export_pdf_with_date_filter(self):
        """Test PDF export with date range"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/export/pdf", params={
            "start_date": "2024-01-01",
            "end_date": "2025-12-31"
        })
        assert response.status_code == 200
        assert len(response.content) > 1000
        print("✓ PDF export with date filter works")
    
    # ===== ADMIN WITHDRAWALS TESTS =====
    
    def test_admin_withdrawals_list(self):
        """Test GET /api/admin/withdrawals returns list"""
        response = self.session.get(f"{BASE_URL}/api/admin/withdrawals")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "withdrawals" in data, "Missing 'withdrawals' in response"
        assert "status_counts" in data, "Missing 'status_counts' in response"
        
        print(f"✓ Admin withdrawals list: {len(data['withdrawals'])} withdrawals")
    
    def test_admin_withdrawals_filter_by_status(self):
        """Test filtering withdrawals by status"""
        for status in ["manual_processing", "completed", "failed"]:
            response = self.session.get(f"{BASE_URL}/api/admin/withdrawals", params={"status": status})
            assert response.status_code == 200
            data = response.json()
            
            for w in data["withdrawals"]:
                assert w["status"] == status, f"Expected status '{status}', got '{w['status']}'"
        
        print("✓ Withdrawal status filter works")
    
    # ===== STRIPE WEBHOOK TEST =====
    
    def test_stripe_webhook_endpoint_exists(self):
        """Test POST /api/webhook/stripe endpoint exists"""
        # Send empty body - endpoint should exist and respond
        response = requests.post(f"{BASE_URL}/api/webhook/stripe", data=b"")
        # 200, 400, 422, or 500 are all acceptable - means endpoint exists
        assert response.status_code in [200, 400, 422, 500], f"Unexpected status: {response.status_code}"
        print(f"✓ Stripe webhook endpoint exists (status: {response.status_code})")
    
    # ===== AUTHORIZATION TESTS =====
    
    def test_accounting_requires_admin(self):
        """Test accounting endpoints require admin access"""
        # Login as regular client
        client_session = requests.Session()
        login_resp = client_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        
        if login_resp.status_code == 200:
            client_token = login_resp.json().get("token")
            client_session.headers.update({
                "Authorization": f"Bearer {client_token}",
                "Content-Type": "application/json"
            })
            
            # Try to access accounting summary
            response = client_session.get(f"{BASE_URL}/api/admin/accounting/summary")
            assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
            print("✓ Accounting endpoints properly restricted to admin")
        else:
            pytest.skip("Client login failed")
    
    def test_export_requires_admin(self):
        """Test export endpoints require admin access"""
        # Login as regular client
        client_session = requests.Session()
        login_resp = client_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        
        if login_resp.status_code == 200:
            client_token = login_resp.json().get("token")
            client_session.headers.update({
                "Authorization": f"Bearer {client_token}",
                "Content-Type": "application/json"
            })
            
            # Try to access Excel export
            response = client_session.get(f"{BASE_URL}/api/admin/accounting/export/excel")
            assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
            
            # Try to access PDF export
            response = client_session.get(f"{BASE_URL}/api/admin/accounting/export/pdf")
            assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
            
            print("✓ Export endpoints properly restricted to admin")
        else:
            pytest.skip("Client login failed")


class TestAccountingDataIntegrity:
    """Test data integrity and calculations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.admin_token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_revenue_calculation_consistency(self):
        """Test that total_revenue = orders_revenue + subscription_revenue"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/summary")
        assert response.status_code == 200
        data = response.json()
        
        revenue = data["revenue"]
        calculated_total = revenue["total_orders_revenue"] + revenue["subscription_revenue"]
        
        # Allow small floating point difference
        assert abs(revenue["total_revenue"] - calculated_total) < 0.01, \
            f"Revenue mismatch: {revenue['total_revenue']} != {calculated_total}"
        
        print(f"✓ Revenue calculation consistent: {revenue['total_revenue']:.2f} CHF")
    
    def test_cashback_liability_calculation(self):
        """Test that net_liability = distributed - used - withdrawn"""
        response = self.session.get(f"{BASE_URL}/api/admin/accounting/summary")
        assert response.status_code == 200
        data = response.json()
        
        cashback = data["cashback"]
        calculated_liability = cashback["total_distributed"] - cashback["total_used"] - cashback["total_withdrawn"]
        
        # Allow small floating point difference
        assert abs(cashback["net_liability"] - calculated_liability) < 0.01, \
            f"Cashback liability mismatch: {cashback['net_liability']} != {calculated_liability}"
        
        print(f"✓ Cashback liability calculation consistent: {cashback['net_liability']:.2f} CHF")
    
    def test_transactions_count_matches_summary(self):
        """Test that transaction counts align with summary"""
        # Get summary
        summary_resp = self.session.get(f"{BASE_URL}/api/admin/accounting/summary")
        assert summary_resp.status_code == 200
        summary = summary_resp.json()
        
        # Get order transactions
        orders_resp = self.session.get(f"{BASE_URL}/api/admin/accounting/transactions", params={
            "transaction_type": "order",
            "limit": 10000
        })
        assert orders_resp.status_code == 200
        orders_data = orders_resp.json()
        
        # Compare counts
        summary_orders = summary["orders"]["total_count"]
        tx_orders = orders_data["total"]
        
        assert summary_orders == tx_orders, \
            f"Order count mismatch: summary={summary_orders}, transactions={tx_orders}"
        
        print(f"✓ Order counts match: {summary_orders}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
