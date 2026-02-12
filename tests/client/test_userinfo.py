"""Tests for KeycloakClient.get_userinfo()."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from fastapi_keycloak_auth.client import KeycloakClient


USERINFO_DATA = {
    "sub": "user-123",
    "email": "user@example.com",
    "preferred_username": "johndoe",
}


def _mock_httpx_get(response_data=USERINFO_DATA, status_code=200):
    mock_request = httpx.Request("GET", "https://fake")
    mock_response = httpx.Response(status_code, json=response_data, request=mock_request)

    mock_http = AsyncMock()
    mock_http.get.return_value = mock_response
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=False)
    return mock_http


class TestGetUserinfo:

    @pytest.mark.asyncio
    async def test_sends_bearer_token_header(self, keycloak_client):
        # Arrange
        mock_http = _mock_httpx_get()

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient", return_value=mock_http):
            # Act
            await keycloak_client.get_userinfo("my-access-token")

        # Assert
        call_kwargs = mock_http.get.call_args
        assert call_kwargs.kwargs["headers"]["Authorization"] == "Bearer my-access-token"

    @pytest.mark.asyncio
    async def test_returns_userinfo_dict(self, keycloak_client):
        # Arrange
        mock_http = _mock_httpx_get()

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient", return_value=mock_http):
            # Act
            result = await keycloak_client.get_userinfo("token")

        # Assert
        assert result == USERINFO_DATA
        assert result["sub"] == "user-123"

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self, keycloak_client):
        # Arrange
        mock_http = _mock_httpx_get(status_code=401)

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient", return_value=mock_http):
            # Act & Assert
            with pytest.raises(httpx.HTTPStatusError):
                await keycloak_client.get_userinfo("bad-token")
