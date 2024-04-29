import multiprocessing
import os
from typing import Any, Dict

import pytest
import functools
import reflex as rx
import reflex.config
from reflex.constants import Endpoint
from contextlib import nullcontext as does_not_raise


def test_requires_app_name():
    """Test that a config requires an app_name."""
    with pytest.raises(ValueError):
        rx.Config()  # type: ignore


def test_set_app_name(base_config_values):
    """Test that the app name is set to the value passed in.

    Args:
        base_config_values: Config values.
    """
    config = rx.Config(**base_config_values)
    assert config.app_name == base_config_values["app_name"]


@pytest.mark.parametrize(
    "param",
    [
        "db_config",
        "admin_dash",
        "env_path",
    ],
)
def test_deprecated_params(base_config_values: Dict[str, Any], param):
    """Test that deprecated params are removed from the config.

    Args:
        base_config_values: Config values.
        param: The deprecated param.
    """
    with pytest.raises(ValueError):
        rx.Config(**base_config_values, **{param: "test"})  # type: ignore


@pytest.mark.parametrize(
    "env_var, value",
    [
        ("APP_NAME", "my_test_app"),
        ("FRONTEND_PORT", 3001),
        ("FRONTEND_PATH", "/test"),
        ("BACKEND_PORT", 8001),
        ("API_URL", "https://mybackend.com:8000"),
        ("DEPLOY_URL", "https://myfrontend.com"),
        ("BACKEND_HOST", "127.0.0.1"),
        ("DB_URL", "postgresql://user:pass@localhost:5432/db"),
        ("REDIS_URL", "redis://localhost:6379"),
        ("TIMEOUT", 600),
        ("TELEMETRY_ENABLED", False),
        ("TELEMETRY_ENABLED", True),
    ],
)
def test_update_from_env(base_config_values, monkeypatch, env_var, value):
    """Test that environment variables override config values.

    Args:
        base_config_values: Config values.
        monkeypatch: The pytest monkeypatch object.
        env_var: The environment variable name.
        value: The environment variable value.
    """
    monkeypatch.setenv(env_var, str(value))
    assert os.environ.get(env_var) == str(value)
    config = rx.Config(**base_config_values)
    assert getattr(config, env_var.lower()) == value


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        (
            {"app_name": "test_app", "api_url": "http://example.com"},
            f"{Endpoint.EVENT}",
        ),
        (
            {"app_name": "test_app", "api_url": "http://example.com/api"},
            f"/api{Endpoint.EVENT}",
        ),
        ({"app_name": "test_app", "event_namespace": "/event"}, f"/event"),
        ({"app_name": "test_app", "event_namespace": "event"}, f"/event"),
        ({"app_name": "test_app", "event_namespace": "event/"}, f"/event"),
        ({"app_name": "test_app", "event_namespace": "/_event"}, f"{Endpoint.EVENT}"),
        ({"app_name": "test_app", "event_namespace": "_event"}, f"{Endpoint.EVENT}"),
        ({"app_name": "test_app", "event_namespace": "_event/"}, f"{Endpoint.EVENT}"),
    ],
)
def test_event_namespace(mocker, kwargs, expected):
    """Test the event namespace.

    Args:
        mocker: The pytest mock object.
        kwargs: The Config kwargs.
        expected: Expected namespace
    """
    conf = rx.Config(**kwargs)
    mocker.patch("reflex.config.get_config", return_value=conf)

    config = reflex.config.get_config()
    assert conf == config
    assert config.get_event_namespace() == expected


DEFAULT_CONFIG = rx.Config(app_name="a")


