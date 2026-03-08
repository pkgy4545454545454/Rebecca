"""
Iteration 16 Bug Fixes Tests
Tests for:
1. Job application flow - CV documents visible and selectable
2. Cashback system - 10% cashback on orders and trainings
3. Cashback history page - balance, statistics, transaction history
4. Document upload - PDF/DOC files
5. Enterprise dashboard - job/training creation forms
6. Client dashboard - all tabs
7. Homepage - sections display
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
ADMIN_EMAIL = "admin@titelli.com"
ADMIN_PASSWORD = "Admin123!"


class TestAuthentication:
    """Authentication tests"""
    
    def test_client_login(self):
        """Test client login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200, f"Client login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        print(f"✓ Client login successful: {data['user'].get('email')}")
    
    def test_enterprise_login(self):
        """Test enterprise login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200, f"Enterprise login failed: {response.text}"
        data = response.json()
        assert "token" in data
        print(f"✓ Enterprise login successful: {data['user'].get('email')}")


class TestCashbackSystem:
    """Tests for 10% cashback system"""
    
    @pytest.fixture
    def client_token(self):
        """Get client auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_cashback_balance_endpoint(self, client_token):
        """Test cashback balance endpoint returns correct structure"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/cashback/balance", headers=headers)
        assert response.status_code == 200, f"Cashback balance failed: {response.text}"
        data = response.json()
        assert "balance" in data
        assert isinstance(data["balance"], (int, float))
        print(f"✓ Cashback balance: {data['balance']} CHF")
    
    def test_cashback_history_endpoint(self, client_token):
        """Test cashback history endpoint returns correct structure with 10% rate"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/cashback/history", headers=headers)
        assert response.status_code == 200, f"Cashback history failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "balance" in data
        assert "transactions" in data
        assert "statistics" in data
        
        # Verify statistics structure
        stats = data["statistics"]
        assert "total_earned" in stats
        assert "total_used" in stats
        assert "cashback_rate" in stats
        assert "transaction_count" in stats
        
        # CRITICAL: Verify 10% cashback rate
        assert stats["cashback_rate"] == "10%", f"Expected 10% cashback rate, got {stats['cashback_rate']}"
        
        print(f"✓ Cashback history - Balance: {data['balance']} CHF, Rate: {stats['cashback_rate']}")
        print(f"  Total earned: {stats['total_earned']} CHF, Total used: {stats['total_used']} CHF")
        print(f"  Transaction count: {stats['transaction_count']}")


class TestClientDocuments:
    """Tests for client documents API (CV for job applications)"""
    
    @pytest.fixture
    def client_token(self):
        """Get client auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_list_client_documents(self, client_token):
        """Test listing client documents"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/client/documents", headers=headers)
        assert response.status_code == 200, f"List documents failed: {response.text}"
        data = response.json()
        
        # Should return documents array
        documents = data.get("documents", data) if isinstance(data, dict) else data
        assert isinstance(documents, list)
        
        # Check document structure if any exist
        if documents:
            doc = documents[0]
            # Verify doc has url and name fields (the bug fix)
            assert "url" in doc or "file_path" in doc, "Document should have url or file_path"
            assert "name" in doc or "file_name" in doc, "Document should have name or file_name"
            print(f"✓ Found {len(documents)} documents")
            for d in documents[:3]:
                print(f"  - {d.get('name', d.get('file_name', 'Unknown'))} ({d.get('category', 'N/A')})")
        else:
            print("✓ Documents endpoint working (no documents yet)")


