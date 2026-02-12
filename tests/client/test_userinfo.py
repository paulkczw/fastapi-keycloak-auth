"""Tests for KeycloakClient.get_userinfo()."""

import pytest

from fastapi_keycloak_auth.client import KeycloakClient


class TestGetUserinfo:

    @pytest.mark.asyncio
    async def test_sends_bearer_token_header(self, keycloak_client):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_returns_userinfo_dict(self, keycloak_client):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self, keycloak_client):
        pytest.skip("TODO")
