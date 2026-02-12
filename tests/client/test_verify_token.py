"""Tests for KeycloakClient.verify_token()."""

import pytest
from jose import JWTError

from fastapi_keycloak_auth.client import KeycloakClient


class TestVerifyValidToken:

    @pytest.mark.asyncio
    async def test_valid_token_returns_token_payload(self, keycloak_client, make_token):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_token_payload_contains_correct_sub(self, keycloak_client, make_token):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_token_payload_contains_correct_email(self, keycloak_client, make_token):
        pytest.skip("TODO")


class TestVerifyInvalidToken:

    @pytest.mark.asyncio
    async def test_expired_token_raises_jwt_error(self, keycloak_client, make_token):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_tampered_token_raises_jwt_error(self, keycloak_client):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_wrong_issuer_raises_jwt_error(self, keycloak_client, make_token):
        pytest.skip("TODO")


class TestAudienceValidation:

    @pytest.mark.asyncio
    async def test_valid_audience_passes(self, keycloak_client, make_token):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_invalid_audience_raises_jwt_error(self, keycloak_client, make_token):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_token_without_audience_passes(self, keycloak_client, make_token):
        pytest.skip("TODO")
