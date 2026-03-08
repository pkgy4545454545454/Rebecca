"""
Iteration 22 - Testing new features:
1. BUG FIX: Wishlist heart button (token issue fixed - titelli_token)
2. GET /api/certifications - returns available certifications
3. POST /api/enterprise/certifications/apply - creates Stripe checkout for certification
4. GET /api/expert-services - returns expert optimization services
5. POST /api/expert-services/book - creates Stripe checkout for expert service
6. GET /api/client/invoices - returns client invoices from orders/subscriptions/trainings
7. POST /api/client/activity-post - creates public activity post for friends feed
8. Fees: Orders should include subtotal, transaction_fee (2.9%), management_fee (10%)
9. POST /api/investments/{id}/invest - should include 12% commission calculation
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

# Test credentials
CLIENT_EMAIL = "test@example.com"
CLIENT_PASSWORD = "Test123!"
ENTERPRISE_EMAIL = "spa.luxury@titelli.com"
ENTERPRISE_PASSWORD = "Demo123!"


class TestCertifications:
    """Test certification system endpoints"""
    
    def test_get_available_certifications(self):
        """GET /api/certifications - returns available certifications"""
        response = requests.get(f"{BASE_URL}/api/certifications")
        assert response.status_code == 200
        
        data = response.json()
        assert "certifications" in data
        certs = data["certifications"]
        
        # Verify 4 certification types exist
        assert "quality" in certs
        assert "eco" in certs
        assert "expert" in certs
        assert "premium_partner" in certs
        
        # Verify certification structure
        quality = certs["quality"]
        assert quality["name"] == "Qualité Titelli"
        assert quality["price"] == 199
        assert quality["duration_months"] == 12
        assert "badge" in quality
        
        print(f"✓ Found {len(certs)} certification types")
    
    def test_apply_for_certification_creates_stripe_checkout(self):
        """POST /api/enterprise/certifications/apply - creates Stripe checkout"""
        # Login as enterprise
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Apply for certification
        response = requests.post(
            f"{BASE_URL}/api/enterprise/certifications/apply",
            json={"certification_type": "quality"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify Stripe checkout URL returned
        assert "checkout_url" in data
        assert "session_id" in data
        assert "checkout.stripe.com" in data["checkout_url"]
        
        print(f"✓ Certification checkout URL: {data['checkout_url'][:60]}...")
    
    def test_get_enterprise_certifications(self):
        """GET /api/enterprise/certifications - returns enterprise's certifications"""
        # Login as enterprise
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/enterprise/certifications", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "certifications" in data
        print(f"✓ Enterprise has {len(data['certifications'])} active certifications")


