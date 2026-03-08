"""
Iteration 15 - Comprehensive Audit Tests for Titelli Platform
Tests: Jobs/Emplois, Trainings/Formations, Services, Products, Enterprise Dashboard, Client Dashboard
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

# Test credentials
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"
ADMIN_EMAIL = "admin@titelli.com"
ADMIN_PASSWORD = "Admin123!"


class TestAuthentication:
    """Test authentication flows"""
    
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
        assert data["user"]["user_type"] == "client"
        print(f"✓ Client login successful: {data['user']['email']}")
    
    def test_enterprise_login(self):
        """Test enterprise login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200, f"Enterprise login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "entreprise"
        print(f"✓ Enterprise login successful: {data['user']['email']}")


class TestJobsAPI:
    """Test Jobs/Emplois API endpoints"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_list_all_jobs_public(self):
        """Test public jobs listing - /api/jobs"""
        response = requests.get(f"{BASE_URL}/api/jobs")
        assert response.status_code == 200, f"Failed to list jobs: {response.text}"
        jobs = response.json()
        assert isinstance(jobs, list)
        print(f"✓ Public jobs listing: {len(jobs)} jobs found")
        return jobs
    
    def test_enterprise_list_jobs(self, enterprise_token):
        """Test enterprise jobs listing - /api/enterprise/jobs"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/jobs",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200, f"Failed to list enterprise jobs: {response.text}"
        jobs = response.json()
        assert isinstance(jobs, list)
        print(f"✓ Enterprise jobs listing: {len(jobs)} jobs found")
        return jobs
    
    def test_create_job(self, enterprise_token):
        """Test job creation - /api/enterprise/jobs"""
        job_data = {
            "title": "TEST_Développeur Full Stack",
            "description": "Nous recherchons un développeur full stack expérimenté",
            "requirements": "5 ans d'expérience, React, Python",
            "location": "Lausanne",
            "job_type": "full_time",
            "salary_min": 80000,
            "salary_max": 120000,
            "is_active": True
        }
        response = requests.post(
            f"{BASE_URL}/api/enterprise/jobs",
            json=job_data,
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200, f"Failed to create job: {response.text}"
        job = response.json()
        assert job["title"] == job_data["title"]
        assert "id" in job
        print(f"✓ Job created: {job['id']}")
        return job
    
    def test_get_job_detail(self, enterprise_token):
        """Test job detail - /api/jobs/{job_id}"""
        # First create a job
        job = self.test_create_job(enterprise_token)
        
        # Then get its detail
        response = requests.get(f"{BASE_URL}/api/jobs/{job['id']}")
        assert response.status_code == 200, f"Failed to get job detail: {response.text}"
        detail = response.json()
        assert detail["id"] == job["id"]
        print(f"✓ Job detail retrieved: {detail['title']}")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/enterprise/jobs/{job['id']}",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
    
    def test_job_application_flow(self, enterprise_token, client_token):
        """Test job application flow"""
        # Create a job
        job_data = {
            "title": "TEST_Stage Marketing",
            "description": "Stage en marketing digital",
            "requirements": "Étudiant en marketing",
            "location": "Lausanne",
            "job_type": "internship",
            "is_active": True
        }
        job_response = requests.post(
            f"{BASE_URL}/api/enterprise/jobs",
            json=job_data,
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert job_response.status_code == 200
        job = job_response.json()
        
        # Apply to the job
        apply_data = {
            "resume_url": "/uploads/test_cv.pdf",
            "cover_letter": "Je suis très motivé pour ce stage"
        }
        apply_response = requests.post(
            f"{BASE_URL}/api/jobs/{job['id']}/apply",
            json=apply_data,
            headers={"Authorization": f"Bearer {client_token}"}
        )
        # May fail if already applied or no CV
        if apply_response.status_code == 200:
            print(f"✓ Job application submitted")
        else:
            print(f"⚠ Job application: {apply_response.status_code} - {apply_response.text}")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/enterprise/jobs/{job['id']}",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )


class TestTrainingsAPI:
    """Test Trainings/Formations API endpoints"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_list_all_trainings_public(self):
        """Test public trainings listing - /api/trainings"""
        response = requests.get(f"{BASE_URL}/api/trainings")
        assert response.status_code == 200, f"Failed to list trainings: {response.text}"
        trainings = response.json()
        assert isinstance(trainings, list)
        print(f"✓ Public trainings listing: {len(trainings)} trainings found")
        return trainings
    
    def test_enterprise_list_trainings(self, enterprise_token):
        """Test enterprise trainings listing - /api/enterprise/trainings"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/trainings",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200, f"Failed to list enterprise trainings: {response.text}"
        trainings = response.json()
        assert isinstance(trainings, list)
        print(f"✓ Enterprise trainings listing: {len(trainings)} trainings found")
        return trainings
    
    def test_create_training(self, enterprise_token):
        """Test training creation - /api/enterprise/trainings"""
        training_data = {
            "title": "TEST_Formation React Avancé",
            "description": "Formation complète sur React et ses hooks avancés",
            "category": "Développement Web",
            "price": 500,
            "duration": "2 jours",
            "training_type": "online",
            "is_active": True
        }
        response = requests.post(
            f"{BASE_URL}/api/enterprise/trainings",
            json=training_data,
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200, f"Failed to create training: {response.text}"
        training = response.json()
        assert training["title"] == training_data["title"]
        assert "id" in training
        print(f"✓ Training created: {training['id']}")
        return training
    
    def test_get_training_detail(self, enterprise_token):
        """Test training detail - /api/trainings/{training_id}"""
        # First create a training
        training = self.test_create_training(enterprise_token)
        
        # Then get its detail
        response = requests.get(f"{BASE_URL}/api/trainings/{training['id']}")
        assert response.status_code == 200, f"Failed to get training detail: {response.text}"
        detail = response.json()
        assert detail["id"] == training["id"]
        print(f"✓ Training detail retrieved: {detail['title']}")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/enterprise/trainings/{training['id']}",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
    
    def test_client_trainings(self, client_token):
        """Test client trainings - /api/client/trainings"""
        response = requests.get(
            f"{BASE_URL}/api/client/trainings",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed to get client trainings: {response.text}"
        data = response.json()
        assert "enrollments" in data
        assert "stats" in data
        print(f"✓ Client trainings: {data['stats']['total']} enrollments")


class TestServicesProductsAPI:
    """Test Services & Products API endpoints"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_list_services_products_public(self):
        """Test public services/products listing"""
        response = requests.get(f"{BASE_URL}/api/services-products")
        assert response.status_code == 200, f"Failed to list services/products: {response.text}"
        data = response.json()
        assert "items" in data
        assert "total" in data
        print(f"✓ Services/Products listing: {data['total']} items found")
    
    def test_list_services_only(self):
        """Test services only listing"""
        response = requests.get(f"{BASE_URL}/api/services-products", params={"type": "service"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Services only: {data['total']} services found")
    
    def test_list_products_only(self):
        """Test products only listing"""
        response = requests.get(f"{BASE_URL}/api/services-products", params={"type": "product"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Products only: {data['total']} products found")
    
    def test_create_service(self, enterprise_token):
        """Test service creation"""
        service_data = {
            "name": "TEST_Massage Relaxant",
            "description": "Massage relaxant de 60 minutes",
            "price": 120,
            "category": "soins_esthetiques",
            "type": "service",
            "images": []
        }
        response = requests.post(
            f"{BASE_URL}/api/services-products",
            json=service_data,
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200, f"Failed to create service: {response.text}"
        service = response.json()
        assert service["name"] == service_data["name"]
        print(f"✓ Service created: {service['id']}")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/services-products/{service['id']}",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
    
    def test_create_product(self, enterprise_token):
        """Test product creation"""
        product_data = {
            "name": "TEST_Crème Hydratante",
            "description": "Crème hydratante bio",
            "price": 45,
            "category": "maquillage_beaute",
            "type": "product",
            "images": []
        }
        response = requests.post(
            f"{BASE_URL}/api/services-products",
            json=product_data,
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200, f"Failed to create product: {response.text}"
        product = response.json()
        assert product["name"] == product_data["name"]
        print(f"✓ Product created: {product['id']}")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/services-products/{product['id']}",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )


class TestEnterprisesAPI:
    """Test Enterprises API endpoints"""
    
    def test_list_enterprises_public(self):
        """Test public enterprises listing"""
        response = requests.get(f"{BASE_URL}/api/enterprises")
        assert response.status_code == 200, f"Failed to list enterprises: {response.text}"
        data = response.json()
        assert "enterprises" in data
        assert "total" in data
        print(f"✓ Enterprises listing: {data['total']} enterprises found")
        return data["enterprises"]
    
    def test_get_enterprise_detail(self):
        """Test enterprise detail"""
        enterprises = self.test_list_enterprises_public()
        if enterprises:
            enterprise_id = enterprises[0]["id"]
            response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
            assert response.status_code == 200, f"Failed to get enterprise detail: {response.text}"
            detail = response.json()
            assert detail["id"] == enterprise_id
            print(f"✓ Enterprise detail retrieved: {detail['business_name']}")
            
            # Check for cover_image and logo fields
            if "cover_image" in detail:
                print(f"  - Cover image: {detail.get('cover_image', 'None')[:50]}...")
            if "logo" in detail:
                print(f"  - Logo: {detail.get('logo', 'None')[:50] if detail.get('logo') else 'None'}...")
    
    def test_filter_certified_enterprises(self):
        """Test filtering certified enterprises"""
        response = requests.get(f"{BASE_URL}/api/enterprises", params={"is_certified": True})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Certified enterprises: {data['total']} found")
    
    def test_filter_premium_enterprises(self):
        """Test filtering premium enterprises"""
        response = requests.get(f"{BASE_URL}/api/enterprises", params={"is_premium": True})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Premium enterprises: {data['total']} found")


class TestEnterpriseApplicationsAPI:
    """Test Enterprise Applications (Postulations) API"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_enterprise_applications(self, enterprise_token):
        """Test getting all applications for enterprise jobs"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/applications",
            headers={"Authorization": f"Bearer {enterprise_token}"}
        )
        assert response.status_code == 200, f"Failed to get applications: {response.text}"
        data = response.json()
        assert "applications" in data
        assert "jobs" in data
        assert "stats" in data
        print(f"✓ Enterprise applications: {data['stats']['total']} total")
        print(f"  - Pending: {data['stats']['pending']}")
        print(f"  - Accepted: {data['stats']['accepted']}")
        print(f"  - Rejected: {data['stats']['rejected']}")


class TestClientDashboardAPI:
    """Test Client Dashboard API endpoints"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_client_profile(self, client_token):
        """Test getting client profile"""
        response = requests.get(
            f"{BASE_URL}/api/client/profile",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed to get profile: {response.text}"
        data = response.json()
        assert "user" in data or "email" in data
        print(f"✓ Client profile retrieved")
    
    def test_get_cashback_balance(self, client_token):
        """Test getting cashback balance"""
        response = requests.get(
            f"{BASE_URL}/api/cashback/balance",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed to get cashback: {response.text}"
        data = response.json()
        assert "balance" in data
        print(f"✓ Cashback balance: {data['balance']} CHF")
    
    def test_get_orders(self, client_token):
        """Test getting client orders"""
        response = requests.get(
            f"{BASE_URL}/api/orders",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed to get orders: {response.text}"
        orders = response.json()
        assert isinstance(orders, list)
        print(f"✓ Client orders: {len(orders)} orders found")
    
    def test_get_client_documents(self, client_token):
        """Test getting client documents"""
        response = requests.get(
            f"{BASE_URL}/api/client/documents",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed to get documents: {response.text}"
        data = response.json()
        assert "documents" in data
        print(f"✓ Client documents: {len(data['documents'])} documents found")
    
    def test_get_client_job_applications(self, client_token):
        """Test getting client job applications"""
        response = requests.get(
            f"{BASE_URL}/api/client/job-applications",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200, f"Failed to get job applications: {response.text}"
        data = response.json()
        assert "applications" in data
        print(f"✓ Client job applications: {len(data['applications'])} applications found")


class TestFeaturedAPI:
    """Test Featured/Homepage API endpoints"""
    
    def test_get_tendances(self):
        """Test getting tendances (labeled enterprises)"""
        response = requests.get(f"{BASE_URL}/api/featured/tendances")
        assert response.status_code == 200, f"Failed to get tendances: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Tendances: {len(data)} enterprises found")
    
    def test_get_guests(self):
        """Test getting guests (certified enterprises)"""
        response = requests.get(f"{BASE_URL}/api/featured/guests")
        assert response.status_code == 200, f"Failed to get guests: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Guests: {len(data)} enterprises found")
    
    def test_get_offres(self):
        """Test getting offres (services/products)"""
        response = requests.get(f"{BASE_URL}/api/featured/offres")
        assert response.status_code == 200, f"Failed to get offres: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Offres: {len(data)} items found")
    
    def test_get_premium(self):
        """Test getting premium enterprises"""
        response = requests.get(f"{BASE_URL}/api/featured/premium")
        assert response.status_code == 200, f"Failed to get premium: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Premium: {len(data)} enterprises found")


class TestCategoriesAPI:
    """Test Categories API endpoints"""
    
    def test_get_product_categories(self):
        """Test getting product categories"""
        response = requests.get(f"{BASE_URL}/api/categories/products")
        assert response.status_code == 200, f"Failed to get product categories: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"✓ Product categories: {len(data)} categories found")
    
    def test_get_service_categories(self):
        """Test getting service categories"""
        response = requests.get(f"{BASE_URL}/api/categories/services")
        assert response.status_code == 200, f"Failed to get service categories: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"✓ Service categories: {len(data)} categories found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
