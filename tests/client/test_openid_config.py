"""Tests for KeycloakClient.get_openid_configuration()."""

import pytest

from fastapi_keycloak_auth.client import KeycloakClient


class TestGetOpenIdConfiguration:

    @pytest.mark.asyncio
    async def test_fetches_configuration_from_keycloak(self, keycloak_settings, openid_configuration):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_caches_configuration(self, keycloak_settings, openid_configuration):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_returns_openid_configuration_model(self, keycloak_client, openid_configuration):
        pytest.skip("TODO")
