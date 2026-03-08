"""
Iteration 32 - Cashback Withdrawal System Tests
Tests for:
- GET /api/cashback/withdrawal-info - Get withdrawal eligibility info
- PUT /api/client/profile - Save IBAN and bank_account_holder
- POST /api/cashback/withdraw - Create withdrawal request
- GET /api/cashback/withdrawals - Get withdrawal history
- Validation: minimum 50 CHF, bank info required
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_CLIENT_EMAIL = "test@example.com"
TEST_CLIENT_PASSWORD = "Test123!"

# Test IBAN (Swiss format)
TEST_IBAN = "CH9300762011623852957"
TEST_BANK_HOLDER = "Test User"


class TestCashbackWithdrawalSystem:
    """Test suite for cashback withdrawal functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate as test client"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_CLIENT_EMAIL,
            "password": TEST_CLIENT_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            self.user_id = data.get("user", {}).get("id")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            return True
        return False
    
    # ============ GET /api/cashback/withdrawal-info Tests ============
    
    def test_withdrawal_info_returns_correct_fields(self):
        """Test that withdrawal-info endpoint returns all required fields"""
        assert self.authenticate(), "Authentication failed"
        
        response = self.session.get(f"{BASE_URL}/api/cashback/withdrawal-info")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify all required fields are present
        assert "balance" in data, "Missing 'balance' field"
        assert "minimum_withdrawal" in data, "Missing 'minimum_withdrawal' field"
        assert "can_withdraw" in data, "Missing 'can_withdraw' field"
        assert "has_bank_info" in data, "Missing 'has_bank_info' field"
        
        # Verify data types
        assert isinstance(data["balance"], (int, float)), "balance should be numeric"
        assert isinstance(data["minimum_withdrawal"], (int, float)), "minimum_withdrawal should be numeric"
        assert isinstance(data["can_withdraw"], bool), "can_withdraw should be boolean"
        assert isinstance(data["has_bank_info"], bool), "has_bank_info should be boolean"
        
        # Verify minimum is 50 CHF
        assert data["minimum_withdrawal"] == 50.0, f"Expected minimum 50 CHF, got {data['minimum_withdrawal']}"
        
        print(f"✓ Withdrawal info: balance={data['balance']}, can_withdraw={data['can_withdraw']}, has_bank_info={data['has_bank_info']}")
    
    def test_withdrawal_info_shows_bank_info_when_saved(self):
        """Test that withdrawal-info shows bank info when IBAN is saved"""
        assert self.authenticate(), "Authentication failed"
        
        response = self.session.get(f"{BASE_URL}/api/cashback/withdrawal-info")
        assert response.status_code == 200
        
        data = response.json()
        
        # If bank info is saved, verify masked IBAN and account holder are returned
        if data["has_bank_info"]:
            assert "iban_masked" in data, "Missing 'iban_masked' when has_bank_info is True"
            assert "account_holder" in data, "Missing 'account_holder' when has_bank_info is True"
            assert data["iban_masked"] is not None, "iban_masked should not be None"
            assert data["account_holder"] is not None, "account_holder should not be None"
            print(f"✓ Bank info present: {data['iban_masked']} ({data['account_holder']})")
        else:
            print("✓ No bank info saved yet")
    
    def test_withdrawal_info_requires_auth(self):
        """Test that withdrawal-info requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cashback/withdrawal-info")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("✓ Withdrawal info requires authentication")
    
    # ============ PUT /api/client/profile Tests (IBAN fields) ============
    
    def test_save_bank_info_via_profile_update(self):
        """Test saving IBAN and bank_account_holder via profile update"""
        assert self.authenticate(), "Authentication failed"
        
        # Save bank info
        response = self.session.put(f"{BASE_URL}/api/client/profile", json={
            "iban": TEST_IBAN,
            "bank_account_holder": TEST_BANK_HOLDER
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify bank info was saved
        assert data.get("iban") == TEST_IBAN, f"IBAN not saved correctly: {data.get('iban')}"
        assert data.get("bank_account_holder") == TEST_BANK_HOLDER, f"Bank holder not saved: {data.get('bank_account_holder')}"
        
        print(f"✓ Bank info saved: IBAN={TEST_IBAN}, Holder={TEST_BANK_HOLDER}")
    
    def test_verify_bank_info_persisted(self):
        """Test that bank info is persisted and returned in withdrawal-info"""
        assert self.authenticate(), "Authentication failed"
        
        # First save bank info
        self.session.put(f"{BASE_URL}/api/client/profile", json={
            "iban": TEST_IBAN,
            "bank_account_holder": TEST_BANK_HOLDER
        })
        
        # Verify via withdrawal-info endpoint
        response = self.session.get(f"{BASE_URL}/api/cashback/withdrawal-info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_bank_info"] == True, "has_bank_info should be True after saving"
        assert data["account_holder"] == TEST_BANK_HOLDER, f"Account holder mismatch: {data.get('account_holder')}"
        
        # IBAN should be masked
        if data.get("iban_masked"):
            assert data["iban_masked"].endswith(TEST_IBAN[-4:]), "Masked IBAN should end with last 4 digits"
        
        print(f"✓ Bank info persisted and verified: {data['iban_masked']}")
    
    # ============ POST /api/cashback/withdraw Tests ============
    
    def test_withdraw_fails_without_bank_info(self):
        """Test that withdrawal fails if no bank info is saved"""
        assert self.authenticate(), "Authentication failed"
        
        # First clear bank info (set to empty)
        self.session.put(f"{BASE_URL}/api/client/profile", json={
            "iban": None,
            "bank_account_holder": None
        })
        
        # Try to withdraw
        response = self.session.post(f"{BASE_URL}/api/cashback/withdraw", json={})
        
        # Should fail with 400 (either for bank info or minimum balance)
        assert response.status_code == 400, f"Expected 400 without bank info, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "Error response should have 'detail'"
        
        # Error could be about bank info OR minimum balance (if balance < 50)
        error_msg = data["detail"].lower()
        valid_error = ("bancaires" in error_msg or "iban" in error_msg or 
                       "minimum" in error_msg or "50" in error_msg)
        assert valid_error, f"Error should mention bank info or minimum: {data['detail']}"
        
        print(f"✓ Withdrawal correctly rejected: {data['detail']}")
    
    def test_withdraw_fails_below_minimum(self):
        """Test that withdrawal fails if balance < 50 CHF"""
        assert self.authenticate(), "Authentication failed"
        
        # First ensure bank info is saved
        self.session.put(f"{BASE_URL}/api/client/profile", json={
            "iban": TEST_IBAN,
            "bank_account_holder": TEST_BANK_HOLDER
        })
        
        # Check current balance
        info_response = self.session.get(f"{BASE_URL}/api/cashback/withdrawal-info")
        balance = info_response.json().get("balance", 0)
        
        if balance < 50:
            # Try to withdraw - should fail
            response = self.session.post(f"{BASE_URL}/api/cashback/withdraw", json={})
            assert response.status_code == 400, f"Expected 400 for low balance, got {response.status_code}"
            
            data = response.json()
            assert "minimum" in data["detail"].lower() or "50" in data["detail"], \
                f"Error should mention minimum: {data['detail']}"
            
            print(f"✓ Withdrawal correctly rejected for low balance ({balance} CHF < 50 CHF)")
        else:
            print(f"⚠ Balance is {balance} CHF (>= 50), skipping low balance test")
    
    def test_withdraw_creates_record_and_deducts_balance(self):
        """Test that successful withdrawal creates record and deducts balance"""
        assert self.authenticate(), "Authentication failed"
        
        # Ensure bank info is saved
        self.session.put(f"{BASE_URL}/api/client/profile", json={
            "iban": TEST_IBAN,
            "bank_account_holder": TEST_BANK_HOLDER
        })
        
        # Check current balance
        info_response = self.session.get(f"{BASE_URL}/api/cashback/withdrawal-info")
        initial_balance = info_response.json().get("balance", 0)
        
        if initial_balance >= 50:
            # Perform withdrawal
            response = self.session.post(f"{BASE_URL}/api/cashback/withdraw", json={})
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            data = response.json()
            
            # Verify response fields
            assert data.get("success") == True, "success should be True"
            assert "withdrawal_id" in data, "Missing withdrawal_id"
            assert "new_balance" in data, "Missing new_balance"
            assert "status" in data, "Missing status"
            
            # Verify balance was deducted
            assert data["new_balance"] < initial_balance, "Balance should be deducted"
            
            # Status should be 'processing' or 'manual_processing'
            assert data["status"] in ["processing", "manual_processing"], \
                f"Unexpected status: {data['status']}"
            
            print(f"✓ Withdrawal successful: {initial_balance} -> {data['new_balance']} CHF, status={data['status']}")
        else:
            print(f"⚠ Balance is {initial_balance} CHF (< 50), cannot test withdrawal")
            pytest.skip("Insufficient balance for withdrawal test")
    
    def test_withdraw_requires_auth(self):
        """Test that withdraw endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/cashback/withdraw", json={})
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("✓ Withdraw endpoint requires authentication")
    
    # ============ GET /api/cashback/withdrawals Tests ============
    
    def test_withdrawal_history_returns_list(self):
        """Test that withdrawal history returns a list of withdrawals"""
        assert self.authenticate(), "Authentication failed"
        
        response = self.session.get(f"{BASE_URL}/api/cashback/withdrawals")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "withdrawals" in data, "Missing 'withdrawals' field"
        assert isinstance(data["withdrawals"], list), "withdrawals should be a list"
        
        # If there are withdrawals, verify structure
        if len(data["withdrawals"]) > 0:
            withdrawal = data["withdrawals"][0]
            assert "id" in withdrawal, "Withdrawal missing 'id'"
            assert "amount" in withdrawal, "Withdrawal missing 'amount'"
            assert "status" in withdrawal, "Withdrawal missing 'status'"
            assert "created_at" in withdrawal, "Withdrawal missing 'created_at'"
            
            print(f"✓ Found {len(data['withdrawals'])} withdrawal(s), latest: {withdrawal['amount']} CHF ({withdrawal['status']})")
        else:
            print("✓ No withdrawals yet (empty list)")
    
    def test_withdrawal_history_requires_auth(self):
        """Test that withdrawal history requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cashback/withdrawals")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("✓ Withdrawal history requires authentication")
    
    # ============ Integration Tests ============
    
    def test_full_withdrawal_flow(self):
        """Test complete withdrawal flow: save bank info -> check eligibility -> withdraw"""
        assert self.authenticate(), "Authentication failed"
        
        # Step 1: Save bank info
        profile_response = self.session.put(f"{BASE_URL}/api/client/profile", json={
            "iban": TEST_IBAN,
            "bank_account_holder": TEST_BANK_HOLDER
        })
        assert profile_response.status_code == 200, "Failed to save bank info"
        print("Step 1: Bank info saved ✓")
        
        # Step 2: Check withdrawal eligibility
        info_response = self.session.get(f"{BASE_URL}/api/cashback/withdrawal-info")
        assert info_response.status_code == 200
        info = info_response.json()
        
        assert info["has_bank_info"] == True, "Bank info should be saved"
        print(f"Step 2: Eligibility checked - balance={info['balance']}, can_withdraw={info['can_withdraw']} ✓")
        
        # Step 3: Attempt withdrawal (if eligible)
        if info["can_withdraw"]:
            withdraw_response = self.session.post(f"{BASE_URL}/api/cashback/withdraw", json={})
            assert withdraw_response.status_code == 200, f"Withdrawal failed: {withdraw_response.text}"
            
            result = withdraw_response.json()
            print(f"Step 3: Withdrawal successful - {result['new_balance']} CHF remaining ✓")
            
            # Step 4: Verify in history
            history_response = self.session.get(f"{BASE_URL}/api/cashback/withdrawals")
            assert history_response.status_code == 200
            
            history = history_response.json()
            assert len(history["withdrawals"]) > 0, "Withdrawal should appear in history"
            print(f"Step 4: Withdrawal appears in history ✓")
        else:
            print(f"Step 3: Cannot withdraw - {info.get('reason_cannot_withdraw', 'Unknown reason')}")
    
    def test_can_withdraw_logic(self):
        """Test that can_withdraw is correctly calculated"""
        assert self.authenticate(), "Authentication failed"
        
        # Ensure bank info is saved
        self.session.put(f"{BASE_URL}/api/client/profile", json={
            "iban": TEST_IBAN,
            "bank_account_holder": TEST_BANK_HOLDER
        })
        
        response = self.session.get(f"{BASE_URL}/api/cashback/withdrawal-info")
        data = response.json()
        
        # can_withdraw should be True only if balance >= 50 AND has_bank_info
        expected_can_withdraw = data["balance"] >= 50 and data["has_bank_info"]
        assert data["can_withdraw"] == expected_can_withdraw, \
            f"can_withdraw mismatch: expected {expected_can_withdraw}, got {data['can_withdraw']}"
        
        print(f"✓ can_withdraw logic correct: balance={data['balance']}, has_bank_info={data['has_bank_info']}, can_withdraw={data['can_withdraw']}")


class TestCashbackBalance:
    """Test cashback balance and history endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def authenticate(self):
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_CLIENT_EMAIL,
            "password": TEST_CLIENT_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            return True
        return False
    
    def test_cashback_balance_endpoint(self):
        """Test GET /api/cashback/balance returns balance"""
        assert self.authenticate(), "Authentication failed"
        
        response = self.session.get(f"{BASE_URL}/api/cashback/balance")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "balance" in data, "Missing 'balance' field"
        assert isinstance(data["balance"], (int, float)), "balance should be numeric"
        
        print(f"✓ Cashback balance: {data['balance']} CHF")
    
    def test_cashback_history_endpoint(self):
        """Test GET /api/cashback/history returns transactions"""
        assert self.authenticate(), "Authentication failed"
        
        response = self.session.get(f"{BASE_URL}/api/cashback/history")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "balance" in data, "Missing 'balance' field"
        assert "transactions" in data, "Missing 'transactions' field"
        assert isinstance(data["transactions"], list), "transactions should be a list"
        
        print(f"✓ Cashback history: {len(data['transactions'])} transactions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
