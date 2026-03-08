"""
Test suite for IA Marketing APIs - Titelli Marketplace
Tests: IA Campaigns, Influencers, Client Invitations, Commercial Gestures
All APIs should persist data in MongoDB (PRODUCTION mode - no mocked data)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"

class TestAuthAndSetup:
    """Authentication tests to get token for subsequent tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for enterprise user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        return data["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_login_enterprise_user(self):
        """Test login with enterprise credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "entreprise"
        print(f"✓ Enterprise login successful: {data['user']['email']}")


class TestInfluencersAPI:
    """Test /api/influencers endpoint - should return real data from MongoDB"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_influencers_list(self):
        """Test GET /api/influencers - should return list of influencers from DB"""
        response = requests.get(f"{BASE_URL}/api/influencers")
        assert response.status_code == 200
        data = response.json()
        
        assert "influencers" in data
        assert "total" in data
        assert isinstance(data["influencers"], list)
        
        # Should have seeded influencers
        assert len(data["influencers"]) > 0, "No influencers found - seeding may have failed"
        
        # Verify influencer structure
        influencer = data["influencers"][0]
        required_fields = ["id", "name", "image", "category", "followers", "engagement_rate", "price"]
        for field in required_fields:
            assert field in influencer, f"Missing field: {field}"
        
        print(f"✓ Found {len(data['influencers'])} influencers in database")
        for inf in data["influencers"][:3]:
            print(f"  - {inf['name']} ({inf['category']}) - {inf['followers']} followers")
    
    def test_get_influencers_by_category(self):
        """Test filtering influencers by category"""
        response = requests.get(f"{BASE_URL}/api/influencers", params={"category": "Lifestyle"})
        assert response.status_code == 200
        data = response.json()
        
        # All returned influencers should be in Lifestyle category
        for inf in data["influencers"]:
            assert inf["category"] == "Lifestyle", f"Wrong category: {inf['category']}"
        
        print(f"✓ Category filter working - found {len(data['influencers'])} Lifestyle influencers")
    
    def test_get_influencer_collaborations(self, auth_headers):
        """Test GET /api/enterprise/influencer-collaborations"""
        response = requests.get(f"{BASE_URL}/api/enterprise/influencer-collaborations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "collaborations" in data
        assert "stats" in data
        assert "total_collaborations" in data["stats"]
        assert "active_collaborations" in data["stats"]
        assert "total_investment" in data["stats"]
        
        print(f"✓ Collaborations endpoint working - {data['stats']['total_collaborations']} total collaborations")
    
    def test_create_influencer_collaboration(self, auth_headers):
        """Test POST /api/enterprise/influencer-collaborations"""
        # First get an influencer ID
        inf_response = requests.get(f"{BASE_URL}/api/influencers")
        influencers = inf_response.json()["influencers"]
        assert len(influencers) > 0, "No influencers available"
        
        influencer_id = influencers[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/enterprise/influencer-collaborations",
            params={
                "influencer_id": influencer_id,
                "message": "Test collaboration request",
                "budget": 500
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["influencer_id"] == influencer_id
        assert data["status"] == "pending"
        assert "influencer" in data
        
        print(f"✓ Created collaboration with {data['influencer']['name']}")
        return data["id"]


class TestIACampaignsAPI:
    """Test /api/enterprise/ia-campaigns CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_ia_campaigns_list(self, auth_headers):
        """Test GET /api/enterprise/ia-campaigns"""
        response = requests.get(f"{BASE_URL}/api/enterprise/ia-campaigns", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "campaigns" in data
        assert "stats" in data
        assert "total_reach" in data["stats"]
        assert "total_engagement" in data["stats"]
        assert "total_conversions" in data["stats"]
        
        print(f"✓ IA Campaigns list working - {len(data['campaigns'])} campaigns, reach: {data['stats']['total_reach']}")
    
    def test_create_ia_campaign(self, auth_headers):
        """Test POST /api/enterprise/ia-campaigns"""
        campaign_data = {
            "name": f"TEST_Campaign_{uuid.uuid4().hex[:8]}",
            "age_range": "25-45",
            "gender": "all",
            "interests": ["Bien-être", "Mode"],
            "behavior": ["Clients fidèles"],
            "location": "lausanne",
            "budget": "medium"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/enterprise/ia-campaigns",
            json=campaign_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["name"] == campaign_data["name"]
        assert data["status"] == "active"
        assert data["reach"] > 0, "Campaign should have calculated reach"
        assert data["engagement"] > 0, "Campaign should have calculated engagement"
        
        print(f"✓ Created IA campaign: {data['name']} with reach {data['reach']}")
        return data["id"]
    
    def test_toggle_ia_campaign(self, auth_headers):
        """Test PUT /api/enterprise/ia-campaigns/{id}/toggle"""
        # First create a campaign
        campaign_data = {
            "name": f"TEST_Toggle_{uuid.uuid4().hex[:8]}",
            "age_range": "25-45",
            "gender": "all",
            "interests": [],
            "behavior": [],
            "location": "lausanne",
            "budget": "medium"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/enterprise/ia-campaigns",
            json=campaign_data,
            headers=auth_headers
        )
        campaign_id = create_response.json()["id"]
        
        # Toggle to paused
        toggle_response = requests.put(
            f"{BASE_URL}/api/enterprise/ia-campaigns/{campaign_id}/toggle",
            headers=auth_headers
        )
        assert toggle_response.status_code == 200
        assert toggle_response.json()["status"] == "paused"
        
        # Toggle back to active
        toggle_response2 = requests.put(
            f"{BASE_URL}/api/enterprise/ia-campaigns/{campaign_id}/toggle",
            headers=auth_headers
        )
        assert toggle_response2.status_code == 200
        assert toggle_response2.json()["status"] == "active"
        
        print(f"✓ Campaign toggle working (active -> paused -> active)")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/enterprise/ia-campaigns/{campaign_id}", headers=auth_headers)
    
    def test_delete_ia_campaign(self, auth_headers):
        """Test DELETE /api/enterprise/ia-campaigns/{id}"""
        # Create a campaign to delete
        campaign_data = {
            "name": f"TEST_Delete_{uuid.uuid4().hex[:8]}",
            "age_range": "25-45",
            "gender": "all",
            "interests": [],
            "behavior": [],
            "location": "lausanne",
            "budget": "medium"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/enterprise/ia-campaigns",
            json=campaign_data,
            headers=auth_headers
        )
        campaign_id = create_response.json()["id"]
        
        # Delete
        delete_response = requests.delete(
            f"{BASE_URL}/api/enterprise/ia-campaigns/{campaign_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200
        
        # Verify deletion by checking list
        list_response = requests.get(f"{BASE_URL}/api/enterprise/ia-campaigns", headers=auth_headers)
        campaigns = list_response.json()["campaigns"]
        assert not any(c["id"] == campaign_id for c in campaigns), "Campaign should be deleted"
        
        print(f"✓ Campaign deletion working")


class TestClientInvitationsAPI:
    """Test /api/enterprise/invitations CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_invitations_list(self, auth_headers):
        """Test GET /api/enterprise/invitations"""
        response = requests.get(f"{BASE_URL}/api/enterprise/invitations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "invitations" in data
        assert "stats" in data
        assert "total_sent" in data["stats"]
        assert "total_opened" in data["stats"]
        assert "total_responses" in data["stats"]
        assert "open_rate" in data["stats"]
        assert "response_rate" in data["stats"]
        
        print(f"✓ Invitations list working - {len(data['invitations'])} invitations, {data['stats']['total_sent']} sent")
    
    def test_create_invitation(self, auth_headers):
        """Test POST /api/enterprise/invitations"""
        invitation_data = {
            "type": "question",
            "title": f"TEST_Invitation_{uuid.uuid4().hex[:8]}",
            "message": "Avez-vous apprécié notre dernier service ?",
            "target_audience": "all",
            "incentive": "10% de réduction"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/enterprise/invitations",
            json=invitation_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["title"] == invitation_data["title"]
        assert data["type"] == "question"
        assert data["sent_count"] > 0, "Should have simulated sent count"
        assert data["opened_count"] > 0, "Should have simulated opened count"
        
        print(f"✓ Created invitation: {data['title']} - sent to {data['sent_count']} clients")
        return data["id"]
    
    def test_delete_invitation(self, auth_headers):
        """Test DELETE /api/enterprise/invitations/{id}"""
        # Create an invitation to delete
        invitation_data = {
            "type": "reminder",
            "title": f"TEST_Delete_{uuid.uuid4().hex[:8]}",
            "message": "Test message for deletion",
            "target_audience": "loyal",
            "incentive": ""
        }
        create_response = requests.post(
            f"{BASE_URL}/api/enterprise/invitations",
            json=invitation_data,
            headers=auth_headers
        )
        invitation_id = create_response.json()["id"]
        
        # Delete
        delete_response = requests.delete(
            f"{BASE_URL}/api/enterprise/invitations/{invitation_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200
        
        print(f"✓ Invitation deletion working")


class TestCommercialGesturesAPI:
    """Test /api/enterprise/commercial-gestures CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_commercial_gestures_list(self, auth_headers):
        """Test GET /api/enterprise/commercial-gestures"""
        response = requests.get(f"{BASE_URL}/api/enterprise/commercial-gestures", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "gestures" in data
        assert "stats" in data
        assert "total_gestures" in data["stats"]
        assert "active_gestures" in data["stats"]
        assert "total_uses" in data["stats"]
        
        print(f"✓ Commercial gestures list working - {data['stats']['total_gestures']} gestures")
    
    def test_create_commercial_gesture(self, auth_headers):
        """Test POST /api/enterprise/commercial-gestures"""
        gesture_data = {
            "offer_type": "percentage",
            "value": 15.0,
            "conditions": "Valable sur tout le magasin",
            "max_uses": 100,
            "valid_until": "2025-12-31"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/enterprise/commercial-gestures",
            json=gesture_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["offer_type"] == "percentage"
        assert data["value"] == 15.0
        assert data["is_active"] == True
        
        print(f"✓ Created commercial gesture: {data['value']}% discount")
        return data["id"]
    
    def test_toggle_commercial_gesture(self, auth_headers):
        """Test PUT /api/enterprise/commercial-gestures/{id}/toggle"""
        # Create a gesture
        gesture_data = {
            "offer_type": "fixed_amount",
            "value": 20.0,
            "conditions": "Test toggle",
            "max_uses": 50
        }
        create_response = requests.post(
            f"{BASE_URL}/api/enterprise/commercial-gestures",
            json=gesture_data,
            headers=auth_headers
        )
        gesture_id = create_response.json()["id"]
        
        # Toggle to inactive
        toggle_response = requests.put(
            f"{BASE_URL}/api/enterprise/commercial-gestures/{gesture_id}/toggle",
            headers=auth_headers
        )
        assert toggle_response.status_code == 200
        assert toggle_response.json()["is_active"] == False
        
        print(f"✓ Commercial gesture toggle working")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/enterprise/commercial-gestures/{gesture_id}", headers=auth_headers)


class TestEnterpriseProfileAndLogo:
    """Test enterprise profile and logo display with getImageUrl()"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_enterprise_profile(self, auth_headers):
        """Test getting enterprise profile with logo"""
        # Get user info first
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        user = me_response.json()
        
        # Get enterprises list
        enterprises_response = requests.get(f"{BASE_URL}/api/enterprises")
        enterprises = enterprises_response.json()["enterprises"]
        
        # Find enterprise for this user
        user_enterprise = next((e for e in enterprises if e.get("user_id") == user["id"]), None)
        
        if user_enterprise:
            assert "id" in user_enterprise
            assert "business_name" in user_enterprise
            print(f"✓ Enterprise profile found: {user_enterprise['business_name']}")
            
            if user_enterprise.get("logo"):
                print(f"  Logo URL: {user_enterprise['logo']}")
                # Verify logo URL is accessible
                logo_url = user_enterprise["logo"]
                if logo_url.startswith("/api/uploads"):
                    full_url = f"{BASE_URL}{logo_url}"
                    logo_response = requests.head(full_url)
                    assert logo_response.status_code == 200, f"Logo not accessible: {full_url}"
                    print(f"  ✓ Logo accessible at {full_url}")
        else:
            print("⚠ No enterprise profile found for this user")


class TestRegistrationFlow:
    """Test multi-step registration form"""
    
    def test_registration_endpoint_exists(self):
        """Test that registration endpoint is available"""
        # Test with invalid data to verify endpoint exists
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "invalid",
            "password": "short"
        })
        # Should return 422 (validation error) not 404
        assert response.status_code in [400, 422], f"Unexpected status: {response.status_code}"
        print(f"✓ Registration endpoint exists and validates input")
    
    def test_registration_with_valid_data(self):
        """Test registration with valid data (client type)"""
        unique_email = f"test_client_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "Client",
            "phone": "+41791234567",
            "user_type": "client"
        })
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == unique_email
        assert data["user"]["user_type"] == "client"
        
        print(f"✓ Client registration successful: {unique_email}")


# Cleanup test data
class TestCleanup:
    """Cleanup TEST_ prefixed data after tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_cleanup_test_campaigns(self, auth_headers):
        """Clean up TEST_ prefixed campaigns"""
        response = requests.get(f"{BASE_URL}/api/enterprise/ia-campaigns", headers=auth_headers)
        campaigns = response.json().get("campaigns", [])
        
        deleted = 0
        for campaign in campaigns:
            if campaign.get("name", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/enterprise/ia-campaigns/{campaign['id']}", headers=auth_headers)
                deleted += 1
        
        print(f"✓ Cleaned up {deleted} test campaigns")
    
    def test_cleanup_test_invitations(self, auth_headers):
        """Clean up TEST_ prefixed invitations"""
        response = requests.get(f"{BASE_URL}/api/enterprise/invitations", headers=auth_headers)
        invitations = response.json().get("invitations", [])
        
        deleted = 0
        for inv in invitations:
            if inv.get("title", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/enterprise/invitations/{inv['id']}", headers=auth_headers)
                deleted += 1
        
        print(f"✓ Cleaned up {deleted} test invitations")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
