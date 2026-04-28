"""Tests for BaseStateEventProcessor, specifically the _rehydrate path."""

import traceback
from collections.abc import Mapping
from typing import Any

import pytest
import pytest_asyncio
from reflex_base.constants import CompileVars
from reflex_base.constants.state import FIELD_MARKER
from reflex_base.event.context import EventContext
from reflex_base.event.processor import BaseStateEventProcessor
from reflex_base.registry import RegistrationContext

from reflex import event
from reflex.app import App
from reflex.event import Event
from reflex.istate.manager.memory import StateManagerMemory
from reflex.istate.manager.token import BaseStateToken
from reflex.state import OnLoadInternalState, State


@pytest.fixture
def _real_base_state_processor_obj() -> BaseStateEventProcessor:
    """A BaseStateEventProcessor with real (unmocked) _rehydrate.

    Returns:
        A fresh BaseStateEventProcessor instance.
    """

    def handle_backend_exception(ex: Exception) -> None:
        formatted_exc = "\n".join(traceback.format_exception(ex))
        pytest.fail(f"Event processor raised an unexpected exception:\n{formatted_exc}")

    return BaseStateEventProcessor(
        backend_exception_handler=handle_backend_exception,
        graceful_shutdown_timeout=2,
    )


@pytest.fixture
def emitted_deltas() -> list[tuple[str, Mapping[str, Mapping[str, Any]]]]:
    """List to capture emitted deltas.

    Returns:
        An empty list for collecting deltas.
    """
    return []


@pytest.fixture
def emitted_events() -> list[tuple[str, tuple[Event, ...]]]:
    """List to capture emitted events.

    Returns:
        An empty list for collecting events.
    """
    return []


@pytest_asyncio.fixture
async def real_base_state_processor(
    _real_base_state_processor_obj: BaseStateEventProcessor,
    emitted_deltas: list,
    emitted_events: list,
    clean_registration_context: RegistrationContext,
):
    """A fully wired BaseStateEventProcessor with real _rehydrate.

    Yields the processor (not yet started). The test must use ``async with processor`` to
    control the lifecycle and assert on emitted deltas after stop.

    Args:
        _real_base_state_processor_obj: The unmocked processor instance.
        emitted_deltas: List to capture emitted deltas.
        emitted_events: List to capture emitted events.
        clean_registration_context: Isolated registration context for the test.

    Yields:
        The configured but not-yet-started BaseStateEventProcessor.
    """
    clean_registration_context.register_base_state(OnLoadInternalState)
    state_manager = StateManagerMemory()

    async def emit_delta_impl(  # noqa: RUF029
        token: str, delta: Mapping[str, Mapping[str, Any]]
    ) -> None:
        emitted_deltas.append((token, delta))

    async def emit_event_impl(token: str, *events: Event) -> None:  # noqa: RUF029
        emitted_events.append((token, events))

    root_ctx = EventContext(
        token="",
        state_manager=state_manager,
        enqueue_impl=_real_base_state_processor_obj.enqueue_many,
        emit_delta_impl=emit_delta_impl,
        emit_event_impl=emit_event_impl,
    )
    _real_base_state_processor_obj._root_context = root_ctx

    yield _real_base_state_processor_obj

    await state_manager.close()


async def test_rehydrate_sets_is_hydrated_on_fresh_token(
    app_module_mock,
    real_base_state_processor: BaseStateEventProcessor,
    emitted_deltas: list[tuple[str, Mapping[str, Mapping[str, Any]]]],
    token: str,
):
    """A non-hydrate event against a fresh token triggers _rehydrate, emitting is_hydrated=True.

    When a token has never been seen before (no router_data on the state),
    and the event is not itself the hydrate event, the processor calls
    _rehydrate which runs State.hydrate. With no on_load events defined,
    hydrate sets is_hydrated=True directly.

    Args:
        app_module_mock: The mock app module fixture.
        real_base_state_processor: The unmocked BaseStateEventProcessor.
        emitted_deltas: List to capture emitted deltas.
        token: The client token.
    """

    class MyState(State):
        @event
        def noop(self):
            pass

    OnLoadInternalState._app_ref = None
    app = app_module_mock.app = App()
    assert real_base_state_processor._root_context is not None
    app._state_manager = real_base_state_processor._root_context.state_manager

    async with real_base_state_processor as processor:
        await processor.enqueue(
            token,
            Event.from_event_type(MyState.noop())[0],
        )
        await processor.join(1)

    state_name = State.get_full_name()
    is_hydrated_key = CompileVars.IS_HYDRATED + FIELD_MARKER
    hydrated_deltas = [
        d
        for _, d in emitted_deltas
        if state_name in d and d[state_name].get(is_hydrated_key) is True
    ]
    assert len(hydrated_deltas) >= 1, (
        f"Expected at least one delta with is_hydrated=True, got deltas: {emitted_deltas}"
    )


