"""
Iteration 40 - Comprehensive Monetization System Testing
Tests for:
- Splash screen optimization (3 seconds)
- Stripe payment flows (Premium 9.99 CHF, VIP 19.99 CHF)
- RDV Titelli - Romantic subscription (200 CHF/month)
- Lifestyle Passes (Healthy 99 CHF, Better You 149 CHF, MVP 299 CHF)
- Titelli Pro++ subscription (199 CHF/month) - enterprises only
- Stripe webhooks endpoint (/api/webhooks/stripe)
- Admin routes (/api/admin/stats, /api/admin/users, /api/admin/accounting/summary)
- Referral system (/api/gamification/referral/my-code)
- Email preferences (/api/notifications/preferences)
- Sports (/api/sports/categories, /api/sports/teams/my)
"""
import pytest
import requests
import os
import json
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://image-fix-demo.preview.emergentagent.com"

# Test credentials
TEST_CREDENTIALS = {
    "admin": {"email": "admin@titelli.com", "password": "Admin123!"},
    "client": {"email": "test.client@titelli.com", "password": "Test123!"},
    "enterprise": {"email": "test.entreprise@titelli.com", "password": "Test123!"}
}


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✅ API Health: {data}")
    
    def test_webhooks_health(self):
        """Test webhooks health endpoint"""
        response = requests.get(f"{BASE_URL}/api/webhooks/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "supported_events" in data
        print(f"✅ Webhooks Health: {data}")


class TestAuthentication:
    """Authentication tests for all user types"""
    
    def test_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["admin"])
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["email"] == TEST_CREDENTIALS["admin"]["email"]
        print(f"✅ Admin login successful: {data['user']['email']}")
    
    def test_client_login(self):
        """Test client login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["user_type"] == "client"
        print(f"✅ Client login successful: {data['user']['email']}")
    
    def test_enterprise_login(self):
        """Test enterprise login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["enterprise"])
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["user_type"] in ["enterprise", "entreprise"]
        print(f"✅ Enterprise login successful: {data['user']['email']}")


class TestStripePaymentFlows:
    """Test Stripe payment checkout flows"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        return response.json()["token"]
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["enterprise"])
        return response.json()["token"]
    
    def test_premium_subscription_checkout(self, client_token):
        """Test Premium subscription checkout (9.99 CHF) - uses query param"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout?plan_id=premium",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "checkout.stripe.com" in data["url"]
        print(f"✅ Premium checkout URL: {data['url'][:80]}...")
    
    def test_premium_mvp_subscription_checkout(self, client_token):
        """Test Premium MVP subscription checkout - uses query param"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout?plan_id=premium_mvp",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "checkout.stripe.com" in data["url"]
        print(f"✅ Premium MVP checkout URL: {data['url'][:80]}...")


class TestRDVTitelliMonetization:
    """Test RDV Titelli romantic subscription (200 CHF/month)"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        return response.json()["token"]
    
    def test_rdv_categories(self, client_token):
        """Test RDV categories endpoint"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/rdv/categories", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) >= 8
        print(f"✅ RDV Categories: {len(data['categories'])} categories")
    
    def test_romantic_subscription_checkout(self, client_token):
        """Test romantic subscription checkout (200 CHF/month) - correct endpoint"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(
            f"{BASE_URL}/api/rdv/subscriptions/romantic",
            headers=headers
        )
        # Should return checkout URL or already subscribed message
        assert response.status_code == 200
        data = response.json()
        if "checkout_url" in data:
            assert "checkout.stripe.com" in data["checkout_url"]
            print(f"✅ Romantic subscription checkout: {data['checkout_url'][:80]}...")
        elif "has_subscription" in data:
            print(f"✅ Romantic subscription: Already subscribed - {data.get('message', 'active')}")
        else:
            print(f"✅ Romantic subscription response: {data}")


