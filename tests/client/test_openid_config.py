"""Tests for KeycloakClient.get_openid_configuration()."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from fastapi_keycloak_auth.client import KeycloakClient
from fastapi_keycloak_auth.models import OpenIdConfiguration


class TestGetOpenIdConfiguration:

    @pytest.mark.asyncio
    async def test_fetches_configuration_from_keycloak(self, keycloak_settings, openid_configuration):
        # Arrange
        client = KeycloakClient(keycloak_settings)  # fresh client, no cache
        mock_response = httpx.Response(200, json=openid_configuration.model_dump(), request=httpx.Request("GET", "https://fake"))

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.get.return_value = mock_response
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            # Act
            result = await client.get_openid_configuration()

        # Assert
        mock_http.get.assert_called_once_with(keycloak_settings.configuration_url)
        assert result.issuer == openid_configuration.issuer

    @pytest.mark.asyncio
    async def test_caches_configuration(self, keycloak_settings, openid_configuration):
        # Arrange
        client = KeycloakClient(keycloak_settings)
        mock_response = httpx.Response(200, json=openid_configuration.model_dump(), request=httpx.Request("GET", "https://fake"))

        with patch("fastapi_keycloak_auth.client.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.get.return_value = mock_response
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            # Act
            await client.get_openid_configuration()
            await client.get_openid_configuration()

        # Assert — only one HTTP call despite two invocations
        assert mock_http.get.call_count == 1

    @pytest.mark.asyncio
    async def test_returns_openid_configuration_model(self, keycloak_client, openid_configuration):
        # Act (keycloak_client already has cached config)
        result = await keycloak_client.get_openid_configuration()

        # Assert
        assert isinstance(result, OpenIdConfiguration)
        assert result.token_endpoint == openid_configuration.token_endpoint