@pytest_asyncio.fixture
async def processor_with_handler(
    emitted_deltas: list,
    emitted_events: list,
    clean_registration_context: RegistrationContext,
):
    """Build a BaseStateEventProcessor with a configurable exception handler.

    The fixture yields a builder ``(handler) -> processor`` that wires the
    processor up with a fresh memory state manager and emit hooks. The test
    must use ``async with processor:`` to drive the lifecycle.

    Args:
        emitted_deltas: List to capture emitted deltas.
        emitted_events: List to capture emitted events.
        clean_registration_context: Isolated registration context for the test.

    Yields:
        A builder callable.
    """
    clean_registration_context.register_base_state(OnLoadInternalState)
    state_manager = StateManagerMemory()

    async def emit_delta_impl(  # noqa: RUF029
        token: str, delta: Mapping[str, Mapping[str, Any]]
    ) -> None:
        emitted_deltas.append((token, delta))

    async def emit_event_impl(token: str, *events: Event) -> None:  # noqa: RUF029
        emitted_events.append((token, events))

    processors: list[BaseStateEventProcessor] = []

    def build(handler):
        processor = BaseStateEventProcessor(
            backend_exception_handler=handler,
            graceful_shutdown_timeout=2,
        )
        processor._root_context = EventContext(
            token="",
            state_manager=state_manager,
            enqueue_impl=processor.enqueue_many,
            emit_delta_impl=emit_delta_impl,
            emit_event_impl=emit_event_impl,
        )
        processors.append(processor)
        return processor, state_manager

    yield build

    await state_manager.close()


async def test_handler_exception_persists_partial_mutations(
    app_module_mock,
    processor_with_handler,
    token: str,
):
    """Mutations made before the raise persist via the state manager.

    Pre-#6267 reflex caught handler exceptions inside the modify_state block,
    so set_state ran and partial mutations were committed. This regression
    test asserts the same behavior is preserved post-#6267 / post-fix:
    raising a second time must use the incremented count.

    Args:
        app_module_mock: The mock app module fixture.
        processor_with_handler: Builder for a BaseStateEventProcessor.
        token: The client token.
    """

    class CountingState(State):
        count: int = 0

        @event
        def increment_then_raise(self):
            self.count += 1
            msg = f"raised {self.count} times"
            raise RuntimeError(msg)

    caught: list[Exception] = []

    def handler(ex: Exception) -> None:
        caught.append(ex)

    processor, state_manager = processor_with_handler(handler)
    OnLoadInternalState._app_ref = None
    app = app_module_mock.app = App()
    app._state_manager = state_manager

    async with processor:
        await processor.enqueue(
            token, Event.from_event_type(CountingState.increment_then_raise())[0]
        )
        await processor.join(1)
        await processor.enqueue(
            token, Event.from_event_type(CountingState.increment_then_raise())[0]
        )
        await processor.join(1)

    assert len(caught) == 2
    assert str(caught[0]) == "raised 1 times"
    assert str(caught[1]) == "raised 2 times"

    root = await state_manager.get_state(BaseStateToken(ident=token, cls=CountingState))
    counting = await root.get_state(CountingState)
    assert counting.count == 2


