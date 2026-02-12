"""Tests for /logout endpoint."""

import pytest


class TestLogout:

    @pytest.mark.asyncio
    async def test_redirects_to_keycloak_logout(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_deletes_access_token_cookie(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_deletes_refresh_token_cookie(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_passes_custom_redirect(self):
        pytest.skip("TODO")


class TestLogoutCallback:

    @pytest.mark.asyncio
    async def test_redirects_to_frontend(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_clears_cookies(self):
        pytest.skip("TODO")
