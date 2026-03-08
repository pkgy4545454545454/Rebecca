#!/usr/bin/env python3
import requests
import sys

def test_specific_login_credentials():
    """Test the specific login credentials mentioned in requirements"""
    base_url = "https://image-fix-demo.preview.emergentagent.com/api"
    
    # Test credentials from requirements
    test_cases = [
        {
            "name": "Client Login",
            "email": "test@example.com",
            "password": "Test123!",
            "expected_user_type": "client"
        },
        {
            "name": "Enterprise Login", 
            "email": "spa.luxury@titelli.com",
            "password": "Demo123!",
            "expected_user_type": "entreprise"
        }
    ]
    
    print("🔐 Testing Specific Login Credentials...")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n🧪 Testing {test_case['name']}")
        print(f"📧 Email: {test_case['email']}")
        
        try:
            response = requests.post(
                f"{base_url}/auth/login",
                json={
                    "email": test_case['email'],
                    "password": test_case['password']
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    user = data['user']
                    user_type = user.get('user_type')
                    
                    if user_type == test_case['expected_user_type']:
                        print(f"✅ {test_case['name']} - SUCCESS")
                        print(f"   User Type: {user_type}")
                        print(f"   User ID: {user.get('id')}")
                        print(f"   Name: {user.get('first_name')} {user.get('last_name')}")
                    else:
                        print(f"❌ {test_case['name']} - WRONG USER TYPE")
                        print(f"   Expected: {test_case['expected_user_type']}, Got: {user_type}")
                else:
                    print(f"❌ {test_case['name']} - INVALID RESPONSE FORMAT")
                    print(f"   Response: {data}")
            else:
                print(f"❌ {test_case['name']} - FAILED")
                print(f"   Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ {test_case['name']} - ERROR: {str(e)}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_specific_login_credentials()