async def test_handler_exception_traceback_is_real(
    app_module_mock,
    processor_with_handler,
    token: str,
):
    r"""``traceback.format_exc()`` inside the user handler returns the real handler frame.

    Pre-fix, the user handler ran in a separate task with no active exception
    so ``format_exc()`` returned ``"NoneType: None\n"``.

    Args:
        app_module_mock: The mock app module fixture.
        processor_with_handler: Builder for a BaseStateEventProcessor.
        token: The client token.
    """

    class TracebackState(State):
        @event
        def boom(self):
            msg = "kaboom"
            raise RuntimeError(msg)

    captured: list[str] = []

    def handler(ex: Exception) -> None:
        captured.append(traceback.format_exc())

    processor, state_manager = processor_with_handler(handler)
    OnLoadInternalState._app_ref = None
    app = app_module_mock.app = App()
    app._state_manager = state_manager

    async with processor:
        await processor.enqueue(token, Event.from_event_type(TracebackState.boom())[0])
        await processor.join(1)

    assert len(captured) == 1
    formatted = captured[0]
    assert "NoneType: None" not in formatted
    assert "RuntimeError: kaboom" in formatted
    assert "boom" in formatted


async def test_handler_returned_events_are_chained(
    app_module_mock,
    processor_with_handler,
    token: str,
):
    """EventSpecs returned by the exception handler are routed through chain_updates.

    The handler returns ``ChainState.show_toast()``; that event must run, which
    flips ``ran_recovery`` on the state.

    Args:
        app_module_mock: The mock app module fixture.
        processor_with_handler: Builder for a BaseStateEventProcessor.
        token: The client token.
    """

    class ChainState(State):
        ran_recovery: bool = False

        @event
        def boom(self):
            msg = "boom"
            raise RuntimeError(msg)

        @event
        def show_toast(self):
            self.ran_recovery = True

    def handler(ex: Exception) -> Any:
        return ChainState.show_toast()

    processor, state_manager = processor_with_handler(handler)
    OnLoadInternalState._app_ref = None
    app = app_module_mock.app = App()
    app._state_manager = state_manager

    async with processor:
        await processor.enqueue(token, Event.from_event_type(ChainState.boom())[0])
        await processor.join(2)

    root = await state_manager.get_state(BaseStateToken(ident=token, cls=ChainState))
    chain_state = await root.get_state(ChainState)
    assert chain_state.ran_recovery is True


async def test_handler_none_records_exception_on_future(
    app_module_mock,
    processor_with_handler,
    token: str,
):
    """Without a backend_exception_handler, the future records the exception.

    Args:
        app_module_mock: The mock app module fixture.
        processor_with_handler: Builder for a BaseStateEventProcessor.
        token: The client token.
    """

    class NoHandlerState(State):
        @event
        def boom(self):
            msg = "no handler"
            raise RuntimeError(msg)

    processor, state_manager = processor_with_handler(None)
    OnLoadInternalState._app_ref = None
    app = app_module_mock.app = App()
    app._state_manager = state_manager

    async with processor:
        future = await processor.enqueue(
            token, Event.from_event_type(NoHandlerState.boom())[0]
        )
        await processor.join(1)

    assert future.done()
    with pytest.raises(RuntimeError, match="no handler"):
        future.result()


async def test_handler_itself_raising_does_not_crash_processor(
    app_module_mock,
    processor_with_handler,
    token: str,
):
    """If the user handler raises, the processor logs and continues.

    A subsequent event must still process normally.

    Args:
        app_module_mock: The mock app module fixture.
        processor_with_handler: Builder for a BaseStateEventProcessor.
        token: The client token.
    """

    class FlakyHandlerState(State):
        ran_after_raise: bool = False

        @event
        def boom(self):
            msg = "boom"
            raise RuntimeError(msg)

        @event
        def mark(self):
            self.ran_after_raise = True

    def handler(ex: Exception) -> None:
        msg = "handler also broken"
        raise ValueError(msg)

    processor, state_manager = processor_with_handler(handler)
    OnLoadInternalState._app_ref = None
    app = app_module_mock.app = App()
    app._state_manager = state_manager

    async with processor:
        await processor.enqueue(
            token, Event.from_event_type(FlakyHandlerState.boom())[0]
        )
        await processor.join(1)
        await processor.enqueue(
            token, Event.from_event_type(FlakyHandlerState.mark())[0]
        )
        await processor.join(1)

    root = await state_manager.get_state(
        BaseStateToken(ident=token, cls=FlakyHandlerState)
    )
    flaky = await root.get_state(FlakyHandlerState)
    assert flaky.ran_after_raise is True
