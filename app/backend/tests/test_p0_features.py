"""
Test P0 Features - Titelli Marketplace
- Job application system
- Job filters (type, location)
- Enterprise applications management
- Boosted advertising algorithm
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


class TestJobFiltersAndListing:
    """Test job listing and filtering functionality"""
    
    def test_list_all_jobs(self):
        """Test GET /api/jobs - list all public jobs"""
        response = requests.get(f"{BASE_URL}/api/jobs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "jobs" in data or isinstance(data, list), "Response should contain jobs"
        jobs = data.get('jobs', data) if isinstance(data, dict) else data
        print(f"SUCCESS: Listed {len(jobs)} jobs")
    
    def test_list_jobs_with_type_filter(self):
        """Test GET /api/jobs?type=CDI - filter by job type"""
        response = requests.get(f"{BASE_URL}/api/jobs", params={"type": "CDI"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        jobs = data.get('jobs', data) if isinstance(data, dict) else data
        # Verify all returned jobs have the correct type
        for job in jobs:
            if job.get('type'):
                assert job['type'] == 'CDI', f"Job type should be CDI, got {job['type']}"
        print(f"SUCCESS: CDI filter returned {len(jobs)} jobs")
    
    def test_list_jobs_with_location_filter(self):
        """Test GET /api/jobs?location=Lausanne - filter by location"""
        response = requests.get(f"{BASE_URL}/api/jobs", params={"location": "Lausanne"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        jobs = data.get('jobs', data) if isinstance(data, dict) else data
        print(f"SUCCESS: Location filter returned {len(jobs)} jobs")
    
    def test_get_job_detail(self):
        """Test GET /api/jobs/{job_id} - get job details"""
        # First get a job ID
        list_response = requests.get(f"{BASE_URL}/api/jobs")
        jobs = list_response.json().get('jobs', list_response.json()) if isinstance(list_response.json(), dict) else list_response.json()
        
        if not jobs:
            pytest.skip("No jobs available to test detail endpoint")
        
        job_id = jobs[0]['id']
        response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        job = response.json()
        assert job['id'] == job_id, "Job ID should match"
        assert 'title' in job, "Job should have title"
        print(f"SUCCESS: Got job detail for '{job.get('title')}'")


class TestJobApplicationSystem:
    """Test job application submission and management"""
    
    @pytest.fixture
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Client login failed: {response.text}")
        return response.json()['token']
    
    @pytest.fixture
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Enterprise login failed: {response.text}")
        return response.json()['token']
    
    def test_apply_to_job_requires_auth(self):
        """Test POST /api/jobs/{job_id}/apply - requires authentication"""
        # Get a job ID first
        list_response = requests.get(f"{BASE_URL}/api/jobs")
        jobs = list_response.json().get('jobs', list_response.json()) if isinstance(list_response.json(), dict) else list_response.json()
        
        if not jobs:
            pytest.skip("No jobs available to test")
        
        job_id = jobs[0]['id']
        response = requests.post(f"{BASE_URL}/api/jobs/{job_id}/apply", json={
            "resume_url": "/uploads/cv.pdf",
            "cover_letter": "Test cover letter"
        })
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("SUCCESS: Apply endpoint requires authentication")
    
    def test_apply_to_job_with_auth(self, client_token):
        """Test POST /api/jobs/{job_id}/apply - submit application"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        # Get a job ID first
        list_response = requests.get(f"{BASE_URL}/api/jobs")
        jobs = list_response.json().get('jobs', list_response.json()) if isinstance(list_response.json(), dict) else list_response.json()
        
        if not jobs:
            pytest.skip("No jobs available to test")
        
        job_id = jobs[0]['id']
        
        # Try to apply
        response = requests.post(
            f"{BASE_URL}/api/jobs/{job_id}/apply",
            json={
                "resume_url": f"/uploads/test_cv_{uuid.uuid4().hex[:8]}.pdf",
                "cover_letter": "Je suis très motivé pour ce poste. Test application."
            },
            headers=headers
        )
        
        # Either 200 (success) or 400 (already applied) is acceptable
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert 'id' in data, "Application should have an ID"
            assert data['status'] == 'pending', "New application should be pending"
            print(f"SUCCESS: Application submitted with ID {data['id']}")
        else:
            print("INFO: User already applied to this job (expected behavior)")
    
    def test_get_my_applications(self, client_token):
        """Test GET /api/client/job-applications - get user's applications"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(f"{BASE_URL}/api/client/job-applications", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'applications' in data, "Response should contain applications"
        print(f"SUCCESS: User has {len(data['applications'])} job applications")


class TestEnterpriseApplicationsManagement:
    """Test enterprise applications section"""
    
    @pytest.fixture
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Enterprise login failed: {response.text}")
        return response.json()['token']
    
    def test_get_enterprise_applications(self, enterprise_token):
        """Test GET /api/enterprise/applications - get all applications for enterprise jobs"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        response = requests.get(f"{BASE_URL}/api/enterprise/applications", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert 'applications' in data, "Response should contain applications"
        assert 'jobs' in data, "Response should contain jobs"
        assert 'stats' in data, "Response should contain stats"
        
        stats = data['stats']
        assert 'total' in stats, "Stats should have total"
        assert 'pending' in stats, "Stats should have pending count"
        assert 'reviewed' in stats, "Stats should have reviewed count"
        assert 'accepted' in stats, "Stats should have accepted count"
        assert 'rejected' in stats, "Stats should have rejected count"
        
        print(f"SUCCESS: Enterprise has {stats['total']} applications (pending: {stats['pending']}, accepted: {stats['accepted']})")
    
    def test_update_application_status_requires_auth(self):
        """Test PUT /api/enterprise/applications/{id}/status - requires auth"""
        response = requests.put(
            f"{BASE_URL}/api/enterprise/applications/fake-id/status",
            params={"status": "reviewed"}
        )
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("SUCCESS: Update application status requires authentication")
    
    def test_update_application_status(self, enterprise_token):
        """Test PUT /api/enterprise/applications/{id}/status - update status"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        # First get applications
        apps_response = requests.get(f"{BASE_URL}/api/enterprise/applications", headers=headers)
        data = apps_response.json()
        
        if not data.get('applications'):
            pytest.skip("No applications available to test status update")
        
        app_id = data['applications'][0]['id']
        original_status = data['applications'][0].get('status', 'pending')
        
        # Update to 'reviewed'
        response = requests.put(
            f"{BASE_URL}/api/enterprise/applications/{app_id}/status",
            params={"status": "reviewed"},
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        result = response.json()
        assert result.get('status') == 'reviewed' or 'message' in result, "Should confirm status update"
        print(f"SUCCESS: Application status updated from '{original_status}' to 'reviewed'")
    
    def test_update_application_invalid_status(self, enterprise_token):
        """Test PUT /api/enterprise/applications/{id}/status - invalid status"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        # First get applications
        apps_response = requests.get(f"{BASE_URL}/api/enterprise/applications", headers=headers)
        data = apps_response.json()
        
        if not data.get('applications'):
            pytest.skip("No applications available to test")
        
        app_id = data['applications'][0]['id']
        
        # Try invalid status
        response = requests.put(
            f"{BASE_URL}/api/enterprise/applications/{app_id}/status",
            params={"status": "invalid_status"},
            headers=headers
        )
        assert response.status_code == 400, f"Expected 400 for invalid status, got {response.status_code}"
        print("SUCCESS: Invalid status rejected correctly")


