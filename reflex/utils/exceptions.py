"""Custom Exceptions and Exception Handlers."""

import reflex.utils.console as console
from reflex.event import EventSpec, window_alert


class InvalidStylePropError(TypeError):
    """Custom Type Error when style props have invalid values."""

    pass


class ImmutableStateError(AttributeError):
    """Raised when a background task attempts to modify state outside of context."""


class LockExpiredError(Exception):
    """Raised when the state lock expires while an event is being processed."""


class MatchTypeError(TypeError):
    """Raised when the return types of match cases are different."""

    pass


def default_frontend_exception_handler(message: str, stack: str) -> None:
    """Default frontend exception handler function.

    Args:
        message: The error message.
        stack: The stack trace.

    """
    console.error(
        f"[Reflex Frontend Exception]\n - Message: {message}\n - Stack: {stack}\n"
    )


def default_backend_exception_handler(message: str, stack: str) -> EventSpec:
    """Default backend exception handler function.

    Args:
        message: The error message.
        stack: The stack trace.

    Returns:
        EventSpec: The window alert event.
    """
    console.error(
        f"[Reflex Backend Exception]\n - Message: {message}\n - Stack: {stack}\n"
    )

    return window_alert("An error occurred. See logs for details.")
