"""
Run this once before the test suite to register a fresh test user.
Usage: python setup_test_user.py
"""
import requests

BASE_URL = "http://localhost:5000"
TEST_USER = "testuser"
TEST_PASS = "testpass123"
TEST_EMAIL = "testuser@test.com"

def register_test_user():
    session = requests.Session()

    # Get the register page first (for any CSRF if needed)
    session.get(f"{BASE_URL}/register")

    # Register the user
    response = session.post(f"{BASE_URL}/register", data={
        "username": TEST_USER,
        "email": TEST_EMAIL,
        "password": TEST_PASS,
        "confirm": TEST_PASS
    })

    if "login" in response.url or response.status_code == 200:
        print(f"✅ Test user '{TEST_USER}' registered successfully")
    else:
        print(f"⚠️  Registration may have failed — status: {response.status_code}")
        print("   User might already exist, which is fine.")

if __name__ == "__main__":
    register_test_user()