@pytest.mark.parametrize(
    ("config_kwargs", "env_vars", "set_persistent_vars", "exp_config_values"),
    [
        (
            {},
            {},
            {},
            {
                "api_url": DEFAULT_CONFIG.api_url,
                "backend_port": DEFAULT_CONFIG.backend_port,
                "deploy_url": DEFAULT_CONFIG.deploy_url,
                "frontend_port": DEFAULT_CONFIG.frontend_port,
            },
        ),
        # Ports set in config kwargs
        (
            {"backend_port": 8001, "frontend_port": 3001},
            {},
            {},
            {
                "api_url": "http://localhost:8001",
                "backend_port": 8001,
                "deploy_url": "http://localhost:3001",
                "frontend_port": 3001,
            },
        ),
        # Ports set in environment take precedence
        (
            {"backend_port": 8001, "frontend_port": 3001},
            {"BACKEND_PORT": 8002},
            {},
            {
                "api_url": "http://localhost:8002",
                "backend_port": 8002,
                "deploy_url": "http://localhost:3001",
                "frontend_port": 3001,
            },
        ),
        # Ports set on the command line take precedence
        (
            {"backend_port": 8001, "frontend_port": 3001},
            {"BACKEND_PORT": 8002},
            {"frontend_port": "3005"},
            {
                "api_url": "http://localhost:8002",
                "backend_port": 8002,
                "deploy_url": "http://localhost:3005",
                "frontend_port": 3005,
            },
        ),
        # api_url / deploy_url already set should not be overridden
        (
            {"api_url": "http://foo.bar:8900", "deploy_url": "http://foo.bar:3001"},
            {"BACKEND_PORT": 8002},
            {"frontend_port": "3005"},
            {
                "api_url": "http://foo.bar:8900",
                "backend_port": 8002,
                "deploy_url": "http://foo.bar:3001",
                "frontend_port": 3005,
            },
        ),
    ],
)
def test_replace_defaults(
    monkeypatch,
    config_kwargs,
    env_vars,
    set_persistent_vars,
    exp_config_values,
):
    """Test that the config replaces defaults with values from the environment.

    Args:
        monkeypatch: The pytest monkeypatch object.
        config_kwargs: The config kwargs.
        env_vars: The environment variables.
        set_persistent_vars: The values passed to config._set_persistent variables.
        exp_config_values: The expected config values.
    """
    mock_os_env = os.environ.copy()
    monkeypatch.setattr(reflex.config.os, "environ", mock_os_env)  # type: ignore
    mock_os_env.update({k: str(v) for k, v in env_vars.items()})
    c = rx.Config(app_name="a", **config_kwargs)
    c._set_persistent(**set_persistent_vars)
    for key, value in exp_config_values.items():
        assert getattr(c, key) == value


def reflex_dir_constant():
    return rx.constants.Reflex.DIR


def test_reflex_dir_env_var(monkeypatch, tmp_path):
    """Test that the REFLEX_DIR environment variable is used to set the Reflex.DIR constant.

    Args:
        monkeypatch: The pytest monkeypatch object.
        tmp_path: The pytest tmp_path object.
    """
    monkeypatch.setenv("REFLEX_DIR", str(tmp_path))

    mp_ctx = multiprocessing.get_context(method="spawn")
    with mp_ctx.Pool(processes=1) as pool:
        assert pool.apply(reflex_dir_constant) == str(tmp_path)


def valid_custom_handler(message: str, stack: str, logger: str = "test"):
    print("Custom Backend Exception")
    print(stack)


def custom_exception_handler_with_wrong_argspec(
    message: int, stack: str  # Should be str
):
    print("Custom Backend Exception")
    print(stack)


class SomeHandler:
    def handle(self, message: str, stack: str):
        print("Custom Backend Exception")
        print(stack)


custom_exception_handlers = {
    "lambda": lambda message, stack: print("Custom Exception Handler", message, stack),
    "wrong_argspec": custom_exception_handler_with_wrong_argspec,
    "valid": valid_custom_handler,
    "partial": functools.partial(valid_custom_handler, logger="test"),
    "method": SomeHandler().handle,
}


@pytest.mark.parametrize(
    "handler_fn, expected",
    [
        pytest.param(
            custom_exception_handlers["partial"],
            pytest.raises(ValueError),
            id="partial",
        ),
        pytest.param(
            custom_exception_handlers["lambda"],
            pytest.raises(ValueError),
            id="lambda",
        ),
        pytest.param(
            custom_exception_handlers["wrong_argspec"],
            pytest.raises(ValueError),
            id="wrong_argspec",
        ),
        pytest.param(
            custom_exception_handlers["valid"],
            does_not_raise(),
            id="valid_handler",
        ),
        pytest.param(
            custom_exception_handlers["method"],
            does_not_raise(),
            id="valid_class_method",
        ),
    ],
)
def test_frontend_exception_handler_validation(handler_fn, expected):
    """Test that the custom frontend exception handler is properly validated.

    Args:
        handler_fn: The handler function.
        expected: The expected result.

    """
    with expected:
        rx.Config(app_name="a", frontend_exception_handler=handler_fn)


@pytest.mark.parametrize(
    "handler_fn, expected",
    [
        pytest.param(
            custom_exception_handlers["partial"],
            pytest.raises(ValueError),
            id="partial",
        ),
        pytest.param(
            custom_exception_handlers["lambda"],
            pytest.raises(ValueError),
            id="lambda",
        ),
        pytest.param(
            custom_exception_handlers["wrong_argspec"],
            pytest.raises(ValueError),
            id="wrong_argspec",
        ),
        pytest.param(
            custom_exception_handlers["valid"],
            does_not_raise(),
            id="valid_handler",
        ),
        pytest.param(
            custom_exception_handlers["method"],
            does_not_raise(),
            id="valid_class_method",
        ),
    ],
)
def test_backend_exception_handler_validation(handler_fn, expected):
    """Test that the custom backend exception handler is properly validated.

    Args:
        handler_fn: The handler function.
        expected: The expected result.

    """
    with expected:
        rx.Config(app_name="a", backend_exception_handler=handler_fn)
