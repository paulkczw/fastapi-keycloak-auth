"""Tests for /callback endpoint."""

import httpx
import pytest
from unittest.mock import AsyncMock


class TestCallbackSuccess:

    def test_exchanges_code_for_tokens(self, client, keycloak_client, mock_exchange_code):
        # Act
        client.get("/auth/callback?code=auth-code-123")

        # Assert
        keycloak_client.exchange_code.assert_called_once_with("auth-code-123")

    def test_sets_access_token_cookie(self, client, mock_exchange_code):
        # Act
        response = client.get("/auth/callback?code=test-code")

        # Assert
        assert "access_token" in response.cookies

    def test_sets_refresh_token_cookie(self, client, keycloak_client, mock_exchange_code, make_token):
        # Arrange — verify_token must succeed for refresh cookie branch
        token = make_token()
        mock_exchange_code.access_token = token
        keycloak_client.exchange_code = AsyncMock(return_value=mock_exchange_code)

        # Act
        response = client.get("/auth/callback?code=test-code")

        # Assert
        assert "refresh_token" in response.cookies

    def test_redirects_to_frontend(self, client, mock_exchange_code):
        # Act
        response = client.get("/auth/callback?code=test-code")

        # Assert
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost:5173/"

    def test_redirects_to_state_url_if_provided(self, client, mock_exchange_code):
        # Act
        response = client.get("/auth/callback?code=test-code&state=https://app.test/page")

        # Assert
        assert response.status_code == 302
        assert response.headers["location"] == "https://app.test/page"


class TestCallbackFailure:

    def test_returns_401_on_invalid_code(self, client, keycloak_client):
        # Arrange
        mock_response = httpx.Response(400, json={"error": "invalid_grant"})
        mock_response.request = httpx.Request("POST", "https://fake")
        keycloak_client.exchange_code = AsyncMock(
            side_effect=httpx.HTTPStatusError("Bad Request", request=mock_response.request, response=mock_response)
        )

        # Act
        response = client.get("/auth/callback?code=bad-code")

        # Assert
        assert response.status_code == 401
