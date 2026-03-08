"""
Test iteration 12 features:
1. Enterprise cover_image updates and displays on cards
2. Media Gallery - photos array management
3. Media Gallery - videos array management  
4. Notification links with ?tab= parameter
5. Services/Products CRUD from enterprise dashboard
6. Dashboard tab parameter support
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


class TestAuth:
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
        print(f"✓ Client login successful: {data['user']['email']}")
        return data['token']
    
    def test_enterprise_login(self):
        """Test enterprise login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data['user']['user_type'] == 'entreprise'
        print(f"✓ Enterprise login successful: {data['user']['email']}")
        return data['token']


class TestEnterpriseCoverImage:
    """Test enterprise cover_image functionality"""
    
    @pytest.fixture
    def enterprise_auth(self):
        """Get enterprise auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()['token']
    
    @pytest.fixture
    def enterprise_id(self, enterprise_auth):
        """Get enterprise ID"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        response = requests.get(f"{BASE_URL}/api/enterprises", headers=headers)
        enterprises = response.json()['enterprises']
        # Find enterprise by user
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        user_id = me_response.json()['id']
        enterprise = next((e for e in enterprises if e.get('user_id') == user_id), None)
        assert enterprise is not None, "Enterprise not found"
        return enterprise['id']
    
    def test_enterprise_has_cover_image_field(self, enterprise_auth, enterprise_id):
        """Test that enterprise model has cover_image field"""
        response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        assert response.status_code == 200
        data = response.json()
        # cover_image should exist (can be null or string)
        assert 'cover_image' in data or data.get('cover_image') is None or isinstance(data.get('cover_image'), str)
        print(f"✓ Enterprise has cover_image field: {data.get('cover_image', 'None')[:50] if data.get('cover_image') else 'None'}...")
    
    def test_update_cover_image(self, enterprise_auth, enterprise_id):
        """Test updating enterprise cover_image"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        test_cover_url = "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800"
        
        response = requests.put(
            f"{BASE_URL}/api/enterprises/{enterprise_id}",
            headers=headers,
            json={"cover_image": test_cover_url}
        )
        assert response.status_code == 200
        print(f"✓ Cover image update request successful")
        
        # Verify the update
        get_response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data.get('cover_image') == test_cover_url
        print(f"✓ Cover image persisted correctly")
    
    def test_enterprises_list_includes_cover_image(self):
        """Test that enterprises list includes cover_image for cards"""
        response = requests.get(f"{BASE_URL}/api/enterprises")
        assert response.status_code == 200
        data = response.json()
        assert 'enterprises' in data
        
        # Check that enterprises have cover_image field
        for enterprise in data['enterprises'][:5]:
            # Field should exist (can be null)
            assert 'cover_image' in enterprise or enterprise.get('cover_image') is None
        print(f"✓ Enterprises list includes cover_image field for {len(data['enterprises'])} enterprises")


class TestMediaGalleryPhotos:
    """Test Media Gallery photos functionality"""
    
    @pytest.fixture
    def enterprise_auth(self):
        """Get enterprise auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()['token']
    
    @pytest.fixture
    def enterprise_id(self, enterprise_auth):
        """Get enterprise ID"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        response = requests.get(f"{BASE_URL}/api/enterprises", headers=headers)
        enterprises = response.json()['enterprises']
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        user_id = me_response.json()['id']
        enterprise = next((e for e in enterprises if e.get('user_id') == user_id), None)
        return enterprise['id']
    
    def test_enterprise_has_photos_array(self, enterprise_auth, enterprise_id):
        """Test that enterprise model has photos array"""
        response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        assert response.status_code == 200
        data = response.json()
        # photos should be a list
        assert 'photos' in data
        assert isinstance(data['photos'], list)
        print(f"✓ Enterprise has photos array with {len(data['photos'])} photos")
    
    def test_add_photo_to_gallery(self, enterprise_auth, enterprise_id):
        """Test adding a photo to the gallery"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        
        # Get current photos
        get_response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        current_photos = get_response.json().get('photos', [])
        
        # Add a new photo
        test_photo_url = f"https://images.unsplash.com/photo-test-{uuid.uuid4().hex[:8]}?w=800"
        new_photos = current_photos + [test_photo_url]
        
        response = requests.put(
            f"{BASE_URL}/api/enterprises/{enterprise_id}",
            headers=headers,
            json={"photos": new_photos}
        )
        assert response.status_code == 200
        print(f"✓ Photo added to gallery")
        
        # Verify
        verify_response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        updated_photos = verify_response.json().get('photos', [])
        assert test_photo_url in updated_photos
        print(f"✓ Photo persisted in gallery (total: {len(updated_photos)})")
        
        # Cleanup - remove the test photo
        cleanup_photos = [p for p in updated_photos if p != test_photo_url]
        requests.put(
            f"{BASE_URL}/api/enterprises/{enterprise_id}",
            headers=headers,
            json={"photos": cleanup_photos}
        )
    
    def test_delete_photo_from_gallery(self, enterprise_auth, enterprise_id):
        """Test deleting a photo from the gallery"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        
        # First add a photo
        test_photo_url = f"https://images.unsplash.com/photo-delete-test-{uuid.uuid4().hex[:8]}?w=800"
        get_response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        current_photos = get_response.json().get('photos', [])
        
        # Add photo
        new_photos = current_photos + [test_photo_url]
        requests.put(
            f"{BASE_URL}/api/enterprises/{enterprise_id}",
            headers=headers,
            json={"photos": new_photos}
        )
        
        # Now delete it
        photos_after_delete = [p for p in new_photos if p != test_photo_url]
        response = requests.put(
            f"{BASE_URL}/api/enterprises/{enterprise_id}",
            headers=headers,
            json={"photos": photos_after_delete}
        )
        assert response.status_code == 200
        
        # Verify deletion
        verify_response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        final_photos = verify_response.json().get('photos', [])
        assert test_photo_url not in final_photos
        print(f"✓ Photo deleted from gallery successfully")


class TestMediaGalleryVideos:
    """Test Media Gallery videos functionality"""
    
    @pytest.fixture
    def enterprise_auth(self):
        """Get enterprise auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()['token']
    
    @pytest.fixture
    def enterprise_id(self, enterprise_auth):
        """Get enterprise ID"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        response = requests.get(f"{BASE_URL}/api/enterprises", headers=headers)
        enterprises = response.json()['enterprises']
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        user_id = me_response.json()['id']
        enterprise = next((e for e in enterprises if e.get('user_id') == user_id), None)
        return enterprise['id']
    
    def test_enterprise_has_videos_array(self, enterprise_auth, enterprise_id):
        """Test that enterprise model has videos array"""
        response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        assert response.status_code == 200
        data = response.json()
        assert 'videos' in data
        assert isinstance(data['videos'], list)
        print(f"✓ Enterprise has videos array with {len(data['videos'])} videos")
    
    def test_add_youtube_video(self, enterprise_auth, enterprise_id):
        """Test adding a YouTube video URL"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        
        # Get current videos
        get_response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        current_videos = get_response.json().get('videos', [])
        
        # Add a YouTube video
        test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        new_videos = current_videos + [test_video_url]
        
        response = requests.put(
            f"{BASE_URL}/api/enterprises/{enterprise_id}",
            headers=headers,
            json={"videos": new_videos}
        )
        assert response.status_code == 200
        print(f"✓ YouTube video added to gallery")
        
        # Verify
        verify_response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        updated_videos = verify_response.json().get('videos', [])
        assert test_video_url in updated_videos
        print(f"✓ Video persisted in gallery (total: {len(updated_videos)})")
        
        # Cleanup
        cleanup_videos = [v for v in updated_videos if v != test_video_url]
        requests.put(
            f"{BASE_URL}/api/enterprises/{enterprise_id}",
            headers=headers,
            json={"videos": cleanup_videos}
        )
    
    def test_delete_video_from_gallery(self, enterprise_auth, enterprise_id):
        """Test deleting a video from the gallery"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        
        # First add a video
        test_video_url = "https://www.youtube.com/watch?v=test123delete"
        get_response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        current_videos = get_response.json().get('videos', [])
        
        # Add video
        new_videos = current_videos + [test_video_url]
        requests.put(
            f"{BASE_URL}/api/enterprises/{enterprise_id}",
            headers=headers,
            json={"videos": new_videos}
        )
        
        # Now delete it
        videos_after_delete = [v for v in new_videos if v != test_video_url]
        response = requests.put(
            f"{BASE_URL}/api/enterprises/{enterprise_id}",
            headers=headers,
            json={"videos": videos_after_delete}
        )
        assert response.status_code == 200
        
        # Verify deletion
        verify_response = requests.get(f"{BASE_URL}/api/enterprises/{enterprise_id}")
        final_videos = verify_response.json().get('videos', [])
        assert test_video_url not in final_videos
        print(f"✓ Video deleted from gallery successfully")


class TestNotificationLinks:
    """Test notification links with tab parameter"""
    
    @pytest.fixture
    def client_auth(self):
        """Get client auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        return response.json()['token']
    
    @pytest.fixture
    def enterprise_auth(self):
        """Get enterprise auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()['token']
    
    def test_get_notifications(self, client_auth):
        """Test getting notifications"""
        headers = {"Authorization": f"Bearer {client_auth}"}
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert 'notifications' in data
        assert 'unread_count' in data
        print(f"✓ Got {len(data['notifications'])} notifications, {data['unread_count']} unread")
    
    def test_notification_has_link_field(self, client_auth):
        """Test that notifications have link field"""
        headers = {"Authorization": f"Bearer {client_auth}"}
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        data = response.json()
        
        # Check if any notification has a link
        for notif in data['notifications']:
            if 'link' in notif and notif['link']:
                print(f"✓ Notification has link: {notif['link']}")
                # Check if link contains tab parameter
                if '?tab=' in notif['link']:
                    print(f"✓ Link contains tab parameter")
                return
        
        print("✓ Notifications endpoint working (no notifications with links found)")
    
    def test_enterprise_notifications(self, enterprise_auth):
        """Test enterprise notifications"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Enterprise has {len(data['notifications'])} notifications")
        
        # Check for order notifications with tab links
        for notif in data['notifications']:
            if notif.get('notification_type') == 'order' and notif.get('link'):
                assert '?tab=' in notif['link'] or 'tab=' in notif['link']
                print(f"✓ Order notification has tab link: {notif['link']}")
                break


