"""Tests for get_current_user_optional dependency."""

from unittest.mock import AsyncMock, patch

import pytest

from fastapi_keycloak_auth.dependencies import get_current_user_optional
from fastapi_keycloak_auth.events import AuthEvent, auth_events
from fastapi_keycloak_auth.models import TokenPayload


def _make_request(cookies=None, headers=None):
    request = AsyncMock()
    request.cookies = cookies or {}
    request.headers = headers or {}
    return request


class TestOptionalUserWithToken:

    @pytest.mark.asyncio
    async def test_returns_token_payload_when_valid(self, keycloak_settings, keycloak_client, make_token):
        # Arrange
        token = make_token()
        request = _make_request(cookies={keycloak_settings.cookie_name: token})

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act
            result = await get_current_user_optional(request)

        # Assert
        assert isinstance(result, TokenPayload)
        assert result.sub == "test-user-id"


class TestOptionalUserWithoutToken:

    @pytest.mark.asyncio
    async def test_returns_none_when_no_token(self, keycloak_settings, keycloak_client):
        # Arrange
        request = _make_request()

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act
            result = await get_current_user_optional(request)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_invalid_token(self, keycloak_settings, keycloak_client):
        # Arrange
        request = _make_request(cookies={keycloak_settings.cookie_name: "invalid-jwt"})

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act
            result = await get_current_user_optional(request)

        # Assert
        assert result is None


class TestOptionalUserEvents:

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
            await get_current_user_optional(request)

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
            await get_current_user_optional(request)

        # Assert
        assert len(received) == 1
        assert received[0].token == "bad-token"
