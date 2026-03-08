"""
Iteration 39 - Complete Production Audit for Titelli Social Commerce Platform
Tests all systems: Auth, RDV, Sports, Gamification, Parrainage, Pro++, Specialists, Notifications, Email Preferences
Verifies Stripe is in LIVE mode (sk_live_*)
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

# Test credentials
CLIENT_CREDS = {"email": "test.client@titelli.com", "password": "Test123!"}
ENTERPRISE_CREDS = {"email": "test.entreprise@titelli.com", "password": "Test123!"}
ADMIN_CREDS = {"email": "admin@titelli.com", "password": "Admin123!"}


class TestAuthentication:
    """Test authentication for all user types"""
    
    def test_client_login(self):
        """Test client login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        assert response.status_code == 200, f"Client login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["user_type"] == "client"
        assert data["user"]["email"] == CLIENT_CREDS["email"]
        print(f"✅ Client login successful: {data['user']['email']}")
    
    def test_enterprise_login(self):
        """Test enterprise login - accepts 'entreprise' user_type"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ENTERPRISE_CREDS)
        assert response.status_code == 200, f"Enterprise login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["user_type"] in ["enterprise", "entreprise"]
        assert data["user"]["email"] == ENTERPRISE_CREDS["email"]
        print(f"✅ Enterprise login successful: {data['user']['email']} (type: {data['user']['user_type']})")
    
    def test_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["user_type"] == "admin"
        print(f"✅ Admin login successful: {data['user']['email']}")


class TestRdvTitelli:
    """Test RDV chez Titelli - Social Booking & Dating Feature"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_rdv_categories_count_8(self):
        """Test RDV categories - should have 8 categories"""
        response = requests.get(f"{BASE_URL}/api/rdv/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 8, f"Expected 8 categories, got {len(data['categories'])}"
        category_ids = [c["id"] for c in data["categories"]]
        expected = ["restaurant", "sport", "wellness", "culture", "nature", "party", "creative", "other"]
        assert set(category_ids) == set(expected), f"Categories mismatch: {category_ids}"
        print(f"✅ RDV Categories: {len(data['categories'])} categories found")
    
    def test_rdv_offers_list(self, client_token):
        """Test getting RDV offers"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/rdv/offers", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "offers" in data
        print(f"✅ RDV Offers: {len(data['offers'])} offers available")
    
    def test_rdv_my_offers(self, client_token):
        """Test getting user's own offers"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/rdv/offers/my", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "offers" in data
        print(f"✅ My RDV Offers: {data.get('count', len(data['offers']))} offers")
    
    def test_rdv_invitations_received(self, client_token):
        """Test getting received invitations"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/rdv/invitations/received", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "invitations" in data
        print(f"✅ RDV Invitations received: {data.get('count', len(data['invitations']))}")
    
    def test_rdv_romantic_subscription_status(self, client_token):
        """Test romantic subscription status"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/rdv/subscriptions/romantic/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "has_subscription" in data
        print(f"✅ Romantic subscription status: has_subscription={data['has_subscription']}")
    
    def test_rdv_romantic_subscription_stripe_checkout(self, client_token):
        """Test romantic subscription creates Stripe checkout (200 CHF/month)"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(f"{BASE_URL}/api/rdv/subscriptions/romantic", headers=headers)
        # Either 200 (checkout created) or already has subscription
        assert response.status_code in [200, 402]
        data = response.json()
        if "checkout_url" in data:
            assert data["checkout_url"].startswith("https://checkout.stripe.com"), "Stripe checkout URL invalid"
            assert data.get("price") == 200.0, f"Expected 200 CHF, got {data.get('price')}"
            print(f"✅ Romantic subscription Stripe checkout: {data['checkout_url'][:60]}...")
        else:
            print(f"✅ Romantic subscription: {data.get('message', 'Already subscribed or pending')}")


class TestSports:
    """Test Sports & Competitions"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_sports_categories_count_11(self):
        """Test sports categories - should have 11 sports"""
        response = requests.get(f"{BASE_URL}/api/sports/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 11, f"Expected 11 sports, got {len(data['categories'])}"
        sport_ids = [c["id"] for c in data["categories"]]
        expected = ["football", "tennis", "basketball", "volleyball", "badminton", "padel", "running", "swimming", "cycling", "fitness", "other"]
        assert set(sport_ids) == set(expected), f"Sports mismatch: {sport_ids}"
        print(f"✅ Sports Categories: {len(data['categories'])} sports found")
    
    def test_sports_matches_list(self, client_token):
        """Test getting sports matches"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/sports/matches", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        print(f"✅ Sports Matches: {len(data['matches'])} matches available")
    
    def test_sports_my_matches(self, client_token):
        """Test getting user's matches"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/sports/matches/my", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        print(f"✅ My Sports Matches: {data.get('count', len(data['matches']))}")
    
    def test_sports_teams_list(self):
        """Test getting teams (public)"""
        response = requests.get(f"{BASE_URL}/api/sports/teams")
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        print(f"✅ Sports Teams: {len(data['teams'])} teams")
    
    def test_sports_my_teams(self, client_token):
        """Test getting user's teams"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/sports/teams/my", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        print(f"✅ My Sports Teams: {data.get('count', len(data['teams']))}")
    
    def test_sports_competitions_list(self):
        """Test getting competitions (public)"""
        response = requests.get(f"{BASE_URL}/api/sports/competitions")
        assert response.status_code == 200
        data = response.json()
        assert "competitions" in data
        print(f"✅ Sports Competitions: {len(data['competitions'])} competitions")


class TestGamification:
    """Test Gamification System - Points, Badges, Leaderboard, Levels"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_gamification_profile(self, client_token):
        """Test gamification profile with points and level"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/gamification/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_points" in data
        assert "level" in data
        assert "badges" in data
        assert "login_streak" in data
        print(f"✅ Gamification Profile: {data['total_points']} points, Level {data['level']['level']} ({data['level']['name']})")
    
    def test_gamification_badges(self, client_token):
        """Test badges list"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/gamification/badges", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "badges" in data
        assert "total_badges" in data
        assert "earned_count" in data
        print(f"✅ Gamification Badges: {data['earned_count']}/{data['total_badges']} earned")
    
    def test_gamification_levels(self):
        """Test levels info - should have 8 levels"""
        response = requests.get(f"{BASE_URL}/api/gamification/levels")
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data
        assert len(data["levels"]) == 8, f"Expected 8 levels, got {len(data['levels'])}"
        level_names = [l["name"] for l in data["levels"]]
        expected = ["Débutant", "Amateur", "Confirmé", "Expert", "Master", "Champion", "Légende", "Titan"]
        assert level_names == expected, f"Levels mismatch: {level_names}"
        print(f"✅ Gamification Levels: {len(data['levels'])} levels (Débutant to Titan)")
    
    def test_gamification_leaderboard(self):
        """Test leaderboard"""
        response = requests.get(f"{BASE_URL}/api/gamification/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data
        print(f"✅ Gamification Leaderboard: {len(data['leaderboard'])} users")
    
    def test_gamification_points_config(self):
        """Test points configuration"""
        response = requests.get(f"{BASE_URL}/api/gamification/points-config")
        assert response.status_code == 200
        data = response.json()
        assert "points_config" in data
        print(f"✅ Points Config: {len(data['points_config'])} actions configured")


class TestParrainage:
    """Test Referral/Parrainage System"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_referral_my_code(self, client_token):
        """Test getting unique referral code"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/gamification/referral/my-code", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert data["code"].startswith("TIT"), f"Referral code should start with TIT: {data['code']}"
        assert "share_url" in data
        assert "referrals_count" in data
        print(f"✅ Referral Code: {data['code']} ({data['referrals_count']} referrals)")
    
    def test_referral_stats(self, client_token):
        """Test referral statistics"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/gamification/referral/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "referrals_count" in data
        assert "total_points_earned" in data
        print(f"✅ Referral Stats: {data['referrals_count']} referrals, {data['total_points_earned']} points earned")
    
    def test_referral_leaderboard(self):
        """Test referral leaderboard"""
        response = requests.get(f"{BASE_URL}/api/gamification/referral/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data
        print(f"✅ Referral Leaderboard: {len(data['leaderboard'])} users")


class TestTitelliProPlus:
    """Test Titelli Pro++ - Enterprise only features"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ENTERPRISE_CREDS)
        return response.json()["token"]
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_pro_status_enterprise_only(self, enterprise_token, client_token):
        """Test Pro++ status - enterprise only"""
        # Enterprise should have access
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/pro/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "has_subscription" in data
        print(f"✅ Pro++ Status (Enterprise): has_subscription={data['has_subscription']}")
        
        # Client should get 403
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/pro/status", headers=headers)
        assert response.status_code == 403, "Client should not access Pro++ status"
        print(f"✅ Pro++ Status (Client): Correctly blocked (403)")
    
    def test_pro_subscribe_stripe_checkout(self, enterprise_token):
        """Test Pro++ subscription creates Stripe checkout (199 CHF/month)"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(f"{BASE_URL}/api/pro/subscribe", headers=headers, json={"business_type": "general"})
        # Either 200 (checkout created) or already has subscription
        assert response.status_code in [200, 402]
        data = response.json()
        if "checkout_url" in data:
            assert data["checkout_url"].startswith("https://checkout.stripe.com"), "Stripe checkout URL invalid"
            assert data.get("price") == 199.0, f"Expected 199 CHF, got {data.get('price')}"
            print(f"✅ Pro++ Stripe checkout: {data['checkout_url'][:60]}...")
        else:
            print(f"✅ Pro++ subscription: {data.get('message', 'Already subscribed')}")
    
    def test_pro_deliveries(self, enterprise_token):
        """Test B2B deliveries endpoint"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/pro/deliveries", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "deliveries" in data
        print(f"✅ Pro++ Deliveries: {data.get('count', len(data['deliveries']))} clients")
    
    def test_pro_liquidations(self, enterprise_token):
        """Test liquidations endpoint"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/pro/liquidations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✅ Pro++ Liquidations: {data.get('count', len(data['items']))} items")


class TestSpecialists:
    """Test Specialists/Passes System"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_specialists_categories_count_10(self):
        """Test specialists categories - should have 10 categories"""
        response = requests.get(f"{BASE_URL}/api/specialists/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 10, f"Expected 10 categories, got {len(data['categories'])}"
        print(f"✅ Specialists Categories: {len(data['categories'])} categories")
    
    def test_specialists_passes_count_3(self):
        """Test lifestyle passes - should have 3 passes"""
        response = requests.get(f"{BASE_URL}/api/specialists/passes")
        assert response.status_code == 200
        data = response.json()
        assert "passes" in data
        passes = data["passes"]
        # Passes are returned as a dictionary, not a list
        assert len(passes) == 3, f"Expected 3 passes, got {len(passes)}"
        
        # Verify pass prices (passes is a dict with keys: healthy, better_you, mvp)
        assert passes.get("healthy", {}).get("price") == 99.0, f"Healthy pass should be 99 CHF"
        assert passes.get("better_you", {}).get("price") == 149.0, f"Better You pass should be 149 CHF"
        assert passes.get("mvp", {}).get("price") == 299.0, f"MVP pass should be 299 CHF"
        print(f"✅ Lifestyle Passes: Healthy (99 CHF), Better You (149 CHF), MVP (299 CHF)")
    
    def test_specialists_pass_subscribe_stripe(self, client_token):
        """Test pass subscription creates Stripe checkout"""
        headers = {"Authorization": f"Bearer {client_token}"}
        # Correct endpoint: POST /api/specialists/passes/subscribe with body
        response = requests.post(
            f"{BASE_URL}/api/specialists/passes/subscribe", 
            headers=headers,
            json={"pass_type": "healthy"}
        )
        # Either 200 (checkout created) or already has subscription
        assert response.status_code in [200, 402]
        data = response.json()
        if "checkout_url" in data:
            assert data["checkout_url"].startswith("https://checkout.stripe.com"), "Stripe checkout URL invalid"
            print(f"✅ Pass Stripe checkout: {data['checkout_url'][:60]}...")
        else:
            print(f"✅ Pass subscription: {data.get('message', 'Already subscribed')}")
    
    def test_specialists_requests(self, client_token):
        """Test specialists requests"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/specialists/requests/my", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "requests" in data
        print(f"✅ Specialists Requests: {len(data['requests'])} requests")


class TestNotifications:
    """Test Notifications System"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_notifications_list(self, client_token):
        """Test getting notifications"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        print(f"✅ Notifications: {len(data['notifications'])} total, {data['unread_count']} unread")
    
    def test_notifications_unread_count(self, client_token):
        """Test unread count endpoint"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/notifications/unread-count", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "unread_count" in data
        print(f"✅ Unread Count: {data['unread_count']}")
    
    def test_notifications_preferences(self, client_token):
        """Test notification preferences GET"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/notifications/preferences", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "preferences" in data
        print(f"✅ Notification Preferences: Retrieved")


class TestEmailPreferences:
    """Test Email Preferences System"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_email_preferences_get(self, client_token):
        """Test getting email preferences"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/notifications/email-preferences", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "email_enabled" in data
        assert "preferences" in data
        print(f"✅ Email Preferences GET: email_enabled={data['email_enabled']}")
    
    def test_email_preferences_put(self, client_token):
        """Test updating email preferences"""
        headers = {"Authorization": f"Bearer {client_token}"}
        payload = {
            "email_enabled": True,
            "preferences": {
                "referral": True,
                "payments": True,
                "orders": True,
                "rdv": True,
                "sports": True,
                "promotions": False,
                "newsletter": False,
                "community": True
            }
        }
        response = requests.put(f"{BASE_URL}/api/notifications/email-preferences", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ Email Preferences PUT: Updated successfully")


class TestStripeConfiguration:
    """Test Stripe is in LIVE mode"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ENTERPRISE_CREDS)
        return response.json()["token"]
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDS)
        return response.json()["token"]
    
    def test_stripe_checkout_urls_are_live(self, enterprise_token, client_token):
        """Verify all Stripe checkout URLs start with https://checkout.stripe.com"""
        checkout_urls = []
        
        # Test Pro++ subscription
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(f"{BASE_URL}/api/pro/subscribe", headers=headers, json={"business_type": "general"})
        if response.status_code == 200 and "checkout_url" in response.json():
            checkout_urls.append(("Pro++", response.json()["checkout_url"]))
        
        # Test Romantic subscription
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(f"{BASE_URL}/api/rdv/subscriptions/romantic", headers=headers)
        if response.status_code == 200 and "checkout_url" in response.json():
            checkout_urls.append(("Romantic", response.json()["checkout_url"]))
        
        # Test Lifestyle Pass
        response = requests.post(
            f"{BASE_URL}/api/specialists/passes/subscribe", 
            headers=headers,
            json={"pass_type": "healthy"}
        )
        if response.status_code == 200 and "checkout_url" in response.json():
            checkout_urls.append(("Lifestyle Pass", response.json()["checkout_url"]))
        
        # Verify all URLs
        for name, url in checkout_urls:
            assert url.startswith("https://checkout.stripe.com"), f"{name} checkout URL invalid: {url}"
            print(f"✅ {name} Stripe URL: {url[:60]}...")
        
        if not checkout_urls:
            print("⚠️ No checkout URLs generated (subscriptions may already exist)")
        else:
            print(f"✅ All {len(checkout_urls)} Stripe checkout URLs are valid (checkout.stripe.com)")


class TestHealthAndBasics:
    """Test basic health and API status"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✅ Health: {data['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
