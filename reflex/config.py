"""The Reflex config."""

from __future__ import annotations

import importlib
import os
import sys
import inspect
import functools
import urllib.parse
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Callable

try:
    # TODO The type checking guard can be removed once
    # reflex-hosting-cli tools are compatible with pydantic v2

    if not TYPE_CHECKING:
        import pydantic.v1 as pydantic
    else:
        raise ModuleNotFoundError
except ModuleNotFoundError:
    import pydantic

from reflex_cli.constants.hosting import Hosting

from reflex import constants
from reflex.base import Base
from reflex.utils import console
from reflex.utils.exceptions import (
    default_frontend_exception_handler,
    default_backend_exception_handler,
)
from reflex.event import EventSpec


class DBConfig(Base):
    """Database config."""

    engine: str
    username: Optional[str] = ""
    password: Optional[str] = ""
    host: Optional[str] = ""
    port: Optional[int] = None
    database: str

    @classmethod
    def postgresql(
        cls,
        database: str,
        username: str,
        password: str | None = None,
        host: str | None = None,
        port: int | None = 5432,
    ) -> DBConfig:
        """Create an instance with postgresql engine.

        Args:
            database: Database name.
            username: Database username.
            password: Database password.
            host: Database host.
            port: Database port.

        Returns:
            DBConfig instance.
        """
        return cls(
            engine="postgresql",
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
        )

    @classmethod
    def postgresql_psycopg2(
        cls,
        database: str,
        username: str,
        password: str | None = None,
        host: str | None = None,
        port: int | None = 5432,
    ) -> DBConfig:
        """Create an instance with postgresql+psycopg2 engine.

        Args:
            database: Database name.
            username: Database username.
            password: Database password.
            host: Database host.
            port: Database port.

        Returns:
            DBConfig instance.
        """
        return cls(
            engine="postgresql+psycopg2",
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
        )

    @classmethod
    def sqlite(
        cls,
        database: str,
    ) -> DBConfig:
        """Create an instance with sqlite engine.

        Args:
            database: Database name.

        Returns:
            DBConfig instance.
        """
        return cls(
            engine="sqlite",
            database=database,
        )

    def get_url(self) -> str:
        """Get database URL.

        Returns:
            The database URL.
        """
        host = (
            f"{self.host}:{self.port}" if self.host and self.port else self.host or ""
        )
        username = urllib.parse.quote_plus(self.username) if self.username else ""
        password = urllib.parse.quote_plus(self.password) if self.password else ""

        if username:
            path = f"{username}:{password}@{host}" if password else f"{username}@{host}"
        else:
            path = f"{host}"

        return f"{self.engine}://{path}/{self.database}"


