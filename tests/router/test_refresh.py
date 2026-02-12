"""Tests for /refresh endpoint."""

import httpx
import pytest
from unittest.mock import AsyncMock


class TestRefresh:

    def test_refreshes_token_from_cookie(self, client, keycloak_client, mock_refresh_tokens, keycloak_settings):
        # Arrange
        client.cookies.set(keycloak_settings.refresh_cookie_name, "cookie-refresh-token")

        # Act
        response = client.post("/auth/refresh")

        # Assert
        keycloak_client.refresh_tokens.assert_called_once_with("cookie-refresh-token")
        assert response.status_code == 200

    def test_refreshes_token_from_body(self, client, keycloak_client, mock_refresh_tokens):
        # Act
        response = client.post("/auth/refresh?refresh_token=body-refresh-token")

        # Assert
        keycloak_client.refresh_tokens.assert_called_once_with("body-refresh-token")
        assert response.status_code == 200

    def test_returns_new_access_token(self, client, mock_refresh_tokens, keycloak_settings):
        # Arrange
        client.cookies.set(keycloak_settings.refresh_cookie_name, "token")

        # Act
        response = client.post("/auth/refresh")

        # Assert
        data = response.json()
        assert data["access_token"] == "refreshed-access-token"
        assert data["expires_in"] == 300

    def test_returns_400_when_no_refresh_token(self, client):
        # Act
        response = client.post("/auth/refresh")

        # Assert
        assert response.status_code == 400

    def test_returns_401_on_invalid_refresh_token(self, client, keycloak_client, keycloak_settings):
        # Arrange
        client.cookies.set(keycloak_settings.refresh_cookie_name, "expired-token")
        mock_response = httpx.Response(401, json={"error": "invalid_grant"})
        mock_response.request = httpx.Request("POST", "https://fake")
        keycloak_client.refresh_tokens = AsyncMock(
            side_effect=httpx.HTTPStatusError("Unauthorized", request=mock_response.request, response=mock_response)
        )

        # Act
        response = client.post("/auth/refresh")

        # Assert
        assert response.status_code == 401
