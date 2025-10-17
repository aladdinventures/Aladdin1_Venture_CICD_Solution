"""
API Testing Script for YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

import httpx
import asyncio
import os
import json

# --- Configuration ---
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Test user credentials
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "test@example.com")
TEST_USERNAME = os.getenv("TEST_USERNAME", "testuser")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "TestPass123!")

# --- Global Variables ---
ACCESS_TOKEN = None
REFRESH_TOKEN = None
TEST_CHANNEL_ID = None
TEST_VIDEO_ID = None

async def call_api(method: str, url: str, **kwargs):
    """
    Helper function to call the API with authentication.
    """
    headers = kwargs.pop("headers", {})
    if ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, f"{BASE_URL}{url}", headers=headers, **kwargs)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            print(f"✅ {method} {url} - Status: {response.status_code}")
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"❌ {method} {url} - HTTP Error: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"❌ {method} {url} - Request Error: {e}")
            return None

async def test_health_check():
    print("\n--- Testing Health Check ---")
    response = await call_api("GET", "/health")
    assert response is not None and response["status"] == "healthy"

async def test_root_endpoint():
    print("\n--- Testing Root Endpoint ---")
    response = await call_api("GET", "/")
    assert response is not None and "YouTube Automation System v3.0" in response["message"]

async def test_auth_register():
    global ACCESS_TOKEN, REFRESH_TOKEN
    print("\n--- Testing User Registration ---")
    # Try to register a new user
    user_data = {
        "email": TEST_USER_EMAIL,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "full_name": "Test User"
    }
    response = await call_api("POST", "/api/v1/auth/register", json=user_data)
    if response:
        assert response["email"] == TEST_USER_EMAIL
        print(f"User {TEST_USERNAME} registered successfully.")
    else:
        # If registration fails, it might be because the user already exists
        # Try to log in instead
        print(f"Registration failed for {TEST_USERNAME}. Attempting login...")
        await test_auth_login()

async def test_auth_login():
    global ACCESS_TOKEN, REFRESH_TOKEN
    print("\n--- Testing User Login ---")
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = await call_api("POST", "/api/v1/auth/login", data=login_data)
    if response:
        ACCESS_TOKEN = response["access_token"]
        REFRESH_TOKEN = response["refresh_token"]
        assert ACCESS_TOKEN is not None
        assert REFRESH_TOKEN is not None
        print("Login successful. Tokens obtained.")
    else:
        print("Login failed. Please ensure the user exists and credentials are correct.")

async def test_auth_me():
    print("\n--- Testing Get Current User Info (/me) ---")
    if not ACCESS_TOKEN:
        print("Skipping /me test: No access token.")
        return
    response = await call_api("GET", "/api/v1/auth/me")
    assert response is not None and response["username"] == TEST_USERNAME
    print(f"Current user info: {response['username']}")

async def test_auth_update_user():
    print("\n--- Testing Update Current User Info (/me PUT) ---")
    if not ACCESS_TOKEN:
        print("Skipping /me PUT test: No access token.")
        return
    update_data = {"full_name": "Updated Test User"}
    response = await call_api("PUT", "/api/v1/auth/me", json=update_data)
    assert response is not None and response["full_name"] == "Updated Test User"
    print(f"User full name updated to: {response['full_name']}")

async def test_auth_change_password():
    print("\n--- Testing Change Password ---")
    if not ACCESS_TOKEN:
        print("Skipping change password test: No access token.")
        return
    change_data = {
        "old_password": TEST_PASSWORD,
        "new_password": "NewTestPass123!"
    }
    response = await call_api("POST", "/api/v1/auth/change-password", json=change_data)
    assert response is not None and response["message"] == "Password changed successfully"
    print("Password changed successfully.")
    
    # Revert password for subsequent tests
    change_data = {
        "old_password": "NewTestPass123!",
        "new_password": TEST_PASSWORD
    }
    response = await call_api("POST", "/api/v1/auth/change-password", json=change_data)
    assert response is not None and response["message"] == "Password changed successfully"
    print("Password reverted for subsequent tests.")

async def test_channels_create():
    global TEST_CHANNEL_ID
    print("\n--- Testing Create Channel ---")
    if not ACCESS_TOKEN:
        print("Skipping create channel test: No access token.")
        return
    channel_data = {
        "name": "My Test Channel",
        "description": "A channel for testing purposes.",
        "niche": "Tech",
        "auto_upload": True,
        "auto_generate": True
    }
    response = await call_api("POST", "/api/v1/channels/", json=channel_data)
    assert response is not None and response["name"] == "My Test Channel"
    TEST_CHANNEL_ID = response["id"]
    print(f"Channel created with ID: {TEST_CHANNEL_ID}")

async def test_channels_list():
    print("\n--- Testing List Channels ---")
    if not ACCESS_TOKEN:
        print("Skipping list channels test: No access token.")
        return
    response = await call_api("GET", "/api/v1/channels/")
    assert response is not None and response["total"] >= 1
    print(f"Found {response['total']} channels.")

async def test_channels_get():
    print("\n--- Testing Get Channel ---")
    if not ACCESS_TOKEN or not TEST_CHANNEL_ID:
        print("Skipping get channel test: No access token or channel ID.")
        return
    response = await call_api("GET", f"/api/v1/channels/{TEST_CHANNEL_ID}")
    assert response is not None and response["id"] == TEST_CHANNEL_ID
    print(f"Retrieved channel: {response['name']}")

async def test_channels_update():
    print("\n--- Testing Update Channel ---")
    if not ACCESS_TOKEN or not TEST_CHANNEL_ID:
        print("Skipping update channel test: No access token or channel ID.")
        return
    update_data = {"description": "Updated description for testing.", "status": "inactive"}
    response = await call_api("PUT", f"/api/v1/channels/{TEST_CHANNEL_ID}", json=update_data)
    assert response is not None and response["description"] == "Updated description for testing." and response["status"] == "inactive"
    print(f"Channel {TEST_CHANNEL_ID} updated.")

async def test_videos_create():
    global TEST_VIDEO_ID
    print("\n--- Testing Create Video ---")
    if not ACCESS_TOKEN or not TEST_CHANNEL_ID:
        print("Skipping create video test: No access token or channel ID.")
        return
    video_data = {
        "title": "My First Test Video",
        "description": "This is a test video generated by the system.",
        "channel_id": TEST_CHANNEL_ID,
        "metadata": {"tags": ["test", "automation"], "category": "Science & Technology"}
    }
    response = await call_api("POST", "/api/v1/videos/", json=video_data)
    assert response is not None and response["title"] == "My First Test Video"
    TEST_VIDEO_ID = response["id"]
    print(f"Video created with ID: {TEST_VIDEO_ID}")

async def test_videos_list():
    print("\n--- Testing List Videos ---")
    if not ACCESS_TOKEN:
        print("Skipping list videos test: No access token.")
        return
    response = await call_api("GET", "/api/v1/videos/", params={"channel_id": TEST_CHANNEL_ID})
    assert response is not None and response["total"] >= 1
    print(f"Found {response['total']} videos.")

async def test_videos_get():
    print("\n--- Testing Get Video ---")
    if not ACCESS_TOKEN or not TEST_VIDEO_ID:
        print("Skipping get video test: No access token or video ID.")
        return
    response = await call_api("GET", f"/api/v1/videos/{TEST_VIDEO_ID}")
    assert response is not None and response["id"] == TEST_VIDEO_ID
    print(f"Retrieved video: {response['title']}")

async def test_videos_update():
    print("\n--- Testing Update Video ---")
    if not ACCESS_TOKEN or not TEST_VIDEO_ID:
        print("Skipping update video test: No access token or video ID.")
        return
    update_data = {"description": "Updated video description.", "status": "generating"}
    response = await call_api("PUT", f"/api/v1/videos/{TEST_VIDEO_ID}", json=update_data)
    assert response is not None and response["description"] == "Updated video description." and response["status"] == "generating"
    print(f"Video {TEST_VIDEO_ID} updated.")

async def test_videos_generate():
    print("\n--- Testing Generate Video ---")
    if not ACCESS_TOKEN or not TEST_VIDEO_ID:
        print("Skipping generate video test: No access token or video ID.")
        return
    generate_data = {"prompt": "A video about the future of AI.", "duration": 600}
    response = await call_api("POST", f"/api/v1/videos/{TEST_VIDEO_ID}/generate", json=generate_data)
    assert response is not None and response["status"] == "generating"
    print(f"Video {TEST_VIDEO_ID} generation queued.")

async def test_videos_progress():
    print("\n--- Testing Get Video Progress ---")
    if not ACCESS_TOKEN or not TEST_VIDEO_ID:
        print("Skipping get video progress test: No access token or video ID.")
        return
    response = await call_api("GET", f"/api/v1/videos/{TEST_VIDEO_ID}/progress")
    assert response is not None and "progress" in response
    print(f"Video {TEST_VIDEO_ID} progress: {response['progress']}%")

async def test_videos_upload():
    print("\n--- Testing Upload Video ---")
    if not ACCESS_TOKEN or not TEST_VIDEO_ID:
        print("Skipping upload video test: No access token or video ID.")
        return
    # First, simulate video being generated
    update_data = {"status": "generated"}
    await call_api("PUT", f"/api/v1/videos/{TEST_VIDEO_ID}", json=update_data)
    
    upload_data = {"privacy": "unlisted", "notify_subscribers": False}
    response = await call_api("POST", f"/api/v1/videos/{TEST_VIDEO_ID}/upload", json=upload_data)
    assert response is not None and response["status"] == "uploading"
    print(f"Video {TEST_VIDEO_ID} upload queued.")

async def test_analytics_video():
    print("\n--- Testing Get Video Analytics ---")
    if not ACCESS_TOKEN or not TEST_VIDEO_ID:
        print("Skipping get video analytics test: No access token or video ID.")
        return
    response = await call_api("GET", f"/api/v1/analytics/video/{TEST_VIDEO_ID}")
    assert response is not None and "views" in response
    print(f"Video {TEST_VIDEO_ID} analytics: Views={response['views']}")

async def test_analytics_channel():
    print("\n--- Testing Get Channel Analytics ---")
    if not ACCESS_TOKEN or not TEST_CHANNEL_ID:
        print("Skipping get channel analytics test: No access token or channel ID.")
        return
    response = await call_api("GET", f"/api/v1/analytics/channel/{TEST_CHANNEL_ID}")
    assert response is not None and "total_videos" in response
    print(f"Channel {TEST_CHANNEL_ID} analytics: Total Videos={response['total_videos']}")

async def test_analytics_summary():
    print("\n--- Testing Get Analytics Summary ---")
    if not ACCESS_TOKEN:
        print("Skipping get analytics summary test: No access token.")
        return
    response = await call_api("GET", "/api/v1/analytics/summary")
    assert response is not None and "total_channels" in response
    print(f"Overall analytics summary: Total Channels={response['total_channels']}")

async def test_channels_delete():
    print("\n--- Testing Delete Channel ---")
    if not ACCESS_TOKEN or not TEST_CHANNEL_ID:
        print("Skipping delete channel test: No access token or channel ID.")
        return
    response = await call_api("DELETE", f"/api/v1/channels/{TEST_CHANNEL_ID}")
    assert response is None # 204 No Content
    print(f"Channel {TEST_CHANNEL_ID} deleted.")

async def main():
    print("Starting API integration tests...")
    
    await test_health_check()
    await test_root_endpoint()
    
    # Authentication tests
    await test_auth_register()
    await test_auth_login()
    await test_auth_me()
    await test_auth_update_user()
    await test_auth_change_password()
    
    # Channel tests
    await test_channels_create()
    await test_channels_list()
    await test_channels_get()
    await test_channels_update()
    
    # Video tests
    await test_videos_create()
    await test_videos_list()
    await test_videos_get()
    await test_videos_update()
    await test_videos_generate()
    await test_videos_progress()
    await test_videos_upload()
    
    # Analytics tests
    await test_analytics_video()
    await test_analytics_channel()
    await test_analytics_summary()
    
    # Cleanup
    await test_channels_delete() # This will also delete associated videos due to cascade
    
    print("\nAPI integration tests completed.")

if __name__ == "__main__":
    asyncio.run(main())

