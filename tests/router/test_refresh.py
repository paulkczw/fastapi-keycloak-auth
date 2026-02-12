"""Tests for /refresh endpoint."""

import pytest


class TestRefresh:

    @pytest.mark.asyncio
    async def test_refreshes_token_from_cookie(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_refreshes_token_from_body(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_returns_new_access_token(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_returns_400_when_no_refresh_token(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_returns_401_on_invalid_refresh_token(self):
        pytest.skip("TODO")
