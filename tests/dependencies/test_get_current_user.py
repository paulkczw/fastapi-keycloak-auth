"""Tests for get_current_user dependency."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from starlette.testclient import TestClient

from fastapi_keycloak_auth.dependencies import get_current_user, get_current_user_optional
from fastapi_keycloak_auth.events import AuthEvent, auth_events
from fastapi_keycloak_auth.models import TokenPayload


def _make_request(cookies=None, headers=None):
    """Create a mock Request with optional cookies and headers."""
    request = AsyncMock()
    request.cookies = cookies or {}
    request.headers = headers or {}
    return request


class TestTokenExtraction:

    @pytest.mark.asyncio
    async def test_extracts_token_from_cookie(self, keycloak_settings, keycloak_client, make_token):
        # Arrange
        token = make_token()
        request = _make_request(cookies={keycloak_settings.cookie_name: token})

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act
            result = await get_current_user(request)

        # Assert
        assert isinstance(result, TokenPayload)
        assert result.sub == "test-user-id"

    @pytest.mark.asyncio
    async def test_extracts_token_from_authorization_header(self, keycloak_settings, keycloak_client, make_token):
        # Arrange
        token = make_token()
        request = _make_request(headers={"Authorization": f"Bearer {token}"})

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act
            result = await get_current_user(request)

        # Assert
        assert result.sub == "test-user-id"

    @pytest.mark.asyncio
    async def test_cookie_takes_precedence_over_header(self, keycloak_settings, keycloak_client, make_token):
        # Arrange
        cookie_token = make_token(sub="cookie-user")
        header_token = make_token(sub="header-user")
        request = _make_request(
            cookies={keycloak_settings.cookie_name: cookie_token},
            headers={"Authorization": f"Bearer {header_token}"},
        )

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act
            result = await get_current_user(request)

        # Assert
        assert result.sub == "cookie-user"


class TestMissingToken:

    @pytest.mark.asyncio
    async def test_raises_401_when_no_token(self, keycloak_settings, keycloak_client):
        # Arrange
        request = _make_request()

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(request)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_raises_401_with_www_authenticate_header(self, keycloak_settings, keycloak_client):
        # Arrange
        request = _make_request()

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(request)
            assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


class TestInvalidToken:

    @pytest.mark.asyncio
    async def test_raises_401_on_invalid_token(self, keycloak_settings, keycloak_client):
        # Arrange
        request = _make_request(cookies={keycloak_settings.cookie_name: "invalid-jwt"})

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(request)
            assert exc_info.value.status_code == 401


class TestEvents:

    @pytest.mark.asyncio
    async def test_emits_token_verified_on_success(self, keycloak_settings, keycloak_client, make_token):
        # Arrange
        token = make_token()
        request = _make_request(cookies={keycloak_settings.cookie_name: token})
        received = []

        @auth_events.on(AuthEvent.TOKEN_VERIFIED)
        async def handler(data):
            received.append(data)

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act
            await get_current_user(request)

        # Assert
        assert len(received) == 1
        assert received[0].user.sub == "test-user-id"

    @pytest.mark.asyncio
    async def test_emits_token_invalid_on_failure(self, keycloak_settings, keycloak_client):
        # Arrange
        request = _make_request(cookies={keycloak_settings.cookie_name: "bad-token"})
        received = []

        @auth_events.on(AuthEvent.TOKEN_INVALID)
        async def handler(data):
            received.append(data)

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act
            with pytest.raises(HTTPException):
                await get_current_user(request)

        # Assert
        assert len(received) == 1
        assert received[0].token == "bad-token"
