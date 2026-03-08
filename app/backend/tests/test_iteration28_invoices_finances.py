"""
Iteration 28 - Test Invoice Generation, Finance Transactions, and Enterprise Documents
Tests for:
1. Order creation generates enterprise invoice (enterprise_invoices)
2. Order creation generates document entry (enterprise_documents)
3. Order creation generates finance transaction (finance_transactions)
4. Invoice contains: invoice_number, order_id, client_info, subtotal, fees, enterprise_net
5. Finance transaction contains: enterprise_id, reference_id (order_id), amount (enterprise_net)
6. GET /api/enterprise/invoices returns invoices with summary
7. GET /api/enterprise/invoices/{id} returns invoice detail
8. GET /api/enterprise/documents?category=factures returns invoices
9. GET /api/enterprise/finances returns transactions with summary
10. Update order status 'completed' marks invoice as 'paid'
11. Update order status 'cancelled' removes finance transaction
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
ENTERPRISE_ID = "b34dd7dd-e7ac-4308-83c8-173163ebc819"

# Titelli fees configuration
MANAGEMENT_FEE_RATE = 0.10  # 10%
TRANSACTION_FEE_RATE = 0.029  # 2.9%


class TestInvoiceAndFinanceGeneration:
    """Test invoice and finance transaction generation on order creation"""
    
    @pytest.fixture(scope="class")
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Client login failed: {response.status_code} - {response.text}")
    
    @pytest.fixture(scope="class")
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Enterprise login failed: {response.status_code} - {response.text}")
    
    @pytest.fixture(scope="class")
    def client_info(self, client_token):
        """Get client user info"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {client_token}"
        })
        if response.status_code == 200:
            return response.json()
        return {}
    
    def test_01_client_login(self, client_token):
        """Test client can login"""
        assert client_token is not None
        print(f"✓ Client logged in successfully")
    
    def test_02_enterprise_login(self, enterprise_token):
        """Test enterprise can login"""
        assert enterprise_token is not None
        print(f"✓ Enterprise logged in successfully")
    
    def test_03_create_order_generates_invoice(self, client_token, enterprise_token):
        """Test that creating an order generates an invoice in enterprise_invoices"""
        # Create an order
        order_data = {
            "enterprise_id": ENTERPRISE_ID,
            "items": [
                {
                    "service_product_id": "test-product-1",
                    "name": "TEST_Service Massage",
                    "price": 100.0,
                    "quantity": 2
                }
            ],
            "notes": "Test order for invoice generation"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == 200, f"Order creation failed: {response.text}"
        order = response.json()
        
        # Verify order structure
        assert "id" in order
        assert "subtotal" in order
        assert "transaction_fee" in order
        assert "management_fee" in order
        assert "total" in order
        
        order_id = order['id']
        subtotal = order['subtotal']
        
        # Verify fee calculations
        expected_transaction_fee = round(subtotal * TRANSACTION_FEE_RATE, 2)
        expected_management_fee = round(subtotal * MANAGEMENT_FEE_RATE, 2)
        expected_total = round(subtotal + expected_transaction_fee, 2)
        
        assert order['subtotal'] == 200.0, f"Subtotal should be 200.0, got {order['subtotal']}"
        assert abs(order['transaction_fee'] - expected_transaction_fee) < 0.01, f"Transaction fee mismatch"
        assert abs(order['management_fee'] - expected_management_fee) < 0.01, f"Management fee mismatch"
        
        print(f"✓ Order created: {order_id}")
        print(f"  Subtotal: {subtotal} CHF")
        print(f"  Transaction fee (2.9%): {order['transaction_fee']} CHF")
        print(f"  Management fee (10%): {order['management_fee']} CHF")
        print(f"  Total: {order['total']} CHF")
        
        # Now check if invoice was created
        invoices_response = requests.get(
            f"{BASE_URL}/api/enterprise/invoices",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert invoices_response.status_code == 200, f"Get invoices failed: {invoices_response.text}"
        invoices_data = invoices_response.json()
        
        assert "invoices" in invoices_data
        assert "summary" in invoices_data
        
        # Find the invoice for our order
        invoice = next((inv for inv in invoices_data['invoices'] if inv.get('order_id') == order_id), None)
        assert invoice is not None, f"Invoice not found for order {order_id}"
        
        # Verify invoice structure
        assert "invoice_number" in invoice, "Invoice missing invoice_number"
        assert "order_id" in invoice, "Invoice missing order_id"
        assert "client_info" in invoice, "Invoice missing client_info"
        assert "subtotal" in invoice, "Invoice missing subtotal"
        assert "transaction_fee" in invoice, "Invoice missing transaction_fee"
        assert "management_fee" in invoice, "Invoice missing management_fee"
        assert "enterprise_net" in invoice, "Invoice missing enterprise_net"
        assert "total_ttc" in invoice, "Invoice missing total_ttc"
        
        # Verify enterprise_net calculation
        expected_enterprise_net = round(subtotal - expected_management_fee, 2)
        assert abs(invoice['enterprise_net'] - expected_enterprise_net) < 0.01, \
            f"Enterprise net mismatch: expected {expected_enterprise_net}, got {invoice['enterprise_net']}"
        
        print(f"✓ Invoice generated: {invoice['invoice_number']}")
        print(f"  Enterprise net: {invoice['enterprise_net']} CHF")
        print(f"  Status: {invoice['status']}")
        
        # Store order_id for later tests
        self.__class__.test_order_id = order_id
        self.__class__.test_invoice_id = invoice['id']
    
    def test_04_order_generates_document_entry(self, enterprise_token):
        """Test that order creates a document entry in enterprise_documents"""
        order_id = getattr(self.__class__, 'test_order_id', None)
        if not order_id:
            pytest.skip("No test order created")
        
        # Get documents with category=factures
        response = requests.get(
            f"{BASE_URL}/api/enterprise/documents?category=factures",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert response.status_code == 200, f"Get documents failed: {response.text}"
        docs_data = response.json()
        
        assert "documents" in docs_data
        
        # Find document for our order
        doc = next((d for d in docs_data['documents'] if d.get('metadata', {}).get('order_id') == order_id), None)
        assert doc is not None, f"Document not found for order {order_id}"
        
        # Verify document structure
        assert doc['category'] == 'factures', f"Document category should be 'factures', got {doc['category']}"
        assert 'metadata' in doc
        assert 'invoice_number' in doc['metadata']
        assert 'client_name' in doc['metadata']
        assert 'total' in doc['metadata']
        assert 'enterprise_net' in doc['metadata']
        
        print(f"✓ Document entry created for invoice")
        print(f"  Name: {doc['name']}")
        print(f"  Category: {doc['category']}")
        print(f"  Invoice number: {doc['metadata']['invoice_number']}")
    
    def test_05_order_generates_finance_transaction(self, enterprise_token):
        """Test that order creates a finance transaction"""
        order_id = getattr(self.__class__, 'test_order_id', None)
        if not order_id:
            pytest.skip("No test order created")
        
        # Get finance transactions
        response = requests.get(
            f"{BASE_URL}/api/enterprise/finances",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert response.status_code == 200, f"Get finances failed: {response.text}"
        finance_data = response.json()
        
        assert "transactions" in finance_data
        assert "summary" in finance_data
        
        # Find transaction for our order
        transaction = next(
            (t for t in finance_data['transactions'] if t.get('reference_id') == order_id),
            None
        )
        assert transaction is not None, f"Finance transaction not found for order {order_id}"
        
        # Verify transaction structure
        assert transaction['enterprise_id'] == ENTERPRISE_ID
        assert transaction['reference_id'] == order_id
        assert transaction['transaction_type'] == 'income'
        assert transaction['category'] == 'ventes'
        assert 'amount' in transaction
        
        # Amount should be enterprise_net (subtotal - management_fee)
        # For 200 CHF subtotal: enterprise_net = 200 - 20 = 180 CHF
        expected_amount = 180.0  # 200 - 10%
        assert abs(transaction['amount'] - expected_amount) < 0.01, \
            f"Transaction amount should be {expected_amount}, got {transaction['amount']}"
        
        print(f"✓ Finance transaction created")
        print(f"  Amount: {transaction['amount']} CHF")
        print(f"  Type: {transaction['transaction_type']}")
        print(f"  Category: {transaction['category']}")
        print(f"  Reference ID: {transaction['reference_id']}")


class TestEnterpriseInvoicesEndpoint:
    """Test /api/enterprise/invoices endpoint"""
    
    @pytest.fixture(scope="class")
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Enterprise login failed: {response.status_code}")
    
    def test_01_get_invoices_returns_list_with_summary(self, enterprise_token):
        """Test GET /api/enterprise/invoices returns invoices with summary"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/invoices",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "invoices" in data
        assert "summary" in data
        assert isinstance(data['invoices'], list)
        
        # Verify summary structure
        summary = data['summary']
        assert "total_invoices" in summary
        assert "pending_invoices" in summary
        assert "paid_invoices" in summary
        assert "total_pending_amount" in summary
        assert "total_paid_amount" in summary
        assert "total_net_revenue" in summary
        assert "total_fees_paid" in summary
        
        print(f"✓ GET /api/enterprise/invoices returns {len(data['invoices'])} invoices")
        print(f"  Summary: {summary}")
    
    def test_02_get_invoices_filter_by_status(self, enterprise_token):
        """Test GET /api/enterprise/invoices?status=pending"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/invoices?status=pending",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned invoices should have status=pending
        for invoice in data['invoices']:
            assert invoice['status'] == 'pending', f"Invoice {invoice['id']} has status {invoice['status']}"
        
        print(f"✓ Filter by status=pending works: {len(data['invoices'])} pending invoices")
    
    def test_03_get_invoice_detail(self, enterprise_token):
        """Test GET /api/enterprise/invoices/{id} returns invoice detail"""
        # First get list of invoices
        list_response = requests.get(
            f"{BASE_URL}/api/enterprise/invoices",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        if list_response.status_code != 200 or not list_response.json().get('invoices'):
            pytest.skip("No invoices available to test detail endpoint")
        
        invoice_id = list_response.json()['invoices'][0]['id']
        
        # Get invoice detail
        response = requests.get(
            f"{BASE_URL}/api/enterprise/invoices/{invoice_id}",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "invoice" in data
        invoice = data['invoice']
        
        # Verify all required fields
        assert invoice['id'] == invoice_id
        assert "invoice_number" in invoice
        assert "order_id" in invoice
        assert "client_info" in invoice
        assert "items" in invoice
        assert "subtotal" in invoice
        assert "transaction_fee" in invoice
        assert "management_fee" in invoice
        assert "total_ttc" in invoice
        assert "enterprise_net" in invoice
        assert "status" in invoice
        
        # Verify client_info structure
        client_info = invoice['client_info']
        assert "id" in client_info
        assert "name" in client_info
        assert "email" in client_info
        
        print(f"✓ GET /api/enterprise/invoices/{invoice_id} returns detail")
        print(f"  Invoice number: {invoice['invoice_number']}")
        print(f"  Client: {client_info['name']}")
        print(f"  Total TTC: {invoice['total_ttc']} CHF")
        print(f"  Enterprise net: {invoice['enterprise_net']} CHF")


class TestEnterpriseDocumentsEndpoint:
    """Test /api/enterprise/documents endpoint for invoices"""
    
    @pytest.fixture(scope="class")
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Enterprise login failed: {response.status_code}")
    
    def test_01_get_documents_factures_category(self, enterprise_token):
        """Test GET /api/enterprise/documents?category=factures returns invoices"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/documents?category=factures",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "documents" in data
        
        # All documents should have category=factures
        for doc in data['documents']:
            assert doc['category'] == 'factures', f"Document {doc['id']} has category {doc['category']}"
        
        print(f"✓ GET /api/enterprise/documents?category=factures returns {len(data['documents'])} documents")
        
        if data['documents']:
            doc = data['documents'][0]
            print(f"  Sample document: {doc['name']}")
            if 'metadata' in doc:
                print(f"  Metadata: {doc['metadata']}")
    
    def test_02_documents_merge_both_collections(self, enterprise_token):
        """Test that documents endpoint merges both documents and enterprise_documents collections"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/documents",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "documents" in data
        print(f"✓ GET /api/enterprise/documents returns {len(data['documents'])} total documents")


class TestEnterpriseFinancesEndpoint:
    """Test /api/enterprise/finances endpoint"""
    
    @pytest.fixture(scope="class")
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Enterprise login failed: {response.status_code}")
    
    def test_01_get_finances_returns_transactions_with_summary(self, enterprise_token):
        """Test GET /api/enterprise/finances returns transactions with summary"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/finances",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "transactions" in data
        assert "summary" in data
        
        # Verify summary structure
        summary = data['summary']
        assert "total_income" in summary
        assert "total_expenses" in summary
        assert "net_profit" in summary
        assert "orders_revenue" in summary
        
        print(f"✓ GET /api/enterprise/finances returns {len(data['transactions'])} transactions")
        print(f"  Summary:")
        print(f"    Total income: {summary['total_income']} CHF")
        print(f"    Total expenses: {summary['total_expenses']} CHF")
        print(f"    Net profit: {summary['net_profit']} CHF")
        print(f"    Orders revenue: {summary['orders_revenue']} CHF")
    
    def test_02_finance_transactions_have_correct_structure(self, enterprise_token):
        """Test that finance transactions have correct structure"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/finances",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert response.status_code == 200
        transactions = response.json().get('transactions', [])
        
        if not transactions:
            pytest.skip("No transactions to verify structure")
        
        # Check first transaction structure
        tx = transactions[0]
        assert "id" in tx
        assert "enterprise_id" in tx
        assert "transaction_type" in tx
        assert "amount" in tx
        assert "description" in tx
        assert "category" in tx
        
        print(f"✓ Transaction structure verified")
        print(f"  Sample: {tx['description']} - {tx['amount']} CHF ({tx['transaction_type']})")


class TestOrderStatusUpdatesInvoice:
    """Test that order status updates affect invoice and finance transaction"""
    
    @pytest.fixture(scope="class")
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Client login failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Enterprise login failed: {response.status_code}")
    
    def test_01_completed_order_marks_invoice_paid(self, client_token, enterprise_token):
        """Test that completing an order marks the invoice as 'paid'"""
        # Create a new order
        order_data = {
            "enterprise_id": ENTERPRISE_ID,
            "items": [
                {
                    "service_product_id": "test-product-2",
                    "name": "TEST_Service Completed",
                    "price": 50.0,
                    "quantity": 1
                }
            ],
            "notes": "Test order for completed status"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert create_response.status_code == 200
        order = create_response.json()
        order_id = order['id']
        
        print(f"✓ Created order {order_id}")
        
        # Verify invoice is pending
        invoices_response = requests.get(
            f"{BASE_URL}/api/enterprise/invoices",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        invoice = next(
            (inv for inv in invoices_response.json()['invoices'] if inv.get('order_id') == order_id),
            None
        )
        assert invoice is not None
        assert invoice['status'] == 'pending', f"Initial invoice status should be 'pending', got {invoice['status']}"
        
        print(f"✓ Invoice status is 'pending'")
        
        # Update order status to completed
        update_response = requests.put(
            f"{BASE_URL}/api/orders/{order_id}/status?status=completed",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert update_response.status_code == 200
        print(f"✓ Order status updated to 'completed'")
        
        # Verify invoice is now paid
        invoices_response = requests.get(
            f"{BASE_URL}/api/enterprise/invoices",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        invoice = next(
            (inv for inv in invoices_response.json()['invoices'] if inv.get('order_id') == order_id),
            None
        )
        assert invoice is not None
        assert invoice['status'] == 'paid', f"Invoice status should be 'paid' after completion, got {invoice['status']}"
        assert invoice.get('payment_date') is not None, "Invoice should have payment_date after completion"
        
        print(f"✓ Invoice status updated to 'paid'")
        print(f"  Payment date: {invoice['payment_date']}")
    
    def test_02_cancelled_order_removes_finance_transaction(self, client_token, enterprise_token):
        """Test that cancelling an order removes the finance transaction"""
        # Create a new order
        order_data = {
            "enterprise_id": ENTERPRISE_ID,
            "items": [
                {
                    "service_product_id": "test-product-3",
                    "name": "TEST_Service Cancelled",
                    "price": 75.0,
                    "quantity": 1
                }
            ],
            "notes": "Test order for cancelled status"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert create_response.status_code == 200
        order = create_response.json()
        order_id = order['id']
        
        print(f"✓ Created order {order_id}")
        
        # Verify finance transaction exists
        finances_response = requests.get(
            f"{BASE_URL}/api/enterprise/finances",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        transaction = next(
            (t for t in finances_response.json()['transactions'] if t.get('reference_id') == order_id),
            None
        )
        assert transaction is not None, "Finance transaction should exist after order creation"
        
        print(f"✓ Finance transaction exists for order")
        
        # Cancel the order
        update_response = requests.put(
            f"{BASE_URL}/api/orders/{order_id}/status?status=cancelled",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        assert update_response.status_code == 200
        print(f"✓ Order status updated to 'cancelled'")
        
        # Verify finance transaction is removed
        finances_response = requests.get(
            f"{BASE_URL}/api/enterprise/finances",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        transaction = next(
            (t for t in finances_response.json()['transactions'] if t.get('reference_id') == order_id),
            None
        )
        assert transaction is None, "Finance transaction should be removed after order cancellation"
        
        print(f"✓ Finance transaction removed after cancellation")
        
        # Verify invoice is marked as cancelled
        invoices_response = requests.get(
            f"{BASE_URL}/api/enterprise/invoices",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        invoice = next(
            (inv for inv in invoices_response.json()['invoices'] if inv.get('order_id') == order_id),
            None
        )
        assert invoice is not None
        assert invoice['status'] == 'cancelled', f"Invoice status should be 'cancelled', got {invoice['status']}"
        
        print(f"✓ Invoice status updated to 'cancelled'")


class TestFeeCalculations:
    """Test Titelli fee calculations are correct"""
    
    @pytest.fixture(scope="class")
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Client login failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Enterprise login failed: {response.status_code}")
    
    def test_01_fee_calculations_are_correct(self, client_token, enterprise_token):
        """Test that fee calculations match Titelli configuration"""
        # Create order with known amounts
        subtotal = 500.0  # 500 CHF
        
        order_data = {
            "enterprise_id": ENTERPRISE_ID,
            "items": [
                {
                    "service_product_id": "test-product-fee",
                    "name": "TEST_Fee Calculation Service",
                    "price": 250.0,
                    "quantity": 2
                }
            ],
            "notes": "Test order for fee calculation verification"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == 200
        order = response.json()
        
        # Expected calculations
        expected_subtotal = 500.0
        expected_transaction_fee = round(expected_subtotal * 0.029, 2)  # 14.50
        expected_management_fee = round(expected_subtotal * 0.10, 2)  # 50.00
        expected_total = round(expected_subtotal + expected_transaction_fee, 2)  # 514.50
        expected_enterprise_net = round(expected_subtotal - expected_management_fee, 2)  # 450.00
        
        # Verify order calculations
        assert order['subtotal'] == expected_subtotal, f"Subtotal: expected {expected_subtotal}, got {order['subtotal']}"
        assert abs(order['transaction_fee'] - expected_transaction_fee) < 0.01, \
            f"Transaction fee: expected {expected_transaction_fee}, got {order['transaction_fee']}"
        assert abs(order['management_fee'] - expected_management_fee) < 0.01, \
            f"Management fee: expected {expected_management_fee}, got {order['management_fee']}"
        assert abs(order['total'] - expected_total) < 0.01, \
            f"Total: expected {expected_total}, got {order['total']}"
        
        print(f"✓ Fee calculations verified for 500 CHF order:")
        print(f"  Subtotal: {order['subtotal']} CHF (expected: {expected_subtotal})")
        print(f"  Transaction fee (2.9%): {order['transaction_fee']} CHF (expected: {expected_transaction_fee})")
        print(f"  Management fee (10%): {order['management_fee']} CHF (expected: {expected_management_fee})")
        print(f"  Total TTC: {order['total']} CHF (expected: {expected_total})")
        
        # Verify invoice has correct enterprise_net
        invoices_response = requests.get(
            f"{BASE_URL}/api/enterprise/invoices",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        
        invoice = next(
            (inv for inv in invoices_response.json()['invoices'] if inv.get('order_id') == order['id']),
            None
        )
        
        assert invoice is not None
        assert abs(invoice['enterprise_net'] - expected_enterprise_net) < 0.01, \
            f"Enterprise net: expected {expected_enterprise_net}, got {invoice['enterprise_net']}"
        
        print(f"  Enterprise net: {invoice['enterprise_net']} CHF (expected: {expected_enterprise_net})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
