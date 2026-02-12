"""Tests for error handling in event emitter."""

import logging

import pytest

from fastapi_keycloak_auth.events import AuthEventEmitter, AuthEvent


class TestHandlerErrors:

    @pytest.mark.asyncio
    async def test_error_in_handler_does_not_stop_other_handlers(self):
        # Arrange
        emitter = AuthEventEmitter()
        results = []

        @emitter.on(AuthEvent.LOGIN)
        async def failing_handler(data):
            raise ValueError("boom")

        @emitter.on(AuthEvent.LOGIN)
        async def succeeding_handler(data):
            results.append("ok")

        # Act
        await emitter.emit(AuthEvent.LOGIN)

        # Assert
        assert results == ["ok"]

    @pytest.mark.asyncio
    async def test_error_in_handler_is_logged(self, caplog):
        # Arrange
        emitter = AuthEventEmitter()

        @emitter.on(AuthEvent.LOGIN)
        async def failing_handler(data):
            raise ValueError("test error")

        # Act
        with caplog.at_level(logging.ERROR):
            await emitter.emit(AuthEvent.LOGIN)

        # Assert
        assert "test error" in caplog.text
        assert "failing_handler" in caplog.text

    @pytest.mark.asyncio
    async def test_all_handlers_run_even_if_first_fails(self):
        # Arrange
        emitter = AuthEventEmitter()
        called = []

        @emitter.on(AuthEvent.LOGIN)
        async def handler_1(data):
            raise RuntimeError("fail")

        @emitter.on(AuthEvent.LOGIN)
        async def handler_2(data):
            called.append("h2")

        @emitter.on(AuthEvent.LOGIN)
        async def handler_3(data):
            called.append("h3")

        # Act
        await emitter.emit(AuthEvent.LOGIN)

        # Assert
        assert called == ["h2", "h3"]