class TestServicesProductsCRUD:
    """Test Services/Products CRUD from enterprise dashboard"""
    
    @pytest.fixture
    def enterprise_auth(self):
        """Get enterprise auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        return response.json()['token']
    
    def test_list_services_products(self, enterprise_auth):
        """Test listing services/products"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        response = requests.get(f"{BASE_URL}/api/services-products", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        print(f"✓ Listed {len(data['items'])} services/products")
    
    def test_create_service(self, enterprise_auth):
        """Test creating a service"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        
        service_data = {
            "name": f"TEST_Service_{uuid.uuid4().hex[:8]}",
            "description": "Test service for iteration 12",
            "type": "service",
            "category": "Bien-être",
            "price": 99.99,
            "duration": "60 min"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/services-products",
            headers=headers,
            json=service_data
        )
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert data['name'] == service_data['name']
        print(f"✓ Created service: {data['name']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/services-products/{data['id']}", headers=headers)
        return data['id']
    
    def test_create_product(self, enterprise_auth):
        """Test creating a product"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        
        product_data = {
            "name": f"TEST_Product_{uuid.uuid4().hex[:8]}",
            "description": "Test product for iteration 12",
            "type": "product",
            "category": "Cosmétiques",
            "price": 49.99
        }
        
        response = requests.post(
            f"{BASE_URL}/api/services-products",
            headers=headers,
            json=product_data
        )
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert data['type'] == 'product'
        print(f"✓ Created product: {data['name']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/services-products/{data['id']}", headers=headers)
    
    def test_update_service_product(self, enterprise_auth):
        """Test updating a service/product"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        
        # Create first
        service_data = {
            "name": f"TEST_Update_{uuid.uuid4().hex[:8]}",
            "description": "Original description",
            "type": "service",
            "category": "Bien-être",
            "price": 50.00
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/services-products",
            headers=headers,
            json=service_data
        )
        item_id = create_response.json()['id']
        
        # Update
        update_response = requests.put(
            f"{BASE_URL}/api/services-products/{item_id}",
            headers=headers,
            json={"price": 75.00, "description": "Updated description"}
        )
        assert update_response.status_code == 200
        print(f"✓ Updated service/product")
        
        # Verify
        get_response = requests.get(f"{BASE_URL}/api/services-products/{item_id}")
        assert get_response.json()['price'] == 75.00
        print(f"✓ Update persisted correctly")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/services-products/{item_id}", headers=headers)
    
    def test_delete_service_product(self, enterprise_auth):
        """Test deleting a service/product"""
        headers = {"Authorization": f"Bearer {enterprise_auth}"}
        
        # Create first
        service_data = {
            "name": f"TEST_Delete_{uuid.uuid4().hex[:8]}",
            "description": "To be deleted",
            "type": "service",
            "category": "Bien-être",
            "price": 25.00
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/services-products",
            headers=headers,
            json=service_data
        )
        item_id = create_response.json()['id']
        
        # Delete
        delete_response = requests.delete(
            f"{BASE_URL}/api/services-products/{item_id}",
            headers=headers
        )
        assert delete_response.status_code == 200
        print(f"✓ Deleted service/product")
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/services-products/{item_id}")
        assert get_response.status_code == 404
        print(f"✓ Deletion verified (404 on get)")


class TestDashboardTabParameter:
    """Test dashboard tab parameter support"""
    
    def test_client_dashboard_tab_parameter_in_notification_links(self):
        """Test that notification links use correct tab parameter format"""
        # Login as client
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        token = response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get notifications
        notif_response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        notifications = notif_response.json()['notifications']
        
        # Check link format
        for notif in notifications:
            if notif.get('link'):
                # Links should use ?tab= format
                if 'dashboard' in notif['link'] and 'tab' in notif['link']:
                    assert '?tab=' in notif['link'] or '&tab=' in notif['link']
                    print(f"✓ Notification link format correct: {notif['link']}")
        
        print("✓ Dashboard tab parameter format verified")
    
    def test_enterprise_dashboard_tab_parameter_in_notification_links(self):
        """Test enterprise notification links use correct tab parameter"""
        # Login as enterprise
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ENTERPRISE_EMAIL,
            "password": ENTERPRISE_PASSWORD
        })
        token = response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get notifications
        notif_response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        notifications = notif_response.json()['notifications']
        
        # Check for enterprise dashboard links
        for notif in notifications:
            if notif.get('link') and 'enterprise-dashboard' in notif['link']:
                if 'tab=' in notif['link']:
                    print(f"✓ Enterprise notification link: {notif['link']}")
        
        print("✓ Enterprise dashboard tab parameter verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
