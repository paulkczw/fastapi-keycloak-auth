"""Tests for /callback endpoint."""

import pytest


class TestCallbackSuccess:

    @pytest.mark.asyncio
    async def test_exchanges_code_for_tokens(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_sets_access_token_cookie(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_sets_refresh_token_cookie(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_redirects_to_frontend(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_redirects_to_state_url_if_provided(self):
        pytest.skip("TODO")


class TestCallbackFailure:

    @pytest.mark.asyncio
    async def test_returns_401_on_invalid_code(self):
        pytest.skip("TODO")
