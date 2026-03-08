#!/usr/bin/env python3
import requests
import sys
import json
from datetime import datetime

class TitelliAPITester:
    def __init__(self, base_url="https://image-fix-demo.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.enterprise_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
            self.failed_tests.append({"test": name, "error": details})

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make API request with error handling"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            return success, response.status_code, response_data

        except requests.exceptions.RequestException as e:
            return False, 0, {"error": str(e)}

    def test_health_check(self):
        """Test health endpoint"""
        success, status, data = self.make_request('GET', 'health')
        self.log_test("Health Check", success and data.get('status') == 'healthy', 
                     f"Status: {status}, Response: {data}")
        return success

    def test_categories_endpoints(self):
        """Test category endpoints"""
        # Test service categories
        success, status, data = self.make_request('GET', 'categories/services')
        services_ok = success and isinstance(data, list) and len(data) > 0
        self.log_test("Service Categories", services_ok, 
                     f"Status: {status}, Count: {len(data) if isinstance(data, list) else 0}")

        # Test product categories  
        success, status, data = self.make_request('GET', 'categories/products')
        products_ok = success and isinstance(data, list) and len(data) > 0
        self.log_test("Product Categories", products_ok,
                     f"Status: {status}, Count: {len(data) if isinstance(data, list) else 0}")

        return services_ok and products_ok

    def test_user_registration_client(self):
        """Test client registration"""
        test_data = {
            "email": f"test_client_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "Client",
            "phone": "+41123456789",
            "user_type": "client"
        }

        success, status, data = self.make_request('POST', 'auth/register', test_data, 200)
        
        if success and 'token' in data:
            self.token = data['token']
            self.user_id = data.get('user', {}).get('id')
            
        self.log_test("Client Registration", success and 'token' in data,
                     f"Status: {status}, Has token: {'token' in data}")
        return success

    def test_user_registration_enterprise(self):
        """Test enterprise registration"""
        test_data = {
            "email": f"test_enterprise_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "Enterprise",
            "phone": "+41123456789",
            "user_type": "entreprise"
        }

        success, status, data = self.make_request('POST', 'auth/register', test_data, 200)
        
        enterprise_token = None
        if success and 'token' in data:
            enterprise_token = data['token']
            
        self.log_test("Enterprise Registration", success and 'token' in data,
                     f"Status: {status}, Has token: {'token' in data}")
        return success, enterprise_token

    def test_user_login(self):
        """Test login with existing user"""
        if not self.token:
            self.log_test("Login Test", False, "No user registered to test login")
            return False

        # Test /auth/me endpoint
        success, status, data = self.make_request('GET', 'auth/me')
        self.log_test("Auth Me Endpoint", success and 'email' in data,
                     f"Status: {status}, Has user data: {'email' in data}")
        return success

    def test_enterprises_endpoints(self):
        """Test enterprise-related endpoints"""
        # Test list enterprises
        success, status, data = self.make_request('GET', 'enterprises')
        enterprises_ok = success and 'enterprises' in data
        self.log_test("List Enterprises", enterprises_ok,
                     f"Status: {status}, Has enterprises: {'enterprises' in data}")

        # Test with filters
        success, status, data = self.make_request('GET', 'enterprises?is_certified=true')
        certified_ok = success and 'enterprises' in data
        self.log_test("Certified Enterprises Filter", certified_ok,
                     f"Status: {status}")

        success, status, data = self.make_request('GET', 'enterprises?is_labeled=true')
        labeled_ok = success and 'enterprises' in data
        self.log_test("Labeled Enterprises Filter", labeled_ok,
                     f"Status: {status}")

        success, status, data = self.make_request('GET', 'enterprises?is_premium=true')
        premium_ok = success and 'enterprises' in data
        self.log_test("Premium Enterprises Filter", premium_ok,
                     f"Status: {status}")

        return enterprises_ok and certified_ok and labeled_ok and premium_ok

    def test_services_products_endpoints(self):
        """Test services and products endpoints"""
        # Test services
        success, status, data = self.make_request('GET', 'services-products?type=service')
        services_ok = success and 'items' in data
        self.log_test("List Services", services_ok,
                     f"Status: {status}, Has items: {'items' in data}")

        # Test products
        success, status, data = self.make_request('GET', 'services-products?type=product')
        products_ok = success and 'items' in data
        self.log_test("List Products", products_ok,
                     f"Status: {status}, Has items: {'items' in data}")

        return services_ok and products_ok

    def test_featured_endpoints(self):
        """Test featured content endpoints"""
        endpoints = [
            ('featured/tendances', 'Tendances'),
            ('featured/guests', 'Guests'),
            ('featured/offres', 'Offres'),
            ('featured/premium', 'Premium')
        ]

        all_ok = True
        for endpoint, name in endpoints:
            success, status, data = self.make_request('GET', endpoint)
            endpoint_ok = success and isinstance(data, list)
            self.log_test(f"Featured {name}", endpoint_ok,
                         f"Status: {status}, Is list: {isinstance(data, list)}")
            all_ok = all_ok and endpoint_ok

        return all_ok

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, status, data = self.make_request('GET', '')
        root_ok = success and 'message' in data
        self.log_test("Root API Endpoint", root_ok,
                     f"Status: {status}, Has message: {'message' in data}")
        return root_ok

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Titelli API Tests...")
        print(f"📍 Testing API: {self.api_url}")
        print("=" * 60)

        # Basic connectivity tests
        self.test_health_check()
        self.test_root_endpoint()
        
        # Category tests
        self.test_categories_endpoints()
        
        # Auth tests
        self.test_user_registration_client()
        self.test_user_login()
        
        # Enterprise registration test
        enterprise_success, enterprise_token = self.test_user_registration_enterprise()
        
        # Enterprise endpoints
        self.test_enterprises_endpoints()
        
        # Services/Products endpoints
        self.test_services_products_endpoints()
        
        # Featured content endpoints
        self.test_featured_endpoints()

        # Print summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"  - {test['test']}: {test['error']}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"✨ Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = TitelliAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())