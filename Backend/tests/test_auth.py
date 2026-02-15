import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ["ENV"] = "test"

import pytest
from httpx import AsyncClient
from app.main import app
import httpx

@pytest.mark.asyncio
async def test_health_check():
    transport = httpx.ASGITransport(app = app)
    
    async with httpx.AsyncClient(
        transport = transport,
        base_url = "http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_login_invalid():
    transport = httpx.ASGITransport(app = app)

    async with httpx.AsyncClient(
        transport = transport,
        base_url = "http://test"
    ) as client:
        response = await client.post("/auth/login", params = {
            "email": "invalid@test.com",
            "password": "wrong"
        })
    
    assert response.status_code in [400, 401]