"""Test rx.State performance."""

from typing import Generator

import time
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from reflex.testing import DEFAULT_TIMEOUT, AppHarness, WebDriver


def StatePerformance():
    """Test that rx.State performance is acceptable."""
    import asyncio

    import reflex as rx

    class State(rx.State):
        counter: int = 0

        @rx.var(cache=True)
        def duplicated_counter(self) -> int:
            return self.counter * 2

        @rx.event(background=True)
        async def increment_background(self):
            for _ in range(1000):
                yield State.increment()
                # TODO: lowering this with redis -> test stuck. locking issues?
                await asyncio.sleep(0.01)

        @rx.event
        def increment(self):
            self.counter += 1

        @rx.event
        def reset_counter(self):
            self.counter = 0

    def index() -> rx.Component:
        return rx.vstack(
            rx.input(
                id="token", value=State.router.session.client_token, is_read_only=True
            ),
            rx.button("Increment", on_click=State.increment, id="increment"),
            rx.button(
                "Increment Background",
                on_click=State.increment_background,
                id="increment_background",
            ),
            rx.button(
                "Reset Counter", on_click=State.reset_counter, id="reset_counter"
            ),
            rx.heading(State.counter, id="counter"),
            rx.heading(State.duplicated_counter, id="duplicated_counter"),
        )

    app = rx.App(state=rx.State)
    app.add_page(index)


@pytest.fixture(scope="module")
def state_performance(
    tmp_path_factory,
) -> Generator[AppHarness, None, None]:
    """Start StatePerformance app at tmp_path via AppHarness.

    Args:
        tmp_path_factory: pytest tmp_path_factory fixture

    Yields:
        running AppHarness instance
    """
    with AppHarness.create(
        root=tmp_path_factory.mktemp("state_performance"),
        app_source=StatePerformance,
    ) as harness:
        yield harness


@pytest.fixture
def driver(state_performance: AppHarness) -> Generator[WebDriver, None, None]:
    """Get an instance of the browser open to the state_performance app.

    Args:
        state_performance: harness for StatePerformance app

    Yields:
        WebDriver instance.
    """
    assert state_performance.app_instance is not None, "app is not running"
    driver = state_performance.frontend()
    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture()
def token(state_performance: AppHarness, driver: WebDriver) -> str:
    """Get a function that returns the active token.

    Args:
        state_performance: harness for StatePerformance app.
        driver: WebDriver instance.

    Returns:
        The token for the connected client
    """
    assert state_performance.app_instance is not None
    token_input = driver.find_element(By.ID, "token")
    assert token_input

    # wait for the backend connection to send the token
    token = state_performance.poll_for_value(token_input, timeout=DEFAULT_TIMEOUT * 2)
    assert token is not None

    return token


@pytest.mark.benchmark(
    group="Compile time of varying page numbers",
    timer=time.perf_counter,
    disable_gc=True,
    warmup=False,
)
def test_state_performance_background(
    state_performance: AppHarness,
    driver: WebDriver,
    token: str,
    benchmark,
):
    """Test that background tasks work as expected.

    Args:
        state_performance: harness for StatePerformance app.
        driver: WebDriver instance.
        token: The token for the connected client.
        benchmark: pytest benchmark fixture.
    """
    assert state_performance.app_instance is not None

    counter = driver.find_element(By.ID, "counter")
    reset_counter = driver.find_element(By.ID, "reset_counter")
    assert counter.text == "0"
    until = WebDriverWait(driver, 60).until

    start_increment_background = driver.find_element(By.ID, "increment_background")

    def increment_background():
        start_increment_background.click()
        # wait for the background task to finish
        assert until(
            lambda driver: driver.find_element(By.ID, "counter").text == "1000"
        )
        reset_counter.click()

    benchmark(increment_background)
