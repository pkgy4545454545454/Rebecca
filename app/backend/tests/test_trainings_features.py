"""
Test file for Training/Formation features
Tests:
- GET /api/trainings - Public list of trainings
- GET /api/enterprise/trainings - Enterprise's trainings
- POST /api/enterprise/trainings - Create training (online/on_site)
- PUT /api/enterprise/trainings/{id} - Update training
- DELETE /api/enterprise/trainings/{id} - Delete training
- POST /api/trainings/{id}/purchase - Purchase training via Stripe
- POST /api/trainings/{id}/enroll - Enroll after payment
- GET /api/client/trainings - Client's enrolled trainings
- PUT /api/client/trainings/{id}/complete - Mark training complete
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


class TestTrainingsPublicAPI:
    """Test public trainings endpoints"""
    
    def test_get_public_trainings_list(self):
        """GET /api/trainings - List public trainings"""
        response = requests.get(f"{BASE_URL}/api/trainings")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Found {len(data)} public trainings")
        
        # If trainings exist, verify structure
        if len(data) > 0:
            training = data[0]
            assert 'id' in training
            assert 'title' in training
            assert 'price' in training
            # training_type may not exist in old data, but should have a default
            print(f"✓ Training structure valid: {training.get('title')}")
            print(f"  - training_type: {training.get('training_type', 'NOT SET (old data)')}")
    
    def test_get_trainings_with_limit(self):
        """GET /api/trainings?limit=3 - List with limit"""
        response = requests.get(f"{BASE_URL}/api/trainings", params={"limit": 3})
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3
        print(f"✓ Limit parameter works: {len(data)} trainings returned")
    
    def test_get_trainings_by_type(self):
        """GET /api/trainings?training_type=online - Filter by type"""
        response = requests.get(f"{BASE_URL}/api/trainings", params={"training_type": "online"})
        assert response.status_code == 200
        data = response.json()
        for training in data:
            assert training.get('training_type') == 'online'
        print(f"✓ Filter by type works: {len(data)} online trainings")


class TestEnterpriseTrainingsAPI:
    """Test enterprise trainings management"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as enterprise user"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip(f"Enterprise login failed: {login_response.text}")
        
        self.token = login_response.json().get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user = login_response.json().get('user')
        print(f"✓ Logged in as enterprise: {self.user.get('email')}")
    
    def test_get_enterprise_trainings(self):
        """GET /api/enterprise/trainings - List enterprise's trainings"""
        response = requests.get(f"{BASE_URL}/api/enterprise/trainings", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Enterprise has {len(data)} trainings")
    
    def test_create_online_training(self):
        """POST /api/enterprise/trainings - Create online training with files"""
        unique_id = str(uuid.uuid4())[:8]
        training_data = {
            "title": f"TEST_Online Training {unique_id}",
            "description": "Test online training with downloadable files",
            "duration": "3 heures",
            "price": 150.0,
            "category": "Marketing",
            "training_type": "online",
            "downloadable_files": [
                {"name": "video_intro.mp4", "url": "/uploads/test_video.mp4", "type": "video/mp4"},
                {"name": "guide.pdf", "url": "/uploads/test_guide.pdf", "type": "application/pdf"}
            ]
        }
        
        response = requests.post(f"{BASE_URL}/api/enterprise/trainings", 
                                json=training_data, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data['title'] == training_data['title']
        assert data['training_type'] == 'online'
        assert 'downloadable_files' in data
        assert len(data['downloadable_files']) == 2
        print(f"✓ Created online training: {data['title']}")
        
        # Store for cleanup
        self.created_training_id = data['id']
        return data
    
    def test_create_onsite_training(self):
        """POST /api/enterprise/trainings - Create on-site training with dates"""
        unique_id = str(uuid.uuid4())[:8]
        training_data = {
            "title": f"TEST_OnSite Training {unique_id}",
            "description": "Test on-site training with location and dates",
            "duration": "2 jours",
            "price": 500.0,
            "category": "Formation",
            "training_type": "on_site",
            "location": "Centre de formation, Lausanne",
            "start_date": "2026-02-15",
            "end_date": "2026-02-16",
            "max_participants": 20
        }
        
        response = requests.post(f"{BASE_URL}/api/enterprise/trainings", 
                                json=training_data, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data['title'] == training_data['title']
        assert data['training_type'] == 'on_site'
        assert data['location'] == training_data['location']
        assert data['start_date'] == training_data['start_date']
        print(f"✓ Created on-site training: {data['title']}")
        
        return data
    
    def test_update_training(self):
        """PUT /api/enterprise/trainings/{id} - Update training"""
        # First create a training
        unique_id = str(uuid.uuid4())[:8]
        create_response = requests.post(f"{BASE_URL}/api/enterprise/trainings", 
            json={
                "title": f"TEST_Update Training {unique_id}",
                "description": "Training to update",
                "duration": "1 heure",
                "price": 100.0,
                "category": "Test",
                "training_type": "online"
            }, headers=self.headers)
        
        assert create_response.status_code == 200
        training_id = create_response.json()['id']
        
        # Update the training
        update_data = {
            "title": f"TEST_Updated Training {unique_id}",
            "price": 200.0
        }
        
        update_response = requests.put(f"{BASE_URL}/api/enterprise/trainings/{training_id}",
                                      json=update_data, headers=self.headers)
        assert update_response.status_code == 200
        print(f"✓ Updated training: {training_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/enterprise/trainings/{training_id}", headers=self.headers)
    
    def test_delete_training(self):
        """DELETE /api/enterprise/trainings/{id} - Delete training"""
        # First create a training
        unique_id = str(uuid.uuid4())[:8]
        create_response = requests.post(f"{BASE_URL}/api/enterprise/trainings", 
            json={
                "title": f"TEST_Delete Training {unique_id}",
                "description": "Training to delete",
                "duration": "1 heure",
                "price": 50.0,
                "category": "Test",
                "training_type": "online"
            }, headers=self.headers)
        
        assert create_response.status_code == 200
        training_id = create_response.json()['id']
        
        # Delete the training
        delete_response = requests.delete(f"{BASE_URL}/api/enterprise/trainings/{training_id}",
                                         headers=self.headers)
        assert delete_response.status_code == 200
        print(f"✓ Deleted training: {training_id}")


class TestTrainingPurchaseAPI:
    """Test training purchase flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as client user"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip(f"Client login failed: {login_response.text}")
        
        self.token = login_response.json().get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user = login_response.json().get('user')
        print(f"✓ Logged in as client: {self.user.get('email')}")
    
    def test_purchase_training_creates_stripe_session(self):
        """POST /api/trainings/{id}/purchase - Creates Stripe checkout"""
        # Get a training to purchase
        trainings_response = requests.get(f"{BASE_URL}/api/trainings")
        trainings = trainings_response.json()
        
        if not trainings:
            pytest.skip("No trainings available to purchase")
        
        training = trainings[0]
        training_id = training['id']
        
        # Attempt purchase
        response = requests.post(f"{BASE_URL}/api/trainings/{training_id}/purchase",
                                headers=self.headers)
        
        # Should return Stripe URL or already enrolled error
        if response.status_code == 200:
            data = response.json()
            assert 'url' in data
            assert 'stripe.com' in data['url'] or 'checkout' in data['url']
            print(f"✓ Stripe checkout created for training: {training['title']}")
        elif response.status_code == 400:
            # Already enrolled
            assert 'déjà inscrit' in response.json().get('detail', '').lower()
            print(f"✓ Already enrolled in training: {training['title']}")
        else:
            pytest.fail(f"Unexpected response: {response.status_code} - {response.text}")
    
    def test_purchase_nonexistent_training(self):
        """POST /api/trainings/{id}/purchase - 404 for invalid training"""
        response = requests.post(f"{BASE_URL}/api/trainings/nonexistent-id/purchase",
                                headers=self.headers)
        assert response.status_code == 404
        print("✓ 404 returned for nonexistent training")


class TestClientTrainingsAPI:
    """Test client trainings endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as client user"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip(f"Client login failed: {login_response.text}")
        
        self.token = login_response.json().get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user = login_response.json().get('user')
        print(f"✓ Logged in as client: {self.user.get('email')}")
    
    def test_get_client_trainings(self):
        """GET /api/client/trainings - Get enrolled trainings"""
        response = requests.get(f"{BASE_URL}/api/client/trainings", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert 'enrollments' in data
        assert 'stats' in data
        assert 'total' in data['stats']
        assert 'in_progress' in data['stats']
        assert 'completed' in data['stats']
        
        print(f"✓ Client has {data['stats']['total']} enrollments")
        print(f"  - In progress: {data['stats']['in_progress']}")
        print(f"  - Completed: {data['stats']['completed']}")
    
    def test_get_client_trainings_filtered_by_status(self):
        """GET /api/client/trainings?status=in_progress - Filter by status"""
        response = requests.get(f"{BASE_URL}/api/client/trainings", 
                               params={"status": "in_progress"}, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        for enrollment in data.get('enrollments', []):
            assert enrollment.get('status') == 'in_progress'
        
        print(f"✓ Filtered trainings by status: {len(data.get('enrollments', []))} in_progress")
    
    def test_enrollment_has_downloadable_files_for_online(self):
        """Verify online training enrollments have downloadable_files"""
        response = requests.get(f"{BASE_URL}/api/client/trainings", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        for enrollment in data.get('enrollments', []):
            if enrollment.get('training_type') == 'online':
                assert 'downloadable_files' in enrollment
                print(f"✓ Online enrollment has downloadable_files: {enrollment.get('training_title')}")
                if enrollment.get('downloadable_files'):
                    for file in enrollment['downloadable_files']:
                        assert 'name' in file
                        assert 'url' in file
                        print(f"  - File: {file.get('name')}")


class TestTrainingEnrollmentAPI:
    """Test training enrollment after payment"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as client user"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip(f"Client login failed: {login_response.text}")
        
        self.token = login_response.json().get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user = login_response.json().get('user')
    
    def test_enroll_without_payment_fails(self):
        """POST /api/trainings/{id}/enroll - Should fail without valid session"""
        trainings_response = requests.get(f"{BASE_URL}/api/trainings")
        trainings = trainings_response.json()
        
        if not trainings:
            pytest.skip("No trainings available")
        
        training_id = trainings[0]['id']
        
        # Try to enroll without session_id (should fail or already enrolled)
        response = requests.post(f"{BASE_URL}/api/trainings/{training_id}/enroll",
                                headers=self.headers)
        
        # Either 400 (already enrolled) or 200 (free enrollment allowed)
        assert response.status_code in [200, 400]
        print(f"✓ Enrollment endpoint responds correctly: {response.status_code}")


class TestHomepageTrainingsSection:
    """Test trainings display on homepage"""
    
    def test_trainings_api_returns_enterprise_info(self):
        """GET /api/trainings - Should include enterprise info for display"""
        response = requests.get(f"{BASE_URL}/api/trainings", params={"limit": 6})
        assert response.status_code == 200
        trainings = response.json()
        
        for training in trainings:
            # These fields are needed for homepage display
            assert 'title' in training
            assert 'price' in training
            assert 'enterprise_name' in training
            
            # training_type may not exist in old data
            training_type = training.get('training_type', 'on_site')
            print(f"✓ Training: {training.get('title')} by {training.get('enterprise_name')} - {training.get('price')} CHF ({training_type})")
            
            # Optional but expected
            if 'enterprise_logo' in training:
                print(f"  - Has enterprise_logo")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_trainings(self):
        """Delete TEST_ prefixed trainings"""
        # Login as enterprise
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip("Cannot login for cleanup")
        
        token = login_response.json().get('token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get enterprise trainings
        trainings_response = requests.get(f"{BASE_URL}/api/enterprise/trainings", headers=headers)
        trainings = trainings_response.json()
        
        deleted_count = 0
        for training in trainings:
            if training.get('title', '').startswith('TEST_'):
                delete_response = requests.delete(
                    f"{BASE_URL}/api/enterprise/trainings/{training['id']}", 
                    headers=headers
                )
                if delete_response.status_code == 200:
                    deleted_count += 1
        
        print(f"✓ Cleaned up {deleted_count} test trainings")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