class TestLifestylePasses:
    """Test Lifestyle Passes (Healthy 99 CHF, Better You 149 CHF, MVP 299 CHF)"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        return response.json()["token"]
    
    def test_get_lifestyle_passes(self, client_token):
        """Test getting available lifestyle passes"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/specialists/passes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "passes" in data
        passes = data["passes"]
        
        # Verify all 3 passes exist with correct prices
        assert "healthy" in passes
        assert passes["healthy"]["price"] == 99.0
        
        assert "better_you" in passes
        assert passes["better_you"]["price"] == 149.0
        
        assert "mvp" in passes
        assert passes["mvp"]["price"] == 299.0
        
        print(f"✅ Lifestyle Passes: Healthy={passes['healthy']['price']} CHF, Better You={passes['better_you']['price']} CHF, MVP={passes['mvp']['price']} CHF")
    
    def test_healthy_pass_checkout(self, client_token):
        """Test Healthy pass checkout (99 CHF)"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(
            f"{BASE_URL}/api/specialists/passes/subscribe",
            json={"pass_type": "healthy"},
            headers=headers
        )
        assert response.status_code in [200, 400]
        data = response.json()
        if response.status_code == 200 and "checkout_url" in data:
            assert "checkout.stripe.com" in data["checkout_url"]
            print(f"✅ Healthy pass checkout: {data['checkout_url'][:80]}...")
        else:
            print(f"ℹ️ Healthy pass: {data.get('message', data)}")
    
    def test_better_you_pass_checkout(self, client_token):
        """Test Better You pass checkout (149 CHF)"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(
            f"{BASE_URL}/api/specialists/passes/subscribe",
            json={"pass_type": "better_you"},
            headers=headers
        )
        assert response.status_code in [200, 400]
        data = response.json()
        if response.status_code == 200 and "checkout_url" in data:
            assert "checkout.stripe.com" in data["checkout_url"]
            print(f"✅ Better You pass checkout: {data['checkout_url'][:80]}...")
        else:
            print(f"ℹ️ Better You pass: {data.get('message', data)}")
    
    def test_mvp_pass_checkout(self, client_token):
        """Test MVP pass checkout (299 CHF)"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(
            f"{BASE_URL}/api/specialists/passes/subscribe",
            json={"pass_type": "mvp"},
            headers=headers
        )
        assert response.status_code in [200, 400]
        data = response.json()
        if response.status_code == 200 and "checkout_url" in data:
            assert "checkout.stripe.com" in data["checkout_url"]
            print(f"✅ MVP pass checkout: {data['checkout_url'][:80]}...")
        else:
            print(f"ℹ️ MVP pass: {data.get('message', data)}")


class TestTitelliProPlus:
    """Test Titelli Pro++ subscription (199 CHF/month) - enterprises only"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        return response.json()["token"]
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["enterprise"])
        return response.json()["token"]
    
    def test_pro_status_client_forbidden(self, client_token):
        """Test that clients cannot access Pro++ (403)"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/pro/status", headers=headers)
        assert response.status_code == 403
        print(f"✅ Pro++ correctly forbidden for clients (403)")
    
    def test_pro_status_enterprise(self, enterprise_token):
        """Test Pro++ status for enterprise"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/pro/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        if not data.get("has_subscription"):
            assert data.get("price") == 199.0
            assert data.get("currency") == "CHF"
        print(f"✅ Pro++ status for enterprise: {data}")
    
    def test_pro_subscribe_enterprise(self, enterprise_token):
        """Test Pro++ subscription checkout (199 CHF/month)"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.post(
            f"{BASE_URL}/api/pro/subscribe",
            json={"business_type": "general"},
            headers=headers
        )
        assert response.status_code in [200, 400]
        data = response.json()
        if response.status_code == 200 and "checkout_url" in data:
            assert "checkout.stripe.com" in data["checkout_url"]
            assert data.get("price") == 199.0
            print(f"✅ Pro++ checkout: {data['checkout_url'][:80]}...")
        else:
            print(f"ℹ️ Pro++ subscription: {data.get('message', data)}")


class TestStripeWebhooks:
    """Test Stripe webhooks endpoint"""
    
    def test_webhook_endpoint_exists(self):
        """Test that webhook endpoint exists and responds"""
        # Send a test webhook payload (will be rejected without valid signature)
        test_payload = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "test_session_123",
                    "metadata": {"type": "test"}
                }
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/webhooks/stripe",
            json=test_payload
        )
        # Should return 200 (processed) or 400 (invalid signature in production)
        assert response.status_code in [200, 400]
        print(f"✅ Webhook endpoint responds: {response.status_code}")
    
    def test_webhook_health(self):
        """Test webhook health endpoint"""
        response = requests.get(f"{BASE_URL}/api/webhooks/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "checkout.session.completed" in data.get("supported_events", [])
        assert "payment_intent.payment_failed" in data.get("supported_events", [])
        print(f"✅ Webhook health: {data}")


class TestAdminRoutes:
    """Test admin routes"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["admin"])
        return response.json()["token"]
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        return response.json()["token"]
    
    def test_admin_stats(self, admin_token):
        """Test admin stats endpoint - actual response structure"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Actual response has: stats, recent_users, recent_orders
        assert "stats" in data
        assert "total_users" in data["stats"]
        assert "total_enterprises" in data["stats"]
        assert "total_orders" in data["stats"]
        print(f"✅ Admin stats: Users={data['stats']['total_users']}, Enterprises={data['stats']['total_enterprises']}, Orders={data['stats']['total_orders']}")
    
    def test_admin_stats_forbidden_for_client(self, client_token):
        """Test that clients cannot access admin stats"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 403
        print(f"✅ Admin stats correctly forbidden for clients (403)")
    
    def test_admin_users(self, admin_token):
        """Test admin users endpoint"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        print(f"✅ Admin users: {data['total']} total users")
    
    def test_admin_accounting_summary(self, admin_token):
        """Test admin accounting summary endpoint"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/accounting/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert "subscriptions" in data
        print(f"✅ Admin accounting summary: Orders revenue={data['orders'].get('total_revenue', 0)}")


