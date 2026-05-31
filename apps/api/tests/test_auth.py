"""
AxonBridge — Auth Endpoint Tests
"""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Successful login returns token pair."""
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "TestPassword123!",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user: User):
    """Login with wrong password returns 401."""
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "WrongPassword123!",
    })
    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Login with unknown email returns 401."""
    response = await client.post("/api/v1/auth/login", json={
        "email": "nobody@nowhere.com",
        "password": "SomePassword123!",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_auth(client: AsyncClient):
    """Accessing protected route without token returns 401."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_auth(client: AsyncClient, auth_headers: dict):
    """Accessing protected route with valid token returns 200."""
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "full_name" in data


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers: dict):
    """Logout invalidates the session."""
    response = await client.post("/api/v1/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged out"
