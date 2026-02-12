"""Tests for KeycloakClient.exchange_code() and refresh_tokens()."""

import pytest

from fastapi_keycloak_auth.client import KeycloakClient


class TestExchangeCode:

    @pytest.mark.asyncio
    async def test_sends_correct_grant_type(self, keycloak_client):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_sends_client_credentials(self, keycloak_client):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_returns_token_response(self, keycloak_client):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self, keycloak_client):
        pytest.skip("TODO")


class TestRefreshTokens:

    @pytest.mark.asyncio
    async def test_sends_refresh_grant_type(self, keycloak_client):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_returns_new_tokens(self, keycloak_client):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self, keycloak_client):
        pytest.skip("TODO")