class TestJobsAPI:
    """Tests for jobs API"""
    
    @pytest.fixture
    def client_token(self):
        """Get client auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_list_all_jobs(self):
        """Test listing all jobs (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/jobs")
        assert response.status_code == 200, f"List jobs failed: {response.text}"
        data = response.json()
        
        jobs = data.get("jobs", data) if isinstance(data, dict) else data
        assert isinstance(jobs, list)
        print(f"✓ Found {len(jobs)} jobs")
        
        if jobs:
            job = jobs[0]
            assert "id" in job
            assert "title" in job
            print(f"  First job: {job.get('title')} at {job.get('enterprise_name', 'N/A')}")
    
    def test_get_job_detail(self):
        """Test getting job detail"""
        # First get a job ID
        response = requests.get(f"{BASE_URL}/api/jobs")
        jobs = response.json().get("jobs", response.json()) if isinstance(response.json(), dict) else response.json()
        
        if jobs:
            job_id = jobs[0]["id"]
            response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
            assert response.status_code == 200, f"Get job detail failed: {response.text}"
            job = response.json()
            assert job["id"] == job_id
            print(f"✓ Job detail: {job.get('title')}")
        else:
            pytest.skip("No jobs available to test")


class TestTrainingsAPI:
    """Tests for trainings API"""
    
    def test_list_all_trainings(self):
        """Test listing all trainings (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/trainings")
        assert response.status_code == 200, f"List trainings failed: {response.text}"
        data = response.json()
        
        trainings = data.get("trainings", data) if isinstance(data, dict) else data
        assert isinstance(trainings, list)
        print(f"✓ Found {len(trainings)} trainings")
        
        if trainings:
            training = trainings[0]
            assert "id" in training
            assert "title" in training
            assert "price" in training
            print(f"  First training: {training.get('title')} - {training.get('price')} CHF")


class TestEnterpriseDashboard:
    """Tests for enterprise dashboard APIs"""
    
    @pytest.fixture
    def enterprise_token(self):
        """Get enterprise auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_enterprise_profile(self, enterprise_token):
        """Test getting enterprise profile via /auth/me"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200, f"Get enterprise profile failed: {response.text}"
        data = response.json()
        assert "id" in data or "email" in data
        print(f"✓ Enterprise user profile: {data.get('email', 'N/A')}")
    
    def test_get_enterprise_jobs(self, enterprise_token):
        """Test getting enterprise's jobs"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/enterprise/jobs", headers=headers)
        assert response.status_code == 200, f"Get enterprise jobs failed: {response.text}"
        data = response.json()
        jobs = data.get("jobs", data) if isinstance(data, dict) else data
        print(f"✓ Enterprise has {len(jobs)} jobs")
    
    def test_get_enterprise_trainings(self, enterprise_token):
        """Test getting enterprise's trainings"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/enterprise/trainings", headers=headers)
        assert response.status_code == 200, f"Get enterprise trainings failed: {response.text}"
        data = response.json()
        trainings = data.get("trainings", data) if isinstance(data, dict) else data
        print(f"✓ Enterprise has {len(trainings)} trainings")
    
    def test_get_enterprise_applications(self, enterprise_token):
        """Test getting job applications for enterprise"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/enterprise/applications", headers=headers)
        assert response.status_code == 200, f"Get applications failed: {response.text}"
        data = response.json()
        assert "applications" in data
        assert "jobs" in data
        print(f"✓ Enterprise has {len(data['applications'])} applications")


class TestClientDashboard:
    """Tests for client dashboard APIs"""
    
    @pytest.fixture
    def client_token(self):
        """Get client auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_client_profile(self, client_token):
        """Test getting client profile via /auth/me"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200, f"Get profile failed: {response.text}"
        data = response.json()
        assert "email" in data
        print(f"✓ Client profile: {data.get('email')}")
    
    def test_get_client_orders(self, client_token):
        """Test getting client orders"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/orders", headers=headers)
        assert response.status_code == 200, f"Get orders failed: {response.text}"
        data = response.json()
        orders = data if isinstance(data, list) else data.get("orders", [])
        print(f"✓ Client has {len(orders)} orders")
    
    def test_get_client_job_applications(self, client_token):
        """Test getting client's job applications"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/client/job-applications", headers=headers)
        assert response.status_code == 200, f"Get applications failed: {response.text}"
        data = response.json()
        applications = data if isinstance(data, list) else data.get("applications", [])
        print(f"✓ Client has {len(applications)} job applications")


class TestFeaturedEndpoints:
    """Tests for homepage featured sections"""
    
    def test_featured_tendances(self):
        """Test tendances endpoint"""
        response = requests.get(f"{BASE_URL}/api/featured/tendances")
        assert response.status_code == 200, f"Tendances failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Tendances: {len(data)} enterprises")
    
    def test_featured_guests(self):
        """Test guests endpoint"""
        response = requests.get(f"{BASE_URL}/api/featured/guests")
        assert response.status_code == 200, f"Guests failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Guests: {len(data)} enterprises")
    
    def test_featured_offres(self):
        """Test offres endpoint"""
        response = requests.get(f"{BASE_URL}/api/featured/offres")
        assert response.status_code == 200, f"Offres failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Offres: {len(data)} items")
    
    def test_featured_premium(self):
        """Test premium endpoint"""
        response = requests.get(f"{BASE_URL}/api/featured/premium")
        assert response.status_code == 200, f"Premium failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Premium: {len(data)} enterprises")


class TestCategoriesEndpoints:
    """Tests for categories endpoints"""
    
    def test_product_categories(self):
        """Test product categories"""
        response = requests.get(f"{BASE_URL}/api/categories/products")
        assert response.status_code == 200, f"Product categories failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Product categories: {len(data)}")
    
    def test_service_categories(self):
        """Test service categories"""
        response = requests.get(f"{BASE_URL}/api/categories/services")
        assert response.status_code == 200, f"Service categories failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Service categories: {len(data)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
