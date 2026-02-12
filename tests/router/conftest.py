"""Shared fixtures for router integration tests."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_keycloak_auth.router import create_auth_router
from fastapi_keycloak_auth.models import TokenResponse


@pytest.fixture
def app(keycloak_settings, keycloak_client):
    """FastAPI app with auth router and mocked singletons."""
    with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
         patch("fastapi_keycloak_auth.dependencies._client", keycloak_client), \
         patch("fastapi_keycloak_auth.router.get_settings", return_value=keycloak_settings), \
         patch("fastapi_keycloak_auth.router.get_keycloak_client", return_value=keycloak_client):
        router = create_auth_router(prefix="/auth")
        application = FastAPI()
        application.include_router(router)
        yield application


@pytest.fixture
def client(app):
    """TestClient (sync) for the FastAPI app."""
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def mock_exchange_code(keycloak_client):
    """Mock exchange_code to return test tokens."""
    token_response = TokenResponse(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        token_type="Bearer",
        expires_in=300,
    )
    keycloak_client.exchange_code = AsyncMock(return_value=token_response)
    return token_response


@pytest.fixture
def mock_refresh_tokens(keycloak_client):
    """Mock refresh_tokens to return new tokens."""
    token_response = TokenResponse(
        access_token="refreshed-access-token",
        refresh_token="refreshed-refresh-token",
        token_type="Bearer",
        expires_in=300,
    )
    keycloak_client.refresh_tokens = AsyncMock(return_value=token_response)
    return token_response
