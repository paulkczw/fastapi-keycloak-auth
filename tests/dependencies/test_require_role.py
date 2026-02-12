"""Tests for require_role and require_any_role dependencies."""

import pytest

from fastapi_keycloak_auth.dependencies import require_role, require_any_role


class TestRequireRole:

    @pytest.mark.asyncio
    async def test_allows_user_with_required_role(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_raises_403_when_role_missing(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_raises_401_when_not_authenticated(self):
        pytest.skip("TODO")


class TestRequireAnyRole:

    @pytest.mark.asyncio
    async def test_allows_user_with_any_matching_role(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_raises_403_when_no_role_matches(self):
        pytest.skip("TODO")
