"""Integration tests for event exception handlers."""
from __future__ import annotations

from typing import Generator
from unittest.mock import AsyncMock

import pytest

import time

from reflex.app import process
from reflex.event import Event
from reflex.state import StateManagerRedis

from reflex.testing import AppHarness
from reflex.config import get_config

from typing import Generator

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def TestApp():
    """A test app for event exception handler integration."""

    import reflex as rx

    def frontend_exception_handler(message: str, stack: str):
        print(f"[Fasfadgasdg] {message} {stack}")

    class TestAppConfig(rx.Config):
        """Config for the TestApp app."""

    class TestAppState(rx.State):
        """State for the TestApp app."""

        value: int

        def go(self, c: int):
            """Increment the value c times and update each time.

            Args:
                c: The number of times to increment.

            Yields:
                After each increment.
            """
            for _ in range(c):
                self.value += 1
                yield

    app = rx.App(state=rx.State)

    @app.add_page
    def index():
        return rx.vstack(
            rx.button(
                "induce_frontend_error",
                on_click=rx.call_script("induce_frontend_error()"),
                id="induce-frontend-error-btn",
            ),
        )


@pytest.fixture(scope="module")
def test_app(tmp_path_factory) -> Generator[AppHarness, None, None]:
    """Start TestApp app at tmp_path via AppHarness.

    Args:
        tmp_path_factory: pytest tmp_path_factory fixture

    Yields:
        running AppHarness instance
    """
    with AppHarness.create(
        root=tmp_path_factory.mktemp("test_app"),
        app_source=TestApp,  # type: ignore
    ) as harness:
        yield harness


@pytest.fixture
def driver(test_app: AppHarness) -> Generator[WebDriver, None, None]:
    """Get an instance of the browser open to the test_app app.

    Args:
        test_app: harness for TestApp app

    Yields:
        WebDriver instance.
    """
    assert test_app.app_instance is not None, "app is not running"
    driver = test_app.frontend()
    try:
        yield driver
    finally:
        driver.quit()


def test_frontend_exception_handler_during_runtime(
    driver: WebDriver,
    capsys,
):
    """Test calling frontend exception handler during runtime.

    We send an event containing a call to a non-existent function in the frontend.
    This should trigger the default frontend exception handler.

    Args:
        driver: WebDriver instance.
        capsys: pytest fixture for capturing stdout and stderr.
    """
    reset_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "induce-frontend-error-btn"))
    )

    # 1. Test the default frontend exception handler

    reset_button.click()

    # Wait for the error to be logged
    time.sleep(2)

    captured_default_handler_output = capsys.readouterr()
    assert (
        "[Reflex Frontend Exception]" in captured_default_handler_output.out
        and "induce_frontend_error" in captured_default_handler_output.out
        and "ReferenceError" in captured_default_handler_output.out
    )

    # 2. Test the custom frontend exception handler

    def custom_frontend_exception_handler(message: str, stack: str) -> None:
        print(f"[Custom Frontend Exception] {message} {stack}")

    # Set the custom frontend exception handler
    config = get_config()
    config.frontend_exception_handler = custom_frontend_exception_handler

    reset_button.click()

    # Wait for the error to be logged
    time.sleep(2)

    captured_custom_handler_output = capsys.readouterr()
    assert (
        "[Custom Frontend Exception]" in captured_custom_handler_output.out
        and "induce_frontend_error" in captured_custom_handler_output.out
        and "ReferenceError" in captured_custom_handler_output.out
    )


@pytest.mark.asyncio
async def test_backend_exception_handler_during_runtime(mocker, capsys, test_app):
    """Test calling backend exception handler during runtime.

    Args:
        mocker: mocker object.
        capsys: capsys fixture.
        test_app: harness for CallScript app.
        driver: WebDriver instance.

    """
    token = "mock_token"

    router_data = {
        "pathname": "/",
        "query": {},
        "token": token,
        "sid": "mock_sid",
        "headers": {},
        "ip": "127.0.0.1",
    }

    app = test_app.app_instance
    mocker.patch.object(app, "postprocess", AsyncMock())

    payload = {"c": "5"}  # should be an int

    # 1. Test the default backend exception handler

    event = Event(
        token=token, name="test_app_state.go", payload=payload, router_data=router_data
    )

    async for _update in process(app, event, "mock_sid", {}, "127.0.0.1"):
        pass

    captured_default_handler_output = capsys.readouterr()
    assert (
        "[Reflex Backend Exception]" in captured_default_handler_output.out
        and "'str' object cannot be interpreted as an integer"
        in captured_default_handler_output.out
    )

    # 2. Test the custom backend exception handler

    def custom_backend_exception_handler(message: str, stack: str) -> None:
        print(f"[Custom Backend Exception] {message} {stack}")

    config = get_config()
    config.backend_exception_handler = custom_backend_exception_handler

    event = Event(
        token=token, name="test_app_state.go", payload=payload, router_data=router_data
    )

    async for _update in process(app, event, "mock_sid", {}, "127.0.0.1"):
        pass

    captured_custom_handler_output = capsys.readouterr()
    assert (
        "[Custom Backend Exception]" in captured_custom_handler_output.out
        and "'str' object cannot be interpreted as an integer"
        in captured_custom_handler_output.out
    )

    if isinstance(app.state_manager, StateManagerRedis):
        await app.state_manager.close()
