"""Tests for /login endpoint."""

import pytest


class TestLoginRedirect:

    @pytest.mark.asyncio
    async def test_redirects_to_keycloak_auth_endpoint(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_includes_client_id_in_params(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_includes_redirect_uri_in_params(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_passes_custom_redirect_as_state(self):
        pytest.skip("TODO")
