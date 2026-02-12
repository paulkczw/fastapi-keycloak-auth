"""Tests for get_current_user_optional dependency."""

import pytest

from fastapi_keycloak_auth.dependencies import get_current_user_optional


class TestOptionalUserWithToken:

    @pytest.mark.asyncio
    async def test_returns_token_payload_when_valid(self):
        pytest.skip("TODO")


class TestOptionalUserWithoutToken:

    @pytest.mark.asyncio
    async def test_returns_none_when_no_token(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_returns_none_on_invalid_token(self):
        pytest.skip("TODO")


class TestOptionalUserEvents:

    @pytest.mark.asyncio
    async def test_emits_token_verified_on_success(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_emits_token_invalid_on_failure(self):
        pytest.skip("TODO")
