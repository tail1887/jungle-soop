import pytest
import requests
import time

BASE_URL = "http://127.0.0.1:5000/api/v1/auth"

def test_login_logout_flow():
    unique_email = f"user_{int(time.time())}@jungle.com"
    password = "password123"

    signup_payload = {
        "email": unique_email,
        "password": password,
        "nickname": "테스터"
    }
    signup_res = requests.post(f"{BASE_URL}/signup", json=signup_payload)
    assert signup_res.status_code == 201

    login_payload = {
        "email": unique_email,
        "password": password
    }
    login_res = requests.post(f"{BASE_URL}/login", json=login_payload)
    
    assert login_res.status_code == 200
    data = login_res.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data

    logout_res = requests.post(f"{BASE_URL}/logout")
    assert logout_res.status_code == 200
    assert logout_res.json()["success"] is True