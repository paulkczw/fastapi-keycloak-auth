"""Tests for /me endpoint."""

import pytest


class TestMe:

    @pytest.mark.asyncio
    async def test_returns_user_json_when_authenticated(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_returns_401_when_not_authenticated(self):
        pytest.skip("TODO")