class Config(Base):
    """A Reflex config."""

    class Config:
        """Pydantic config for the config."""

        validate_assignment = True

    # The name of the app.
    app_name: str

    # The log level to use.
    loglevel: constants.LogLevel = constants.LogLevel.INFO

    # The port to run the frontend on.
    frontend_port: int = 3000

    # The path to run the frontend on.
    frontend_path: str = ""

    # The port to run the backend on.
    backend_port: int = 8000

    # The backend url the frontend will connect to.
    api_url: str = f"http://localhost:{backend_port}"

    # The url the frontend will be hosted on.
    deploy_url: Optional[str] = f"http://localhost:{frontend_port}"

    # The url the backend will be hosted on.
    backend_host: str = "0.0.0.0"

    # The database url.
    db_url: Optional[str] = "sqlite:///reflex.db"

    # The redis url.
    redis_url: Optional[str] = None

    # Telemetry opt-in.
    telemetry_enabled: bool = True

    # The bun path
    bun_path: str = constants.Bun.DEFAULT_PATH

    # List of origins that are allowed to connect to the backend API.
    cors_allowed_origins: List[str] = ["*"]

    # Tailwind config.
    tailwind: Optional[Dict[str, Any]] = {}

    # Timeout when launching the gunicorn server. TODO(rename this to backend_timeout?)
    timeout: int = 120

    # Whether to enable or disable nextJS gzip compression.
    next_compression: bool = True

    # The event namespace for ws connection
    event_namespace: Optional[str] = None

    # Additional frontend packages to install.
    frontend_packages: List[str] = []

    # The hosting service backend URL.
    cp_backend_url: str = Hosting.CP_BACKEND_URL
    # The hosting service frontend URL.
    cp_web_url: str = Hosting.CP_WEB_URL

    # The worker class used in production mode
    gunicorn_worker_class: str = "uvicorn.workers.UvicornH11Worker"

    # Attributes that were explicitly set by the user.
    _non_default_attributes: Set[str] = pydantic.PrivateAttr(set())

    # Frontend Error Handler Function
    frontend_exception_handler: Optional[
        Callable[[str, str], None]
    ] = default_frontend_exception_handler

    # Backend Error Handler Function
    backend_exception_handler: Optional[
        Callable[[str, str], EventSpec | list[EventSpec] | None]
    ] = default_backend_exception_handler

    def __init__(self, *args, **kwargs):
        """Initialize the config values.

        Args:
            *args: The args to pass to the Pydantic init method.
            **kwargs: The kwargs to pass to the Pydantic init method.
        """
        super().__init__(*args, **kwargs)

        # Check for deprecated values.
        self.check_deprecated_values(**kwargs)

        # Update the config from environment variables.
        env_kwargs = self.update_from_env()
        for key, env_value in env_kwargs.items():
            setattr(self, key, env_value)

        # Update default URLs if ports were set
        kwargs.update(env_kwargs)
        self._non_default_attributes.update(kwargs)
        self._replace_defaults(**kwargs)

        # Check the exception handlers
        self._validate_exception_handlers()

    @property
    def module(self) -> str:
        """Get the module name of the app.

        Returns:
            The module name.
        """
        return ".".join([self.app_name, self.app_name])

    @staticmethod
    def check_deprecated_values(**kwargs):
        """Check for deprecated config values.

        Args:
            **kwargs: The kwargs passed to the config.

        Raises:
            ValueError: If a deprecated config value is found.
        """
        if "db_config" in kwargs:
            raise ValueError("db_config is deprecated - use db_url instead")
        if "admin_dash" in kwargs:
            raise ValueError(
                "admin_dash is deprecated in the config - pass it as a param to rx.App instead"
            )
        if "env_path" in kwargs:
            raise ValueError(
                "env_path is deprecated - use environment variables instead"
            )

    def update_from_env(self) -> dict[str, Any]:
        """Update the config from environment variables.

        Returns:
            The updated config values.

        Raises:
            ValueError: If an environment variable is set to an invalid type.
        """
        updated_values = {}
        # Iterate over the fields.
        for key, field in self.__fields__.items():
            # The env var name is the key in uppercase.
            env_var = os.environ.get(key.upper())

            # If the env var is set, override the config value.
            if env_var is not None:
                if key.upper() != "DB_URL":
                    console.info(
                        f"Overriding config value {key} with env var {key.upper()}={env_var}"
                    )

                # Convert the env var to the expected type.
                try:
                    if issubclass(field.type_, bool):
                        # special handling for bool values
                        env_var = env_var.lower() in ["true", "1", "yes"]
                    else:
                        env_var = field.type_(env_var)
                except ValueError:
                    console.error(
                        f"Could not convert {key.upper()}={env_var} to type {field.type_}"
                    )
                    raise

                # Set the value.
                updated_values[key] = env_var

        return updated_values

    def get_event_namespace(self) -> str:
        """Get the websocket event namespace.

        Returns:
            The namespace for websocket.
        """
        if self.event_namespace:
            console.deprecate(
                feature_name="Passing event_namespace in the config",
                reason="",
                deprecation_version="0.3.5",
                removal_version="0.5.0",
            )
            return f'/{self.event_namespace.strip("/")}'

        event_url = constants.Endpoint.EVENT.get_url()
        return urllib.parse.urlsplit(event_url).path

    def _replace_defaults(self, **kwargs):
        """Replace formatted defaults when the caller provides updates.

        Args:
            **kwargs: The kwargs passed to the config or from the env.
        """
        if "api_url" not in self._non_default_attributes and "backend_port" in kwargs:
            self.api_url = f"http://localhost:{kwargs['backend_port']}"

        if (
            "deploy_url" not in self._non_default_attributes
            and "frontend_port" in kwargs
        ):
            self.deploy_url = f"http://localhost:{kwargs['frontend_port']}"

        # If running in Github Codespaces, override API_URL
        codespace_name = os.getenv("CODESPACE_NAME")
        if "api_url" not in self._non_default_attributes and codespace_name:
            GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN = os.getenv(
                "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
            )
            if codespace_name:
                self.api_url = (
                    f"https://{codespace_name}-{kwargs.get('backend_port', self.backend_port)}"
                    f".{GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
                )

    def _set_persistent(self, **kwargs):
        """Set values in this config and in the environment so they persist into subprocess.

        Args:
            **kwargs: The kwargs passed to the config.
        """
        for key, value in kwargs.items():
            if value is not None:
                os.environ[key.upper()] = str(value)
            setattr(self, key, value)
        self._non_default_attributes.update(kwargs)
        self._replace_defaults(**kwargs)

    def _validate_exception_handlers(self):
        """Validate the custom event exception handlers for front- and backend.

        Raises:
            ValueError: If the custom exception handlers are invalid.

        """
        FRONTEND_ARG_SPEC = {
            "message": str,
            "stack": str,
        }

        BACKEND_ARG_SPEC = {
            "message": str,
            "stack": str,
        }

        for handler_domain, handler_fn, handler_spec in zip(
            ["frontend", "backend"],
            [self.frontend_exception_handler, self.backend_exception_handler],
            [
                FRONTEND_ARG_SPEC,
                BACKEND_ARG_SPEC,
            ],
        ):
            if hasattr(handler_fn, "__name__"):
                _fn_name = handler_fn.__name__
            else:
                _fn_name = handler_fn.__class__.__name__

            if isinstance(handler_fn, functools.partial):
                raise ValueError(
                    f"Provided custom {handler_domain} exception handler `{_fn_name}` is a partial function. Please provide a named function instead."
                )

            if not callable(handler_fn):
                raise ValueError(
                    f"Provided custom {handler_domain} exception handler `{_fn_name}` is not a function."
                )

            # Allow named functions only as lambda functions cannot be introspected
            if _fn_name == "<lambda>":
                raise ValueError(
                    f"Provided custom {handler_domain} exception handler `{_fn_name}` is a lambda function. Please use a named function instead."
                )

            # Check if the function has the necessary annotations and types
            arg_annotations = inspect.get_annotations(handler_fn)

            for required_arg in handler_spec:

                if required_arg not in arg_annotations:
                    raise ValueError(
                        f"Provided custom {handler_domain} exception handler `{_fn_name}` does not take the required argument `{required_arg}`"
                    )

                if arg_annotations[required_arg] != handler_spec[required_arg]:
                    raise ValueError(
                        f"Provided custom {handler_domain} exception handler `{_fn_name}` has the wrong type for {required_arg} argument."
                        f"Expected `{handler_spec[required_arg]}` but got `{arg_annotations[required_arg]}`"
                    )

            # Check if the return type is valid for backend exception handler
            if handler_domain == "backend":
                sig = inspect.signature(self.backend_exception_handler)
                return_type = sig.return_annotation

                valid = bool(
                    return_type == EventSpec
                    or return_type == Optional[EventSpec]
                    or return_type == list[EventSpec]
                    or return_type == inspect.Signature.empty
                )

                if not valid:
                    raise ValueError(
                        f"Provided custom {handler_domain} exception handler `{_fn_name}` has the wrong return type."
                        f"Expected `EventSpec | list[EventSpec] | None` but got `{return_type}`"
                    )


def get_config(reload: bool = False) -> Config:
    """Get the app config.

    Args:
        reload: Re-import the rxconfig module from disk

    Returns:
        The app config.
    """
    sys.path.insert(0, os.getcwd())
    try:
        rxconfig = __import__(constants.Config.MODULE)
        if reload:
            importlib.reload(rxconfig)
        return rxconfig.config

    except ImportError:
        return Config(app_name="")  # type: ignore
