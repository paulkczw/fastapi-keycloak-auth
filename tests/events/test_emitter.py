"""Tests for AuthEventEmitter core functionality."""

import pytest

from fastapi_keycloak_auth.events import AuthEventEmitter, AuthEvent


class TestRegisterHandler:

    @pytest.mark.asyncio
    async def test_register_via_decorator(self):
        # Arrange
        emitter = AuthEventEmitter()

        @emitter.on(AuthEvent.LOGIN)
        async def handler(data):
            pass

        # Act & Assert
        assert emitter.has_handlers(AuthEvent.LOGIN) is True

    @pytest.mark.asyncio
    async def test_register_via_add_handler(self):
        # Arrange
        emitter = AuthEventEmitter()

        async def handler(data):
            pass

        # Act
        emitter.add_handler(AuthEvent.LOGIN, handler)

        # Assert
        assert emitter.has_handlers(AuthEvent.LOGIN) is True

    @pytest.mark.asyncio
    async def test_duplicate_handler_not_added(self):
        # Arrange
        emitter = AuthEventEmitter()

        async def handler(data):
            pass

        # Act
        emitter.add_handler(AuthEvent.LOGIN, handler)
        emitter.add_handler(AuthEvent.LOGIN, handler)

        # Assert
        assert len(emitter._handlers[AuthEvent.LOGIN]) == 1

    @pytest.mark.asyncio
    async def test_remove_handler(self):
        # Arrange
        emitter = AuthEventEmitter()

        async def handler(data):
            pass

        emitter.add_handler(AuthEvent.LOGIN, handler)

        # Act
        emitter.remove_handler(AuthEvent.LOGIN, handler)

        # Assert
        assert emitter.has_handlers(AuthEvent.LOGIN) is False

    @pytest.mark.asyncio
    async def test_clear_handlers_for_event(self):
        # Arrange
        emitter = AuthEventEmitter()

        @emitter.on(AuthEvent.LOGIN)
        async def h1(data):
            pass

        @emitter.on(AuthEvent.LOGOUT)
        async def h2(data):
            pass

        # Act
        emitter.clear_handlers(AuthEvent.LOGIN)

        # Assert
        assert emitter.has_handlers(AuthEvent.LOGIN) is False
        assert emitter.has_handlers(AuthEvent.LOGOUT) is True

    @pytest.mark.asyncio
    async def test_clear_all_handlers(self):
        # Arrange
        emitter = AuthEventEmitter()

        @emitter.on(AuthEvent.LOGIN)
        async def h1(data):
            pass

        @emitter.on(AuthEvent.LOGOUT)
        async def h2(data):
            pass

        # Act
        emitter.clear_handlers()

        # Assert
        assert emitter.has_handlers(AuthEvent.LOGIN) is False
        assert emitter.has_handlers(AuthEvent.LOGOUT) is False


class TestEmit:

    @pytest.mark.asyncio
    async def test_emit_calls_handler_with_data(self):
        # Arrange
        emitter = AuthEventEmitter()
        received = []

        @emitter.on(AuthEvent.LOGIN)
        async def handler(data):
            received.append(data)

        # Act
        await emitter.emit(AuthEvent.LOGIN, "test-data")

        # Assert
        assert received == ["test-data"]

    @pytest.mark.asyncio
    async def test_emit_calls_handlers_in_registration_order(self):
        # Arrange
        emitter = AuthEventEmitter()
        order = []

        @emitter.on(AuthEvent.LOGIN)
        async def first(data):
            order.append("first")

        @emitter.on(AuthEvent.LOGIN)
        async def second(data):
            order.append("second")

        @emitter.on(AuthEvent.LOGIN)
        async def third(data):
            order.append("third")

        # Act
        await emitter.emit(AuthEvent.LOGIN)

        # Assert
        assert order == ["first", "second", "third"]

    @pytest.mark.asyncio
    async def test_emit_with_no_handlers_does_not_raise(self):
        # Arrange
        emitter = AuthEventEmitter()

        # Act & Assert (should not raise)
        await emitter.emit(AuthEvent.LOGIN, "data")


class TestHasHandlers:

    def test_has_handlers_returns_false_initially(self):
        # Arrange
        emitter = AuthEventEmitter()

        # Act & Assert
        assert emitter.has_handlers(AuthEvent.LOGIN) is False

    @pytest.mark.asyncio
    async def test_has_handlers_returns_true_after_registration(self):
        # Arrange
        emitter = AuthEventEmitter()

        @emitter.on(AuthEvent.LOGIN)
        async def handler(data):
            pass

        # Act & Assert
        assert emitter.has_handlers(AuthEvent.LOGIN) is True
