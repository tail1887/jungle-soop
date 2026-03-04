import pytest
import requests
import time

BASE_URL = "http://127.0.0.1:5000/api/v1/auth"

unique_email = f"jungle_{int(time.time())}@jungle.com"

def test_signup_success():
    payload = {
        "email": unique_email,
        "password": "password123",
        "nickname": "정글러"
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert "user_id" in response.json()["data"]

def test_signup_duplicate_email():
    payload = {
        "email": unique_email,
        "password": "password123",
        "nickname": "정글러"
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    assert response.status_code == 409
    assert response.json()["success"] is False

def test_signup_invalid_input():
    payload = {"email": "no_password@test.com"}
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    assert response.status_code == 400