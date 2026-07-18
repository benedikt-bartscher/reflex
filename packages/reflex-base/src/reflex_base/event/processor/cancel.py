"""Cross-worker coordination for ``cancel_previous_task`` background events."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import Protocol


class CancelPreviousBroker(Protocol):
    """Coordinates ``cancel_previous_task`` across multiple backend workers.

    A background handler declared with ``cancel_previous_task=True`` should have
    at most one in-flight run per ``(client token, event name)``. Within a
    single worker this is enforced in-process by the ``EventProcessor``. When
    several workers share state (e.g. the redis state manager), a task started
    on one worker cannot be cancelled from another because ``Task.cancel()``
    only works in the owning event loop. The broker bridges that gap by
    propagating a globally-ordered "latest run" value so the worker that owns a
    now-superseded task can cancel it itself.
    """

    async def claim(self, token: str, event_name: str, txid: str) -> None:
        """Record ``txid`` as the latest run for ``(token, event_name)``.

        Implementations must establish a single, globally-ordered "latest"
        value so that concurrent claims from different workers converge on
        exactly one winner (the last claim to be applied).

        Args:
            token: The client token the event belongs to.
            event_name: The fully-qualified event handler name.
            txid: The transaction id of the newly dispatched run.
        """
        ...

    def subscribe(
        self, on_supersede: Callable[[str, str, str], None]
    ) -> AbstractAsyncContextManager[None]:
        """Listen for supersede signals for the lifetime of the returned context.

        Args:
            on_supersede: Called as ``on_supersede(token, event_name, latest_txid)``
                whenever a key's latest run changes, where ``latest_txid`` is the
                current winning transaction id. The callback runs on the caller's
                event loop.

        Returns:
            An async context manager that runs the listener while active.
        """
        ...


__all__ = ["CancelPreviousBroker"]