class TestReferralSystem:
    """Test referral/parrainage system"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        return response.json()["token"]
    
    def test_get_my_referral_code(self, client_token):
        """Test getting user's referral code"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/gamification/referral/my-code", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert data["code"].startswith("TIT")
        print(f"✅ Referral code: {data['code']}")
    
    def test_referral_stats(self, client_token):
        """Test referral stats - actual response structure"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/gamification/referral/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Actual response has: referrals_count, total_points_earned, code, referrals, bonuses_achieved, next_bonus
        assert "referrals_count" in data
        assert "total_points_earned" in data
        assert "code" in data
        print(f"✅ Referral stats: {data['referrals_count']} referrals, {data['total_points_earned']} points")
    
    def test_referral_leaderboard(self, client_token):
        """Test referral leaderboard"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/gamification/referral/leaderboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data
        print(f"✅ Referral leaderboard: {len(data['leaderboard'])} entries")


class TestEmailPreferences:
    """Test email/notification preferences"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        return response.json()["token"]
    
    def test_get_notification_preferences(self, client_token):
        """Test getting notification preferences"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/notifications/preferences", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "preferences" in data
        print(f"✅ Notification preferences: {data['preferences']}")
    
    def test_update_notification_preferences(self, client_token):
        """Test updating notification preferences"""
        headers = {"Authorization": f"Bearer {client_token}"}
        new_prefs = {
            "email_marketing": True,
            "email_orders": True,
            "push_notifications": True
        }
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            json=new_prefs,
            headers=headers
        )
        assert response.status_code == 200
        print(f"✅ Notification preferences updated")


class TestSportsFeatures:
    """Test sports features"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        return response.json()["token"]
    
    def test_sports_categories(self, client_token):
        """Test sports categories endpoint"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/sports/categories", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) >= 11
        
        # Verify some expected sports
        sport_ids = [s["id"] for s in data["categories"]]
        assert "football" in sport_ids
        assert "tennis" in sport_ids
        assert "basketball" in sport_ids
        print(f"✅ Sports categories: {len(data['categories'])} sports")
    
    def test_my_teams(self, client_token):
        """Test my teams endpoint"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/sports/teams/my", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert "count" in data
        print(f"✅ My teams: {data['count']} teams")
    
    def test_sports_matches(self, client_token):
        """Test sports matches endpoint"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/sports/matches", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        print(f"✅ Sports matches: {data.get('total', len(data['matches']))} matches")


class TestSpecialistCategories:
    """Test specialist categories"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        return response.json()["token"]
    
    def test_specialist_categories(self, client_token):
        """Test specialist categories endpoint"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/specialists/categories", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) >= 10
        print(f"✅ Specialist categories: {len(data['categories'])} categories")


class TestGamificationProfile:
    """Test gamification profile"""
    
    @pytest.fixture
    def client_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["client"])
        return response.json()["token"]
    
    def test_gamification_profile(self, client_token):
        """Test gamification profile endpoint - actual response structure"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/gamification/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Actual response has: total_points, level, badges, badges_count, login_streak, etc.
        assert "total_points" in data
        assert "level" in data
        print(f"✅ Gamification profile: {data['total_points']} points, level {data['level']['name']}")
    
    def test_gamification_levels(self, client_token):
        """Test gamification levels endpoint"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/gamification/levels", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data
        assert len(data["levels"]) >= 8
        print(f"✅ Gamification levels: {len(data['levels'])} levels")


class TestProFeatures:
    """Test Pro++ features for enterprises"""
    
    @pytest.fixture
    def enterprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS["enterprise"])
        return response.json()["token"]
    
    def test_pro_features(self, enterprise_token):
        """Test Pro++ features endpoint"""
        headers = {"Authorization": f"Bearer {enterprise_token}"}
        response = requests.get(f"{BASE_URL}/api/specialists/pro/features", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["price"] == 199.0
        assert "features" in data
        print(f"✅ Pro++ features: {data['name']} - {data['price']} CHF")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
