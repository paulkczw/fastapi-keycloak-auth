"""Tests for require_role and require_any_role dependencies."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from fastapi_keycloak_auth.dependencies import require_role, require_any_role


def _make_request(cookies=None, headers=None):
    request = AsyncMock()
    request.cookies = cookies or {}
    request.headers = headers or {}
    return request


class TestRequireRole:

    @pytest.mark.asyncio
    async def test_allows_user_with_required_role(self, keycloak_settings, keycloak_client, make_token):
        # Arrange
        token = make_token(realm_roles=["admin", "user"])
        request = _make_request(cookies={keycloak_settings.cookie_name: token})
        checker = require_role("admin")

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act
            result = await checker(request)

        # Assert
        assert result.has_role("admin") is True

    @pytest.mark.asyncio
    async def test_raises_403_when_role_missing(self, keycloak_settings, keycloak_client, make_token):
        # Arrange
        token = make_token(realm_roles=["user"])
        request = _make_request(cookies={keycloak_settings.cookie_name: token})
        checker = require_role("admin")

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await checker(request)
            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_raises_401_when_not_authenticated(self, keycloak_settings, keycloak_client):
        # Arrange
        request = _make_request()
        checker = require_role("admin")

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await checker(request)
            assert exc_info.value.status_code == 401


class TestRequireAnyRole:

    @pytest.mark.asyncio
    async def test_allows_user_with_any_matching_role(self, keycloak_settings, keycloak_client, make_token):
        # Arrange
        token = make_token(realm_roles=["moderator"])
        request = _make_request(cookies={keycloak_settings.cookie_name: token})
        checker = require_any_role("admin", "moderator")

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act
            result = await checker(request)

        # Assert
        assert result.has_role("moderator") is True

    @pytest.mark.asyncio
    async def test_raises_403_when_no_role_matches(self, keycloak_settings, keycloak_client, make_token):
        # Arrange
        token = make_token(realm_roles=["user"])
        request = _make_request(cookies={keycloak_settings.cookie_name: token})
        checker = require_any_role("admin", "moderator")

        with patch("fastapi_keycloak_auth.dependencies._settings", keycloak_settings), \
             patch("fastapi_keycloak_auth.dependencies._client", keycloak_client):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await checker(request)
            assert exc_info.value.status_code == 403
