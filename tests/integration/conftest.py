"""Shared conftest for all integration tests."""

import os
import re
from pathlib import Path
from typing import Generator, Type

import pytest

import reflex.constants
from reflex.config import EnvironmentVariables
from reflex.constants.base import Env
from reflex.testing import AppHarness, AppHarnessProd

DISPLAY = None
XVFB_DIMENSIONS = (800, 600)


@pytest.fixture(scope="session", autouse=True)
def xvfb():
    """Create virtual X display.

    This function is a no-op unless GITHUB_ACTIONS is set in the environment.

    Yields:
        the pyvirtualdisplay object that the browser will be open on
    """
    if (
        os.environ.get("GITHUB_ACTIONS")
        and not EnvironmentVariables.APP_HARNESS_HEADLESS.get()
    ):
        from pyvirtualdisplay.smartdisplay import (  # pyright: ignore [reportMissingImports]
            SmartDisplay,
        )

        global DISPLAY
        with SmartDisplay(visible=False, size=XVFB_DIMENSIONS) as DISPLAY:
            yield DISPLAY
        DISPLAY = None
    else:
        yield None


def pytest_exception_interact(node, call, report):
    """Take and upload screenshot when tests fail.

    Args:
        node: The pytest item that failed.
        call: The pytest call describing when/where the test was invoked.
        report: The pytest log report object.
    """
    screenshot_dir = EnvironmentVariables.SCREENSHOT_DIR.get()
    if DISPLAY is None or screenshot_dir is None:
        return

    screenshot_dir = Path(screenshot_dir)
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = re.sub(
        r"(?u)[^-\w.]",
        "_",
        str(node.nodeid).strip().replace(" ", "_").replace(":", "_").replace(".py", ""),
    )

    try:
        DISPLAY.waitgrab().save(
            (Path(screenshot_dir) / safe_filename).with_suffix(".png"),
        )
    except Exception as e:
        print(f"Failed to take screenshot for {node}: {e}")


@pytest.fixture(
    scope="session",
    params=[
        AppHarness,
        AppHarnessProd,
    ],
    ids=[
        reflex.constants.Env.DEV.value,
        reflex.constants.Env.PROD.value,
    ],
)
def app_harness_env(
    request: pytest.FixtureRequest,
) -> Generator[Type[AppHarness], None, None]:
    """Parametrize the AppHarness class to use for the test, either dev or prod.

    Args:
        request: The pytest fixture request object.

    Yields:
        The AppHarness class to use for the test.
    """
    harness: Type[AppHarness] = request.param
    if issubclass(harness, AppHarnessProd):
        EnvironmentVariables.REFLEX_ENV_MODE.set(Env.PROD)
    yield harness
    if isinstance(harness, AppHarnessProd):
        EnvironmentVariables.REFLEX_ENV_MODE.set(None)