class TestBoostedAdvertisingAlgorithm:
    """Test boosted advertising public endpoint"""
    
    def test_get_public_advertising(self):
        """Test GET /api/advertising/public - get boosted ads"""
        response = requests.get(f"{BASE_URL}/api/advertising/public")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert 'ads' in data, "Response should contain ads"
        assert 'total' in data, "Response should contain total count"
        
        print(f"SUCCESS: Got {data['total']} boosted ads")
        
        # Verify ads are sorted by budget (if multiple ads)
        ads = data['ads']
        if len(ads) > 1:
            for i in range(len(ads) - 1):
                budget_current = ads[i].get('budget', 0)
                budget_next = ads[i + 1].get('budget', 0)
                # Higher budget should come first
                assert budget_current >= budget_next, f"Ads should be sorted by budget descending"
            print("SUCCESS: Ads are correctly sorted by budget (boost algorithm)")
    
    def test_get_public_advertising_with_placement(self):
        """Test GET /api/advertising/public?placement=homepage - filter by placement"""
        response = requests.get(f"{BASE_URL}/api/advertising/public", params={"placement": "homepage"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'ads' in data, "Response should contain ads"
        print(f"SUCCESS: Got {data['total']} ads for homepage placement")
    
    def test_get_public_advertising_with_limit(self):
        """Test GET /api/advertising/public?limit=5 - limit results"""
        response = requests.get(f"{BASE_URL}/api/advertising/public", params={"limit": 5})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert len(data['ads']) <= 5, "Should respect limit parameter"
        print(f"SUCCESS: Limit parameter works correctly")
    
    def test_track_ad_click(self):
        """Test POST /api/advertising/{ad_id}/click - track click"""
        # First get an ad
        ads_response = requests.get(f"{BASE_URL}/api/advertising/public")
        ads = ads_response.json().get('ads', [])
        
        if not ads:
            pytest.skip("No ads available to test click tracking")
        
        ad_id = ads[0]['id']
        
        response = requests.post(f"{BASE_URL}/api/advertising/{ad_id}/click")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        result = response.json()
        assert 'message' in result, "Should return confirmation message"
        print(f"SUCCESS: Click tracked for ad {ad_id}")
    
    def test_track_click_invalid_ad(self):
        """Test POST /api/advertising/{ad_id}/click - invalid ad ID"""
        response = requests.post(f"{BASE_URL}/api/advertising/invalid-ad-id/click")
        assert response.status_code == 404, f"Expected 404 for invalid ad, got {response.status_code}"
        print("SUCCESS: Invalid ad click returns 404")


class TestEnterpriseJobManagement:
    """Test enterprise job creation and management"""
    
    @pytest.fixture
    def enterprise_token(self):
        """Get enterprise authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Enterprise login failed: {response.text}")
        return response.json()['token']
    
    def test_list_enterprise_jobs(self, enterprise_token):
        """Test GET /api/enterprise/jobs - list enterprise's jobs"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        response = requests.get(f"{BASE_URL}/api/enterprise/jobs", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        jobs = data if isinstance(data, list) else data.get('jobs', [])
        print(f"SUCCESS: Enterprise has {len(jobs)} jobs")
    
    def test_create_job(self, enterprise_token):
        """Test POST /api/enterprise/jobs - create new job"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        
        job_data = {
            "title": f"TEST_Job_{uuid.uuid4().hex[:8]}",
            "description": "Test job description for automated testing",
            "type": "CDI",
            "location": "Lausanne",
            "salary_min": 5000,
            "salary_max": 7000,
            "requirements": "Test requirements"
        }
        
        response = requests.post(f"{BASE_URL}/api/enterprise/jobs", json=job_data, headers=headers)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        
        job = response.json()
        assert 'id' in job, "Job should have an ID"
        assert job['title'] == job_data['title'], "Job title should match"
        print(f"SUCCESS: Created job '{job['title']}' with ID {job['id']}")
        
        # Cleanup - delete the test job
        delete_response = requests.delete(f"{BASE_URL}/api/enterprise/jobs/{job['id']}", headers=headers)
        if delete_response.status_code == 200:
            print(f"CLEANUP: Deleted test job {job['id']}")


class TestClientDocumentsForCV:
    """Test client documents API for CV selection in job applications"""
    
    @pytest.fixture
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Client login failed: {response.text}")
        return response.json()['token']
    
    def test_list_client_documents(self, client_token):
        """Test GET /api/client/documents - list user's documents"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(f"{BASE_URL}/api/client/documents", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        documents = data.get('documents', data) if isinstance(data, dict) else data
        print(f"SUCCESS: User has {len(documents)} documents")
    
    def test_list_client_documents_cv_category(self, client_token):
        """Test GET /api/client/documents?category=cv - filter CVs"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        response = requests.get(f"{BASE_URL}/api/client/documents", params={"category": "cv"}, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        documents = data.get('documents', data) if isinstance(data, dict) else data
        print(f"SUCCESS: User has {len(documents)} CV documents")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
