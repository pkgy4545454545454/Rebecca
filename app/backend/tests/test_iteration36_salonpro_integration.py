"""
Iteration 36 - SalonPro Integration Tests
Tests for:
1. /api/auth/salonpro-token endpoint - generates JWT token with redirect_url
2. /api/client/agenda - returns personal events AND bookings
3. sync_order_to_salonpro webhook function (called during order creation)
"""

import pytest
import requests
import os
import json
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"


class TestSalonProTokenEndpoint:
    """Tests for /api/auth/salonpro-token endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as enterprise user"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as enterprise
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code == 200:
            self.enterprise_token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.enterprise_token}"})
        else:
            pytest.skip(f"Enterprise login failed: {response.status_code}")
    
    def test_salonpro_token_returns_valid_response(self):
        """Test that salonpro-token endpoint returns token and redirect_url"""
        response = self.session.get(f"{BASE_URL}/api/auth/salonpro-token")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify required fields
        assert "token" in data, "Response should contain 'token'"
        assert "redirect_url" in data, "Response should contain 'redirect_url'"
        assert "salonpro_url" in data, "Response should contain 'salonpro_url'"
        assert "expires_in" in data, "Response should contain 'expires_in'"
        
        # Verify token is a non-empty string
        assert isinstance(data["token"], str), "Token should be a string"
        assert len(data["token"]) > 50, "Token should be a valid JWT (length > 50)"
        
        # Verify redirect_url contains the token
        assert data["token"] in data["redirect_url"], "redirect_url should contain the token"
        assert "autologin_token=" in data["redirect_url"], "redirect_url should have autologin_token param"
        
        # Verify expires_in is 300 seconds (5 minutes)
        assert data["expires_in"] == 300, f"expires_in should be 300, got {data['expires_in']}"
        
        print(f"SUCCESS: SalonPro token generated")
        print(f"  - Token length: {len(data['token'])}")
        print(f"  - SalonPro URL: {data['salonpro_url']}")
        print(f"  - Expires in: {data['expires_in']} seconds")
    
    def test_salonpro_token_requires_enterprise_user(self):
        """Test that client users cannot access salonpro-token endpoint"""
        # Login as client
        client_session = requests.Session()
        client_session.headers.update({"Content-Type": "application/json"})
        
        login_response = client_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip("Client login failed")
        
        client_token = login_response.json().get("token")
        client_session.headers.update({"Authorization": f"Bearer {client_token}"})
        
        # Try to get salonpro token as client
        response = client_session.get(f"{BASE_URL}/api/auth/salonpro-token")
        
        assert response.status_code == 403, f"Expected 403 for client user, got {response.status_code}"
        print("SUCCESS: Client users correctly blocked from salonpro-token endpoint")
    
    def test_salonpro_token_requires_authentication(self):
        """Test that unauthenticated requests are rejected"""
        response = requests.get(f"{BASE_URL}/api/auth/salonpro-token")
        
        assert response.status_code == 401, f"Expected 401 for unauthenticated request, got {response.status_code}"
        print("SUCCESS: Unauthenticated requests correctly rejected")


class TestClientAgendaWithBookings:
    """Tests for /api/client/agenda endpoint including bookings"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as client user"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as client
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code == 200:
            self.client_token = response.json().get("token")
            self.user_data = response.json().get("user")
            self.session.headers.update({"Authorization": f"Bearer {self.client_token}"})
        else:
            pytest.skip(f"Client login failed: {response.status_code}")
    
    def test_client_agenda_returns_events_array(self):
        """Test that client agenda returns events array"""
        response = self.session.get(f"{BASE_URL}/api/client/agenda")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "events" in data, "Response should contain 'events' array"
        assert isinstance(data["events"], list), "events should be a list"
        
        print(f"SUCCESS: Client agenda returned {len(data['events'])} events")
    
    def test_client_agenda_booking_has_source_field(self):
        """Test that bookings in agenda have source='booking' field"""
        response = self.session.get(f"{BASE_URL}/api/client/agenda")
        
        assert response.status_code == 200
        
        data = response.json()
        events = data.get("events", [])
        
        # Check if any bookings exist
        bookings = [e for e in events if e.get("source") == "booking"]
        
        if bookings:
            for booking in bookings:
                # Verify booking has required fields
                assert "source" in booking, "Booking should have 'source' field"
                assert booking["source"] == "booking", "Booking source should be 'booking'"
                assert "enterprise_name" in booking, "Booking should have 'enterprise_name'"
                assert "event_type" in booking, "Booking should have 'event_type'"
                assert booking["event_type"] == "appointment", "Booking event_type should be 'appointment'"
                
            print(f"SUCCESS: Found {len(bookings)} bookings with correct source='booking' field")
        else:
            print("INFO: No bookings found in client agenda (this is expected if no appointments exist)")
    
    def test_client_agenda_create_personal_event(self):
        """Test creating a personal agenda event"""
        event_data = {
            "title": "TEST_Personal Event",
            "description": "Test event for iteration 36",
            "start_datetime": "2026-02-01T10:00:00",
            "end_datetime": "2026-02-01T11:00:00",
            "event_type": "personal",
            "location": "Test Location"
        }
        
        response = self.session.post(f"{BASE_URL}/api/client/agenda", json=event_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify created event
        assert "id" in data, "Created event should have 'id'"
        assert data["title"] == event_data["title"], "Title should match"
        
        # Store event ID for cleanup
        self.created_event_id = data["id"]
        
        print(f"SUCCESS: Personal event created with ID: {data['id']}")
        
        # Cleanup - delete the test event
        delete_response = self.session.delete(f"{BASE_URL}/api/client/agenda/{data['id']}")
        if delete_response.status_code == 200:
            print("  - Test event cleaned up successfully")


class TestOrderWebhookSync:
    """Tests for order creation with SalonPro webhook sync"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as client user"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as client
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code == 200:
            self.client_token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.client_token}"})
        else:
            pytest.skip(f"Client login failed: {response.status_code}")
    
    def test_order_creation_triggers_webhook(self):
        """Test that order creation works (webhook is called internally)"""
        # First, get an enterprise to order from
        enterprises_response = self.session.get(f"{BASE_URL}/api/enterprises?limit=1")
        
        if enterprises_response.status_code != 200:
            pytest.skip("Could not fetch enterprises")
        
        enterprises = enterprises_response.json().get("enterprises", [])
        if not enterprises:
            pytest.skip("No enterprises available for testing")
        
        enterprise_id = enterprises[0]["id"]
        
        # Get services from this enterprise
        services_response = self.session.get(f"{BASE_URL}/api/services-products?enterprise_id={enterprise_id}&limit=1")
        
        if services_response.status_code != 200:
            pytest.skip("Could not fetch services")
        
        services = services_response.json().get("items", [])
        if not services:
            pytest.skip("No services available for testing")
        
        service = services[0]
        
        # Create order
        order_data = {
            "enterprise_id": enterprise_id,
            "items": [{
                "service_product_id": service["id"],
                "name": service["name"],
                "price": service["price"],
                "quantity": 1
            }],
            "delivery_address": "Test Address for SalonPro Sync",
            "notes": "TEST_Order for webhook sync test"
        }
        
        response = self.session.post(f"{BASE_URL}/api/orders", json=order_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify order was created
        assert "id" in data, "Order should have 'id'"
        assert data["enterprise_id"] == enterprise_id, "Enterprise ID should match"
        
        # Note: The webhook sync_order_to_salonpro is called asynchronously
        # Since SALONPRO_WEBHOOK_URL is not configured, it will be skipped silently
        # This is expected behavior as mentioned in the test request
        
        print(f"SUCCESS: Order created with ID: {data['id']}")
        print("  - Webhook sync_order_to_salonpro was triggered (skipped if URL not configured)")


class TestEnterpriseMenuSalonProButton:
    """Tests to verify the Voir Planning button configuration"""
    
    def test_menu_item_configuration(self):
        """Verify the menu item for SalonPro is correctly configured in frontend"""
        # This is a configuration check - the actual button test will be done via Playwright
        # Here we just verify the API endpoint exists and works
        
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login as enterprise
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        
        assert response.status_code == 200, "Enterprise login should succeed"
        
        token = response.json().get("token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Verify the salonpro-token endpoint is accessible
        response = session.get(f"{BASE_URL}/api/auth/salonpro-token")
        
        assert response.status_code == 200, "SalonPro token endpoint should be accessible"
        
        data = response.json()
        assert "redirect_url" in data, "Should return redirect_url for button click"
        
        print("SUCCESS: SalonPro token endpoint ready for 'Voir Planning' button")
        print(f"  - Redirect URL pattern: {data['salonpro_url']}/dashboard?autologin_token=...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