class TestExpertServices:
    """Test expert optimization services endpoints"""
    
    def test_get_expert_services(self):
        """GET /api/expert-services - returns expert optimization services"""
        response = requests.get(f"{BASE_URL}/api/expert-services")
        assert response.status_code == 200
        
        data = response.json()
        assert "services" in data
        services = data["services"]
        
        # Verify 4 service types exist
        assert "image_optimization" in services
        assert "fiscal_optimization" in services
        assert "marketing_strategy" in services
        assert "business_starter" in services
        
        # Verify service structure
        image_opt = services["image_optimization"]
        assert image_opt["name"] == "Optimisation d'Image"
        assert image_opt["price"] == 299
        assert "description" in image_opt
        assert "duration" in image_opt
        
        print(f"✓ Found {len(services)} expert services")
    
    def test_book_expert_service_creates_stripe_checkout(self):
        """POST /api/expert-services/book - creates Stripe checkout for expert service"""
        # Login as client
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Book expert service
        response = requests.post(
            f"{BASE_URL}/api/expert-services/book?service_type=image_optimization",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify Stripe checkout URL returned
        assert "checkout_url" in data
        assert "session_id" in data
        assert "checkout.stripe.com" in data["checkout_url"]
        
        print(f"✓ Expert service checkout URL: {data['checkout_url'][:60]}...")


class TestClientInvoices:
    """Test client invoices endpoint"""
    
    def test_get_client_invoices(self):
        """GET /api/client/invoices - returns client invoices from orders/subscriptions/trainings"""
        # Login as client
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/client/invoices", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "invoices" in data
        assert "total_invoices" in data
        assert "total_spent" in data
        
        # Verify invoice structure if any exist
        if data["invoices"]:
            invoice = data["invoices"][0]
            assert "id" in invoice
            assert "type" in invoice  # order, subscription, training
            assert "total" in invoice
            assert "status" in invoice
            assert "date" in invoice
            
            # Verify fee fields for orders
            if invoice["type"] == "order":
                assert "subtotal" in invoice
                assert "transaction_fee" in invoice
        
        print(f"✓ Client has {data['total_invoices']} invoices, total spent: {data['total_spent']} CHF")


class TestActivityPost:
    """Test activity post endpoint for friends feed"""
    
    def test_create_activity_post(self):
        """POST /api/client/activity-post - creates public activity post for friends feed"""
        # Login as client
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create activity post
        post_data = {
            "activity_type": "recommendation",
            "title": "TEST_Recommandation de service",
            "description": "J'ai testé ce service et c'était excellent!",
            "is_public": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/client/activity-post",
            json=post_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify post structure
        assert "id" in data
        assert data["activity_type"] == "recommendation"
        assert data["title"] == "TEST_Recommandation de service"
        assert data["is_public"] == True
        assert "user_name" in data
        assert "created_at" in data
        
        print(f"✓ Activity post created with ID: {data['id'][:8]}...")
        
        # Cleanup - get posts and verify
        posts_res = requests.get(f"{BASE_URL}/api/client/activity-posts", headers=headers)
        assert posts_res.status_code == 200
        posts = posts_res.json()["posts"]
        assert any(p["id"] == data["id"] for p in posts)
        print(f"✓ Activity post verified in user's posts list")


class TestOrderFees:
    """Test that orders include proper fee calculations"""
    
    def test_order_includes_fees(self):
        """Orders should include subtotal, transaction_fee (2.9%), management_fee (10%)"""
        # Login as client
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get an enterprise to order from
        enterprises_res = requests.get(f"{BASE_URL}/api/enterprises?limit=1")
        assert enterprises_res.status_code == 200
        enterprises = enterprises_res.json()["enterprises"]
        
        if not enterprises:
            pytest.skip("No enterprises available for order test")
        
        enterprise_id = enterprises[0]["id"]
        
        # Get a service/product from this enterprise
        items_res = requests.get(f"{BASE_URL}/api/services-products?enterprise_id={enterprise_id}&limit=1")
        items = items_res.json().get("items", [])
        
        if not items:
            pytest.skip("No items available for order test")
        
        item = items[0]
        
        # Create order
        order_data = {
            "enterprise_id": enterprise_id,
            "items": [{
                "service_product_id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "quantity": 1
            }]
        }
        
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
        assert response.status_code == 200
        
        order = response.json()
        
        # Verify fee fields exist
        assert "subtotal" in order, "Order missing subtotal field"
        assert "transaction_fee" in order, "Order missing transaction_fee field"
        assert "management_fee" in order, "Order missing management_fee field"
        assert "total" in order, "Order missing total field"
        
        # Verify fee calculations
        subtotal = order["subtotal"]
        transaction_fee = order["transaction_fee"]
        management_fee = order["management_fee"]
        total = order["total"]
        
        # Transaction fee should be 2.9% of subtotal
        expected_transaction_fee = round(subtotal * 0.029, 2)
        assert abs(transaction_fee - expected_transaction_fee) < 0.01, \
            f"Transaction fee {transaction_fee} != expected {expected_transaction_fee} (2.9%)"
        
        # Management fee should be 10% of subtotal
        expected_management_fee = round(subtotal * 0.10, 2)
        assert abs(management_fee - expected_management_fee) < 0.01, \
            f"Management fee {management_fee} != expected {expected_management_fee} (10%)"
        
        # Total should be subtotal + transaction_fee
        expected_total = round(subtotal + transaction_fee, 2)
        assert abs(total - expected_total) < 0.01, \
            f"Total {total} != expected {expected_total}"
        
        print(f"✓ Order fees verified:")
        print(f"  Subtotal: {subtotal} CHF")
        print(f"  Transaction fee (2.9%): {transaction_fee} CHF")
        print(f"  Management fee (10%): {management_fee} CHF")
        print(f"  Total: {total} CHF")


class TestInvestmentCommission:
    """Test investment 12% commission calculation"""
    
    def test_investment_includes_12pct_commission(self):
        """POST /api/investments/{id}/invest - should include 12% commission calculation"""
        # Login as client
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get available investments
        investments_res = requests.get(f"{BASE_URL}/api/investments")
        assert investments_res.status_code == 200
        investments = investments_res.json()
        
        if not investments:
            pytest.skip("No investments available for test")
        
        investment = investments[0]
        investment_id = investment["id"]
        min_investment = investment.get("min_investment", 100)
        
        # Make investment
        response = requests.post(
            f"{BASE_URL}/api/investments/{investment_id}/invest?amount={min_investment}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify investment record
        assert "investment" in data
        inv = data["investment"]
        assert inv["amount_invested"] == min_investment
        assert "management_fee" in inv
        assert "transaction_fee" in inv
        assert "titelli_commission_12pct" in inv
        assert "expected_net_return" in inv
        
        # Verify fees breakdown
        assert "fees_breakdown" in data
        fees = data["fees_breakdown"]
        assert fees["gross_amount"] == min_investment
        assert "management_fee_10pct" in fees
        assert "transaction_fee_2_9pct" in fees
        assert "titelli_commission_12pct" in fees
        assert "expected_net_return_to_you" in fees
        
        # Verify 12% commission calculation
        expected_return_rate = investment.get("expected_return", 0) / 100
        gross_return = round(min_investment * expected_return_rate, 2)
        expected_commission = round(gross_return * 0.12, 2)
        
        assert abs(fees["titelli_commission_12pct"] - expected_commission) < 0.01, \
            f"Commission {fees['titelli_commission_12pct']} != expected {expected_commission} (12%)"
        
        print(f"✓ Investment commission verified:")
        print(f"  Amount invested: {min_investment} CHF")
        print(f"  Management fee (10%): {fees['management_fee_10pct']} CHF")
        print(f"  Transaction fee (2.9%): {fees['transaction_fee_2_9pct']} CHF")
        print(f"  Expected gross return: {fees['expected_gross_return']} CHF")
        print(f"  Titelli commission (12%): {fees['titelli_commission_12pct']} CHF")
        print(f"  Net return to investor: {fees['expected_net_return_to_you']} CHF")


class TestWishlistBugFix:
    """Test wishlist heart button bug fix (token issue)"""
    
    def test_wishlist_add_with_correct_token(self):
        """Wishlist should work with titelli_token (not 'token')"""
        # Login as client
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get a service/product to add to wishlist
        items_res = requests.get(f"{BASE_URL}/api/services-products?limit=1")
        assert items_res.status_code == 200
        items = items_res.json().get("items", [])
        
        if not items:
            pytest.skip("No items available for wishlist test")
        
        item = items[0]
        
        # Add to wishlist
        wishlist_data = {
            "item_id": item["id"],
            "item_type": item["type"],
            "item_name": item["name"],
            "item_price": item["price"],
            "item_image": item.get("images", [""])[0] if item.get("images") else ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/client/wishlist",
            json=wishlist_data,
            headers=headers
        )
        
        # Should succeed (200) or already exists (400)
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            print(f"✓ Wishlist item added successfully")
        else:
            print(f"✓ Wishlist item already exists (expected)")
        
        # Verify wishlist check works
        check_res = requests.get(
            f"{BASE_URL}/api/client/wishlist/check/{item['id']}",
            headers=headers
        )
        assert check_res.status_code == 200
        assert "in_wishlist" in check_res.json()
        print(f"✓ Wishlist check endpoint working")
        
        # Verify wishlist list works
        list_res = requests.get(f"{BASE_URL}/api/client/wishlist", headers=headers)
        assert list_res.status_code == 200
        assert "items" in list_res.json()
        print(f"✓ Wishlist list endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
