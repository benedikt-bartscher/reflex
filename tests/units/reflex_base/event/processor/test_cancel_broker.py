"""Cross-worker ``cancel_previous_task`` coordination via the redis broker."""

import asyncio

import pytest
from reflex_base.event.processor.event_processor import EventProcessor
from reflex_base.registry import RegistrationContext

from reflex.event import Event, EventHandler
from reflex.istate.manager.redis import StateManagerRedis
from tests.units.mock_redis import mock_redis

_started: list[str] = []
_cancelled: list[str] = []
_completed: list[str] = []
_park: list[asyncio.Event] = []


async def _cancel_prev_handler(run_id: str = ""):
    """A background cancel-previous handler that parks until released.

    Args:
        run_id: An identifier used to track this run across the test.
    """
    _started.append(run_id)
    try:
        await _park[0].wait()
    except asyncio.CancelledError:
        _cancelled.append(run_id)
        raise
    _completed.append(run_id)


_cancel_prev_handler._reflex_background_task = True  # type: ignore[attr-defined]
_cancel_prev_handler._reflex_cancel_previous_task = True  # type: ignore[attr-defined]
cancel_prev_event = EventHandler(fn=_cancel_prev_handler)


@pytest.fixture
def registered_handler(forked_registration_context: RegistrationContext):
    """Register the cancel-previous handler and reset the run logs.

    Args:
        forked_registration_context: Isolated registration context for the test.
    """
    _started.clear()
    _cancelled.clear()
    _completed.clear()
    _park.clear()
    _park.append(asyncio.Event())
    RegistrationContext.register_event_handler(cancel_prev_event)


@pytest.mark.asyncio
@pytest.mark.usefixtures("registered_handler")
async def test_cancel_previous_across_workers(token: str):
    """A run started on one worker cancels a prior run owned by another worker.

    Two independent ``EventProcessor`` instances share a single redis state
    manager, standing in for two backend workers behind one redis. A
    cancel-previous background run is started on worker A, then a newer run for
    the same ``(token, event)`` is started on worker B. Worker A must cancel its
    now-superseded run even though the newer run lives in a different processor.

    Args:
        token: A unique client token.
    """
    redis = mock_redis()
    manager = StateManagerRedis(redis=redis)
    worker_a = EventProcessor(graceful_shutdown_timeout=1).configure(
        state_manager=manager
    )
    worker_b = EventProcessor(graceful_shutdown_timeout=1).configure(
        state_manager=manager
    )
    event_name = Event.from_event_type(cancel_prev_event("1"))[0].name

    try:
        async with worker_a, worker_b:
            # Run 1 starts on worker A and parks.
            await worker_a.enqueue(
                token, Event.from_event_type(cancel_prev_event("1"))[0]
            )
            await asyncio.sleep(0.3)
            assert _started == ["1"]
            assert (token, event_name) in worker_a._cancel_keys

            # Run 2 starts on worker B and supersedes run 1 on worker A.
            await worker_b.enqueue(
                token, Event.from_event_type(cancel_prev_event("2"))[0]
            )
            await asyncio.sleep(0.3)
            assert _started == ["1", "2"]
            assert _cancelled == ["1"]

            # Let the surviving run finish.
            _park[0].set()
            await asyncio.sleep(0.3)
            assert _completed == ["2"]
    finally:
        await manager.close()
