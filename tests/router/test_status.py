"""Tests for /status endpoint."""

import pytest


class TestStatus:

    @pytest.mark.asyncio
    async def test_returns_200_always(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_authenticated_true_with_valid_token(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_authenticated_false_without_token(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_includes_user_when_authenticated(self):
        pytest.skip("TODO")
