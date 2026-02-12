"""Tests for KeycloakClient.exchange_code() and refresh_tokens()."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from fastapi_keycloak_auth.client import KeycloakClient
from fastapi_keycloak_auth.models import TokenResponse


TOKEN_RESPONSE_DATA = {
    "access_token": "new-access-token",
    "refresh_token": "new-refresh-token",
    "token_type": "Bearer",
    "expires_in": 300,
}


def _mock_httpx_post(response_data=TOKEN_RESPONSE_DATA, status_code=200):
    """Create a patched httpx.AsyncClient that returns a mock POST response."""
    mock_request = httpx.Request("POST", "https://fake")
    mock_response = httpx.Response(status_code, json=response_data, request=mock_request)

    mock_http = AsyncMock()
    mock_http.post.return_value = mock_response
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=False)
    return mock_http


class TestExchangeCode:

    @pytest.mark.asyncio
    async def test_sends_correct_grant_type(self, keycloak_client):
        # Arrange
        mock_http = _mock_httpx_post()

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient", return_value=mock_http):
            # Act
            await keycloak_client.exchange_code("auth-code-123")

        # Assert
        call_kwargs = mock_http.post.call_args
        assert call_kwargs.kwargs["data"]["grant_type"] == "authorization_code"
        assert call_kwargs.kwargs["data"]["code"] == "auth-code-123"

    @pytest.mark.asyncio
    async def test_sends_client_credentials(self, keycloak_client):
        # Arrange
        mock_http = _mock_httpx_post()

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient", return_value=mock_http):
            # Act
            await keycloak_client.exchange_code("code")

        # Assert
        data = mock_http.post.call_args.kwargs["data"]
        assert data["client_id"] == "test-client"
        assert data["client_secret"] == "test-secret"

    @pytest.mark.asyncio
    async def test_returns_token_response(self, keycloak_client):
        # Arrange
        mock_http = _mock_httpx_post()

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient", return_value=mock_http):
            # Act
            result = await keycloak_client.exchange_code("code")

        # Assert
        assert isinstance(result, TokenResponse)
        assert result.access_token == "new-access-token"
        assert result.refresh_token == "new-refresh-token"
        assert result.expires_in == 300

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self, keycloak_client):
        # Arrange
        mock_http = _mock_httpx_post(status_code=400)

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient", return_value=mock_http):
            # Act & Assert
            with pytest.raises(httpx.HTTPStatusError):
                await keycloak_client.exchange_code("bad-code")


class TestRefreshTokens:

    @pytest.mark.asyncio
    async def test_sends_refresh_grant_type(self, keycloak_client):
        # Arrange
        mock_http = _mock_httpx_post()

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient", return_value=mock_http):
            # Act
            await keycloak_client.refresh_tokens("refresh-token-abc")

        # Assert
        data = mock_http.post.call_args.kwargs["data"]
        assert data["grant_type"] == "refresh_token"
        assert data["refresh_token"] == "refresh-token-abc"

    @pytest.mark.asyncio
    async def test_returns_new_tokens(self, keycloak_client):
        # Arrange
        mock_http = _mock_httpx_post()

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient", return_value=mock_http):
            # Act
            result = await keycloak_client.refresh_tokens("refresh-token")

        # Assert
        assert isinstance(result, TokenResponse)
        assert result.access_token == "new-access-token"

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self, keycloak_client):
        # Arrange
        mock_http = _mock_httpx_post(status_code=401)

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient", return_value=mock_http):
            # Act & Assert
            with pytest.raises(httpx.HTTPStatusError):
                await keycloak_client.refresh_tokens("expired-token")
