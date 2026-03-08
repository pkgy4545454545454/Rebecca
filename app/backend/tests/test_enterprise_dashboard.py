"""
Test suite for Titelli Enterprise Dashboard APIs
Tests: Team, Agenda, Finances, Stock, Documents, Jobs, Investments, Advertising
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"
ADMIN_EMAIL = "admin@titelli.com"
ADMIN_PASSWORD = "Admin123!"


class TestAuth:
    """Authentication tests"""
    
    def test_enterprise_login(self):
        """Test enterprise user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not in response"
        assert "user" in data, "User not in response"
        assert data["user"]["user_type"] == "entreprise", "User type should be entreprise"
        print(f"✓ Enterprise login successful - User: {data['user']['first_name']} {data['user']['last_name']}")
        return data["token"]
    
    def test_client_login(self):
        """Test client user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200, f"Client login failed: {response.text}"
        data = response.json()
        assert "token" in data
        print(f"✓ Client login successful")
        return data["token"]
    
    def test_get_me(self):
        """Test get current user endpoint"""
        token = self.test_enterprise_login()
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200, f"Get me failed: {response.text}"
        data = response.json()
        assert data["email"] == ENTERPRISE_EMAIL
        print(f"✓ Get me successful - Email: {data['email']}")


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
def auth_headers(enterprise_token):
    """Get auth headers"""
    return {"Authorization": f"Bearer {enterprise_token}"}


class TestEnterpriseTeam:
    """Team management API tests"""
    
    def test_get_team_list(self, auth_headers):
        """Test getting team members list"""
        response = requests.get(f"{BASE_URL}/api/enterprise/team", headers=auth_headers)
        assert response.status_code == 200, f"Get team failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get team list successful - {len(data)} members")
    
    def test_add_team_member(self, auth_headers):
        """Test adding a team member"""
        member_data = {
            "first_name": "TEST_Jean",
            "last_name": "Dupont",
            "email": "test_jean.dupont@test.com",
            "phone": "+41 79 123 45 67",
            "role": "Manager",
            "department": "Ventes"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/team", json=member_data, headers=auth_headers)
        assert response.status_code == 200, f"Add team member failed: {response.text}"
        data = response.json()
        assert "id" in data, "Member ID not in response"
        assert data["first_name"] == "TEST_Jean"
        print(f"✓ Add team member successful - ID: {data['id']}")
        return data["id"]
    
    def test_delete_team_member(self, auth_headers):
        """Test deleting a team member"""
        # First add a member
        member_data = {
            "first_name": "TEST_ToDelete",
            "last_name": "Member",
            "email": "test_delete@test.com",
            "role": "Temp"
        }
        add_response = requests.post(f"{BASE_URL}/api/enterprise/team", json=member_data, headers=auth_headers)
        if add_response.status_code == 200:
            member_id = add_response.json()["id"]
            # Now delete
            delete_response = requests.delete(f"{BASE_URL}/api/enterprise/team/{member_id}", headers=auth_headers)
            assert delete_response.status_code == 200, f"Delete team member failed: {delete_response.text}"
            print(f"✓ Delete team member successful")


class TestEnterpriseAgenda:
    """Agenda/Calendar API tests"""
    
    def test_get_agenda(self, auth_headers):
        """Test getting agenda events"""
        response = requests.get(f"{BASE_URL}/api/enterprise/agenda", headers=auth_headers)
        assert response.status_code == 200, f"Get agenda failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get agenda successful - {len(data)} events")
    
    def test_create_agenda_event(self, auth_headers):
        """Test creating an agenda event"""
        event_data = {
            "title": "TEST_Rendez-vous client",
            "description": "Meeting with important client",
            "event_type": "appointment",
            "start_datetime": "2026-01-20T10:00:00",
            "end_datetime": "2026-01-20T11:00:00",
            "color": "#0047AB"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/agenda", json=event_data, headers=auth_headers)
        assert response.status_code == 200, f"Create event failed: {response.text}"
        data = response.json()
        assert "id" in data, "Event ID not in response"
        assert data["title"] == "TEST_Rendez-vous client"
        print(f"✓ Create agenda event successful - ID: {data['id']}")
        return data["id"]
    
    def test_delete_agenda_event(self, auth_headers):
        """Test deleting an agenda event"""
        # First create an event
        event_data = {
            "title": "TEST_ToDelete",
            "event_type": "task",
            "start_datetime": "2026-01-21T10:00:00"
        }
        add_response = requests.post(f"{BASE_URL}/api/enterprise/agenda", json=event_data, headers=auth_headers)
        if add_response.status_code == 200:
            event_id = add_response.json()["id"]
            # Now delete
            delete_response = requests.delete(f"{BASE_URL}/api/enterprise/agenda/{event_id}", headers=auth_headers)
            assert delete_response.status_code == 200, f"Delete event failed: {delete_response.text}"
            print(f"✓ Delete agenda event successful")


class TestEnterpriseFinances:
    """Finances API tests"""
    
    def test_get_finances(self, auth_headers):
        """Test getting finances summary"""
        response = requests.get(f"{BASE_URL}/api/enterprise/finances", headers=auth_headers)
        assert response.status_code == 200, f"Get finances failed: {response.text}"
        data = response.json()
        assert "summary" in data, "Summary not in response"
        assert "transactions" in data, "Transactions not in response"
        print(f"✓ Get finances successful - Net profit: {data['summary'].get('net_profit', 0)} CHF")
    
    def test_add_transaction(self, auth_headers):
        """Test adding a financial transaction"""
        transaction_data = {
            "transaction_type": "income",
            "category": "sales",
            "amount": 150.00,
            "description": "TEST_Vente service",
            "date": "2026-01-15"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/finances/transactions", json=transaction_data, headers=auth_headers)
        assert response.status_code == 200, f"Add transaction failed: {response.text}"
        data = response.json()
        assert "id" in data, "Transaction ID not in response"
        print(f"✓ Add transaction successful - ID: {data['id']}")
        return data["id"]


class TestEnterpriseStock:
    """Stock management API tests"""
    
    def test_get_stock(self, auth_headers):
        """Test getting stock list"""
        response = requests.get(f"{BASE_URL}/api/enterprise/stock", headers=auth_headers)
        assert response.status_code == 200, f"Get stock failed: {response.text}"
        data = response.json()
        assert "items" in data, "Items not in response"
        assert "alerts" in data, "Alerts not in response"
        print(f"✓ Get stock successful - {len(data['items'])} items, {len(data['alerts'])} alerts")
    
    def test_add_stock_item(self, auth_headers):
        """Test adding a stock item"""
        stock_data = {
            "product_id": "test-product-123",
            "product_name": "TEST_Produit Test",
            "quantity": 50,
            "min_quantity": 10,
            "unit": "pièce"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/stock", json=stock_data, headers=auth_headers)
        assert response.status_code == 200, f"Add stock failed: {response.text}"
        data = response.json()
        assert "id" in data, "Stock ID not in response"
        print(f"✓ Add stock item successful - ID: {data['id']}")
    
    def test_stock_movement(self, auth_headers):
        """Test recording stock movement"""
        movement_data = {
            "product_id": "test-product-123",
            "quantity": 5,
            "movement_type": "in"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/stock/movement", json=movement_data, headers=auth_headers)
        # May return 200 or 404 if product doesn't exist
        assert response.status_code in [200, 404], f"Stock movement failed: {response.text}"
        print(f"✓ Stock movement test completed - Status: {response.status_code}")


class TestEnterpriseDocuments:
    """Documents API tests"""
    
    def test_get_documents(self, auth_headers):
        """Test getting documents list"""
        response = requests.get(f"{BASE_URL}/api/enterprise/documents", headers=auth_headers)
        assert response.status_code == 200, f"Get documents failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get documents successful - {len(data)} documents")
    
    def test_add_document(self, auth_headers):
        """Test adding a document"""
        doc_data = {
            "title": "TEST_Contrat Client",
            "category": "contract",
            "file_url": "https://example.com/test-contract.pdf",
            "file_type": "pdf",
            "is_important": True
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/documents", json=doc_data, headers=auth_headers)
        assert response.status_code == 200, f"Add document failed: {response.text}"
        data = response.json()
        assert "id" in data, "Document ID not in response"
        print(f"✓ Add document successful - ID: {data['id']}")
        return data["id"]


class TestEnterpriseJobs:
    """Jobs/Employment API tests"""
    
    def test_get_enterprise_jobs(self, auth_headers):
        """Test getting enterprise jobs"""
        response = requests.get(f"{BASE_URL}/api/enterprise/jobs", headers=auth_headers)
        assert response.status_code == 200, f"Get jobs failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get enterprise jobs successful - {len(data)} jobs")
    
    def test_create_job(self, auth_headers):
        """Test creating a job posting"""
        job_data = {
            "title": "TEST_Esthéticienne",
            "description": "Recherche esthéticienne expérimentée",
            "job_type": "full_time",
            "salary_min": 4000,
            "salary_max": 5000,
            "salary_type": "monthly",
            "location": "Lausanne",
            "remote": False,
            "requirements": "3 ans d'expérience minimum",
            "benefits": "Assurance maladie, formation continue"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/jobs", json=job_data, headers=auth_headers)
        assert response.status_code == 200, f"Create job failed: {response.text}"
        data = response.json()
        assert "id" in data, "Job ID not in response"
        assert data["title"] == "TEST_Esthéticienne"
        print(f"✓ Create job successful - ID: {data['id']}")
        return data["id"]
    
    def test_get_all_jobs_public(self):
        """Test getting all public jobs"""
        response = requests.get(f"{BASE_URL}/api/jobs")
        assert response.status_code == 200, f"Get all jobs failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get all public jobs successful - {len(data)} jobs")


class TestEnterpriseInvestments:
    """Investments API tests"""
    
    def test_get_enterprise_investments(self, auth_headers):
        """Test getting enterprise investments"""
        response = requests.get(f"{BASE_URL}/api/enterprise/investments", headers=auth_headers)
        assert response.status_code == 200, f"Get investments failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get enterprise investments successful - {len(data)} investments")
    
    def test_create_investment(self, auth_headers):
        """Test creating an investment opportunity"""
        investment_data = {
            "title": "TEST_Expansion Spa",
            "description": "Investissement pour expansion du spa",
            "investment_type": "shares",
            "min_investment": 5000,
            "max_investment": 50000,
            "expected_return": 8.5,
            "duration": "24 mois",
            "risk_level": "medium"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/investments", json=investment_data, headers=auth_headers)
        assert response.status_code == 200, f"Create investment failed: {response.text}"
        data = response.json()
        assert "id" in data, "Investment ID not in response"
        print(f"✓ Create investment successful - ID: {data['id']}")
        return data["id"]


class TestEnterpriseAdvertising:
    """Advertising API tests"""
    
    def test_get_advertising(self, auth_headers):
        """Test getting advertising campaigns"""
        response = requests.get(f"{BASE_URL}/api/enterprise/advertising", headers=auth_headers)
        assert response.status_code == 200, f"Get advertising failed: {response.text}"
        data = response.json()
        assert "campaigns" in data, "Campaigns not in response"
        assert "stats" in data, "Stats not in response"
        print(f"✓ Get advertising successful - {len(data['campaigns'])} campaigns")
    
    def test_create_ad_campaign(self, auth_headers):
        """Test creating an ad campaign"""
        ad_data = {
            "title": "TEST_Promo Janvier",
            "ad_type": "banner",
            "placement": "homepage",
            "budget": 100,
            "start_date": "2026-01-15",
            "end_date": "2026-02-15"
        }
        response = requests.post(f"{BASE_URL}/api/enterprise/advertising", json=ad_data, headers=auth_headers)
        assert response.status_code == 200, f"Create ad failed: {response.text}"
        data = response.json()
        assert "id" in data, "Ad ID not in response"
        print(f"✓ Create ad campaign successful - ID: {data['id']}")
        return data["id"]


class TestEnterpriseOrders:
    """Orders API tests"""
    
    def test_get_orders(self, auth_headers):
        """Test getting enterprise orders"""
        response = requests.get(f"{BASE_URL}/api/orders", headers=auth_headers)
        assert response.status_code == 200, f"Get orders failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Get orders successful - {len(data)} orders")


class TestEnterpriseProfile:
    """Enterprise profile API tests"""
    
    def test_get_enterprises_list(self):
        """Test getting enterprises list"""
        response = requests.get(f"{BASE_URL}/api/enterprises")
        assert response.status_code == 200, f"Get enterprises failed: {response.text}"
        data = response.json()
        assert "enterprises" in data, "Enterprises not in response"
        assert "total" in data, "Total not in response"
        print(f"✓ Get enterprises list successful - {data['total']} enterprises")
    
    def test_get_services_products(self, auth_headers):
        """Test getting services/products"""
        response = requests.get(f"{BASE_URL}/api/services-products", headers=auth_headers)
        assert response.status_code == 200, f"Get services failed: {response.text}"
        data = response.json()
        assert "items" in data, "Items not in response"
        print(f"✓ Get services/products successful - {len(data['items'])} items")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_data(self, auth_headers):
        """Clean up TEST_ prefixed data"""
        # Get and delete test team members
        team_response = requests.get(f"{BASE_URL}/api/enterprise/team", headers=auth_headers)
        if team_response.status_code == 200:
            for member in team_response.json():
                if member.get("first_name", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/enterprise/team/{member['id']}", headers=auth_headers)
        
        # Get and delete test agenda events
        agenda_response = requests.get(f"{BASE_URL}/api/enterprise/agenda", headers=auth_headers)
        if agenda_response.status_code == 200:
            for event in agenda_response.json():
                if event.get("title", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/enterprise/agenda/{event['id']}", headers=auth_headers)
        
        # Get and delete test jobs
        jobs_response = requests.get(f"{BASE_URL}/api/enterprise/jobs", headers=auth_headers)
        if jobs_response.status_code == 200:
            for job in jobs_response.json():
                if job.get("title", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/enterprise/jobs/{job['id']}", headers=auth_headers)
        
        # Get and delete test investments
        inv_response = requests.get(f"{BASE_URL}/api/enterprise/investments", headers=auth_headers)
        if inv_response.status_code == 200:
            for inv in inv_response.json():
                if inv.get("title", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/enterprise/investments/{inv['id']}", headers=auth_headers)
        
        # Get and delete test documents
        docs_response = requests.get(f"{BASE_URL}/api/enterprise/documents", headers=auth_headers)
        if docs_response.status_code == 200:
            for doc in docs_response.json():
                if doc.get("title", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/enterprise/documents/{doc['id']}", headers=auth_headers)
        
        # Get and delete test ads
        ads_response = requests.get(f"{BASE_URL}/api/enterprise/advertising", headers=auth_headers)
        if ads_response.status_code == 200:
            for ad in ads_response.json().get("campaigns", []):
                if ad.get("title", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/enterprise/advertising/{ad['id']}", headers=auth_headers)
        
        print("✓ Cleanup completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
