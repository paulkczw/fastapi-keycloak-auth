"""Tests for get_current_user dependency."""

import pytest

from fastapi_keycloak_auth.dependencies import get_current_user


class TestTokenExtraction:

    @pytest.mark.asyncio
    async def test_extracts_token_from_cookie(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_extracts_token_from_authorization_header(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_cookie_takes_precedence_over_header(self):
        pytest.skip("TODO")


class TestMissingToken:

    @pytest.mark.asyncio
    async def test_raises_401_when_no_token(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_raises_401_with_www_authenticate_header(self):
        pytest.skip("TODO")


class TestInvalidToken:

    @pytest.mark.asyncio
    async def test_raises_401_on_invalid_token(self):
        pytest.skip("TODO")


class TestEvents:

    @pytest.mark.asyncio
    async def test_emits_token_verified_on_success(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_emits_token_invalid_on_failure(self):
        pytest.skip("TODO")
