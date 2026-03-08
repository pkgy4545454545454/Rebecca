"""
Iteration 27 - Testing Features:
1. Postulations - CV display and download (resume_url)
2. Messages - Client/Enterprise conversations
3. Messages - Send/receive messages
4. Influencers - List and collaborations
5. IA Campaigns - Real BDD targeting
6. WebSocket status endpoint
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"


class TestAuthentication:
    """Authentication tests"""
    
    def test_client_login(self):
        """Test client login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == CLIENT_EMAIL
        assert data["user"]["user_type"] == "client"
    
    def test_enterprise_login(self):
        """Test enterprise login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == ENTERPRISE_EMAIL
        assert data["user"]["user_type"] == "entreprise"


@pytest.fixture
def client_token():
    """Get client authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": CLIENT_EMAIL,
        "password": CLIENT_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Client authentication failed")


@pytest.fixture
def enterprise_token():
    """Get enterprise authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ENTERPRISE_EMAIL,
        "password": ENTERPRISE_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Enterprise authentication failed")


class TestJobApplicationsWithCV:
    """Test job applications with CV (resume_url)"""
    
    def test_get_jobs_list(self):
        """Test getting list of jobs"""
        response = requests.get(f"{BASE_URL}/api/jobs")
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
        # Check that jobs have enterprise info
        if len(jobs) > 0:
            job = jobs[0]
            assert "id" in job
            assert "title" in job
            assert "enterprise_id" in job
    
    def test_get_job_applications_with_resume(self, enterprise_token):
        """Test getting job applications with resume_url"""
        # First get jobs to find one with applications
        response = requests.get(f"{BASE_URL}/api/enterprise/jobs", 
                               headers={"Authorization": f"Bearer {enterprise_token}"})
        assert response.status_code == 200
        jobs = response.json()
        
        # Find a job with applications
        job_with_apps = None
        for job in jobs:
            if job.get('applications_count', 0) > 0 or job.get('applications', 0) > 0:
                job_with_apps = job
                break
        
        if not job_with_apps:
            pytest.skip("No jobs with applications found")
        
        # Get applications for this job
        response = requests.get(
            f"{BASE_URL}/api/enterprise/jobs/{job_with_apps['id']}/applications",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "applications" in data
        
        # Check that applications have resume_url
        if len(data["applications"]) > 0:
            app = data["applications"][0]
            assert "resume_url" in app
            assert "applicant" in app
            assert "cover_letter" in app
    
    def test_cv_file_accessible(self, enterprise_token):
        """Test that CV files are accessible"""
        # Get a job with applications
        response = requests.get(f"{BASE_URL}/api/enterprise/jobs", 
                               headers={"Authorization": f"Bearer {enterprise_token}"})
        jobs = response.json()
        
        job_with_apps = None
        for job in jobs:
            if job.get('applications_count', 0) > 0 or job.get('applications', 0) > 0:
                job_with_apps = job
                break
        
        if not job_with_apps:
            pytest.skip("No jobs with applications found")
        
        # Get applications
        response = requests.get(
            f"{BASE_URL}/api/enterprise/jobs/{job_with_apps['id']}/applications",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        data = response.json()
        
        # Find an application with a real PDF resume
        for app in data.get("applications", []):
            resume_url = app.get("resume_url", "")
            if resume_url and resume_url.endswith(".pdf"):
                # Test that the CV file is accessible
                cv_response = requests.head(f"{BASE_URL}{resume_url}")
                assert cv_response.status_code == 200
                assert "application/pdf" in cv_response.headers.get("content-type", "")
                return
        
        pytest.skip("No PDF resumes found in applications")


class TestMessagesSystem:
    """Test messaging system between client and enterprise"""
    
    def test_get_conversations_client(self, client_token):
        """Test getting conversations for client"""
        response = requests.get(
            f"{BASE_URL}/api/messages/conversations",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        
        # Check conversation structure
        if len(data["conversations"]) > 0:
            conv = data["conversations"][0]
            assert "partner" in conv
            assert "last_message" in conv
            assert "unread_count" in conv
    
    def test_get_conversations_enterprise(self, enterprise_token):
        """Test getting conversations for enterprise"""
        response = requests.get(
            f"{BASE_URL}/api/messages/conversations",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
    
    def test_send_message_client_to_enterprise(self, client_token):
        """Test sending message from client to enterprise"""
        # Get enterprise user ID
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        enterprise_user_id = login_response.json()["user"]["id"]
        
        # Send message
        response = requests.post(
            f"{BASE_URL}/api/messages",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "recipient_id": enterprise_user_id,
                "content": "TEST_Message from iteration 27 test",
                "message_type": "text"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["content"] == "TEST_Message from iteration 27 test"
        assert data["recipient_id"] == enterprise_user_id
    
    def test_get_messages_with_partner(self, client_token):
        """Test getting messages with a specific partner"""
        # Get enterprise user ID
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        enterprise_user_id = login_response.json()["user"]["id"]
        
        # Get messages
        response = requests.get(
            f"{BASE_URL}/api/messages/{enterprise_user_id}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "partner" in data


class TestInfluencersSection:
    """Test influencers endpoints"""
    
    def test_get_influencers_list(self):
        """Test getting list of influencers"""
        response = requests.get(f"{BASE_URL}/api/influencers")
        assert response.status_code == 200
        data = response.json()
        assert "influencers" in data
        assert "total" in data
        assert data["total"] >= 8  # Should have at least 8 seeded influencers
        
        # Check influencer structure
        if len(data["influencers"]) > 0:
            inf = data["influencers"][0]
            assert "id" in inf
            assert "name" in inf
            assert "category" in inf
            assert "followers" in inf
            assert "engagement_rate" in inf
            assert "price" in inf
    
    def test_get_influencers_by_category(self):
        """Test filtering influencers by category"""
        response = requests.get(f"{BASE_URL}/api/influencers?category=Food")
        assert response.status_code == 200
        data = response.json()
        assert "influencers" in data
        # All returned influencers should be in Food category
        for inf in data["influencers"]:
            assert inf["category"] == "Food"
    
    def test_get_enterprise_collaborations(self, enterprise_token):
        """Test getting enterprise influencer collaborations"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/influencer-collaborations",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "collaborations" in data
        assert "stats" in data
        assert "total_collaborations" in data["stats"]
        assert "active_collaborations" in data["stats"]
        assert "total_investment" in data["stats"]
    
    def test_create_influencer_collaboration(self, enterprise_token):
        """Test creating an influencer collaboration"""
        # Get an influencer ID
        inf_response = requests.get(f"{BASE_URL}/api/influencers")
        influencers = inf_response.json()["influencers"]
        if len(influencers) == 0:
            pytest.skip("No influencers available")
        
        influencer_id = influencers[0]["id"]
        
        # Create collaboration
        response = requests.post(
            f"{BASE_URL}/api/enterprise/influencer-collaborations",
            headers={"Authorization": f"Bearer {enterprise_token}"},
            params={
                "influencer_id": influencer_id,
                "message": "TEST_Collaboration request from iteration 27",
                "budget": 1000
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["influencer_id"] == influencer_id
        assert "influencer" in data


class TestIACampaignsWithRealBDD:
    """Test IA campaigns with real database targeting"""
    
    def test_get_ia_campaigns(self, enterprise_token):
        """Test getting IA campaigns list"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/ia-campaigns",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "campaigns" in data
        assert "stats" in data
        assert "total_reach" in data["stats"]
        assert "total_engagement" in data["stats"]
        assert "total_conversions" in data["stats"]
        assert "real_customers" in data["stats"]
    
    def test_create_ia_campaign_with_real_targeting(self, enterprise_token):
        """Test creating IA campaign with real BDD targeting"""
        response = requests.post(
            f"{BASE_URL}/api/enterprise/ia-campaigns",
            headers={"Authorization": f"Bearer {enterprise_token}"},
            json={
                "name": "TEST_Campaign Iteration 27",
                "age_range": "25-45",
                "gender": "all",
                "interests": ["beaute"],
                "behavior": [],
                "location": "lausanne",
                "budget": "high"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "reach" in data
        assert "engagement" in data
        assert "conversions" in data
        assert "targeting_details" in data
        
        # Verify targeting details contain real BDD info
        targeting = data["targeting_details"]
        assert "total_potential_users" in targeting
        assert "budget_multiplier" in targeting
        assert targeting["budget_multiplier"] == 0.85  # high budget = 85%
    
    def test_ia_campaign_budget_multipliers(self, enterprise_token):
        """Test that different budgets apply correct multipliers"""
        budgets = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.85,
            "premium": 1.0
        }
        
        for budget, expected_multiplier in budgets.items():
            response = requests.post(
                f"{BASE_URL}/api/enterprise/ia-campaigns",
                headers={"Authorization": f"Bearer {enterprise_token}"},
                json={
                    "name": f"TEST_Budget_{budget}_Campaign",
                    "age_range": "18-65",
                    "gender": "all",
                    "interests": [],
                    "behavior": [],
                    "location": "",
                    "budget": budget
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["targeting_details"]["budget_multiplier"] == expected_multiplier


class TestWebSocketEndpoints:
    """Test WebSocket related endpoints"""
    
    def test_ws_status_endpoint(self):
        """Test WebSocket status endpoint"""
        response = requests.get(f"{BASE_URL}/api/ws/status")
        assert response.status_code == 200
        data = response.json()
        assert "online_users_count" in data
        assert "status" in data
        assert data["status"] == "active"
    
    def test_ws_online_friends_endpoint(self, client_token):
        """Test WebSocket online friends endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/ws/online-friends",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "online_friends" in data


class TestEnterpriseCustomers:
    """Test enterprise customers endpoint (real BDD data)"""
    
    def test_get_enterprise_customers(self, enterprise_token):
        """Test getting real customers from orders"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/customers",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert "total" in data
        assert "stats" in data
        
        # Check customer structure if any exist
        if len(data["customers"]) > 0:
            customer = data["customers"][0]
            assert "id" in customer
            assert "first_name" in customer
            assert "orders_count" in customer
            assert "total_spent" in customer


class TestHealthAndRoot:
    """Test basic health endpoints"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Titelli" in data["message"]
