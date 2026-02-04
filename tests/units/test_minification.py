"""Unit tests for state and event handler minification via minify.json."""

from __future__ import annotations

import json

import pytest

from reflex.environment import MinifyMode, environment
from reflex.minify import (
    MINIFY_JSON,
    SCHEMA_VERSION,
    MinifyConfig,
    _get_frontend_var_names,
    clear_config_cache,
    generate_minify_config,
    get_event_id,
    get_state_full_path,
    get_state_id,
    get_var_id,
    int_to_minified_name,
    is_event_minify_enabled,
    is_minify_enabled,
    is_state_minify_enabled,
    is_var_minify_enabled,
    minified_name_to_int,
    save_minify_config,
    sync_minify_config,
    validate_minify_config,
)
from reflex.state import BaseState, State


class TestIntToMinifiedName:
    """Tests for int_to_minified_name function."""

    def test_zero(self):
        """Test that 0 maps to 'a'."""
        assert int_to_minified_name(0) == "a"

    def test_single_char(self):
        """Test single character mappings."""
        assert int_to_minified_name(1) == "b"
        assert int_to_minified_name(25) == "z"
        assert int_to_minified_name(26) == "A"
        assert int_to_minified_name(51) == "Z"
        assert int_to_minified_name(52) == "$"
        assert int_to_minified_name(53) == "_"

    def test_two_chars(self):
        """Test two character mappings (base 54)."""
        # 54 = 1*54 + 0 -> 'ba'
        assert int_to_minified_name(54) == "ba"
        # 55 = 1*54 + 1 -> 'bb'
        assert int_to_minified_name(55) == "bb"

    def test_unique_names(self):
        """Test that a large range of IDs produce unique names."""
        names = set()
        for i in range(10000):
            name = int_to_minified_name(i)
            assert name not in names, f"Duplicate name {name} for id {i}"
            names.add(name)

    def test_negative_raises(self):
        """Test that negative IDs raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            int_to_minified_name(-1)


class TestMinifiedNameToInt:
    """Tests for minified_name_to_int reverse conversion."""

    def test_single_char(self):
        """Test single character conversion."""
        assert minified_name_to_int("a") == 0
        assert minified_name_to_int("b") == 1
        assert minified_name_to_int("z") == 25
        assert minified_name_to_int("A") == 26
        assert minified_name_to_int("Z") == 51

    def test_roundtrip(self):
        """Test that int -> minified -> int roundtrip works."""
        for i in range(1000):
            minified = int_to_minified_name(i)
            result = minified_name_to_int(minified)
            assert result == i, f"Roundtrip failed for {i}: {minified} -> {result}"

    def test_invalid_char_raises(self):
        """Test that invalid characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid character"):
            minified_name_to_int("!")


class TestGetStateFullPath:
    """Tests for get_state_full_path function."""

    def test_root_state_path(self):
        """Test that root State has correct full path."""
        path = get_state_full_path(State)
        assert path == "reflex.state.State"

    def test_substate_path(self):
        """Test that substates have correct full paths."""

        class TestState(BaseState):
            pass

        path = get_state_full_path(TestState)
        assert "TestState" in path
        assert path.startswith("tests.units.test_minification.")


@pytest.fixture
def temp_minify_json(tmp_path, monkeypatch):
    """Create a temporary directory and mock cwd to use it for minify.json.

    Yields:
        The temporary directory path.
    """
    monkeypatch.chdir(tmp_path)
    clear_config_cache()
    # Clear State caches to ensure clean slate
    State.get_name.cache_clear()
    State.get_full_name.cache_clear()
    State.get_class_substate.cache_clear()
    yield tmp_path
    # Clean up: clear config and all cached state names
    clear_config_cache()
    State.get_name.cache_clear()
    State.get_full_name.cache_clear()
    State.get_class_substate.cache_clear()


class TestMinifyConfig:
    """Tests for minify.json configuration loading and saving."""

    def test_no_config_returns_none(self, temp_minify_json):
        """Test that missing minify.json returns None."""
        assert is_minify_enabled() is False
        assert get_state_id("any.path") is None
        assert get_event_id("any.path", "handler") is None

    def test_save_and_load_config(self, temp_minify_json, monkeypatch):
        """Test saving and loading a config."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.ENABLED.value
        )
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_EVENTS.name, MinifyMode.ENABLED.value
        )
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {"test.module.MyState": "a"},
            "events": {"test.module.MyState": {"handler": "a"}},
        }
        save_minify_config(config)

        # Clear cache and reload
        clear_config_cache()

        assert is_minify_enabled() is True
        assert get_state_id("test.module.MyState") == "a"
        assert get_event_id("test.module.MyState", "handler") == "a"

    def test_invalid_version_raises(self, temp_minify_json, monkeypatch):
        """Test that invalid version raises ValueError."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.ENABLED.value
        )
        config = {"version": 999, "states": {}, "events": {}}
        path = temp_minify_json / MINIFY_JSON
        with path.open("w") as f:
            json.dump(config, f)

        clear_config_cache()

        with pytest.raises(ValueError, match=r"Unsupported.*version"):
            is_state_minify_enabled()

    def test_missing_states_raises(self, temp_minify_json, monkeypatch):
        """Test that missing 'states' key raises ValueError."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.ENABLED.value
        )
        config = {"version": SCHEMA_VERSION, "events": {}}
        path = temp_minify_json / MINIFY_JSON
        with path.open("w") as f:
            json.dump(config, f)

        clear_config_cache()

        with pytest.raises(ValueError, match="'states' must be"):
            is_state_minify_enabled()


class TestGenerateMinifyConfig:
    """Tests for generate_minify_config function."""

    def test_generate_for_root_state(self):
        """Test generating config for the root State."""
        config = generate_minify_config(State)

        assert config["version"] == SCHEMA_VERSION
        assert "reflex.state.State" in config["states"]
        # State should have event handlers like set_is_hydrated
        state_path = "reflex.state.State"
        assert state_path in config["events"]
        assert "set_is_hydrated" in config["events"][state_path]

    def test_generates_unique_sibling_ids(self):
        """Test that sibling states get unique IDs."""

        class ParentState(BaseState):
            pass

        class ChildA(ParentState):
            pass

        class ChildB(ParentState):
            pass

        config = generate_minify_config(ParentState)

        # Find the IDs for ChildA and ChildB
        child_a_path = get_state_full_path(ChildA)
        child_b_path = get_state_full_path(ChildB)

        child_a_id = config["states"].get(child_a_path)
        child_b_id = config["states"].get(child_b_path)

        assert child_a_id is not None
        assert child_b_id is not None
        assert child_a_id != child_b_id


class TestValidateMinifyConfig:
    """Tests for validate_minify_config function."""

    def test_valid_config_no_errors(self):
        """Test that a valid config produces no errors."""
        config = generate_minify_config(State)
        errors, _warnings, missing = validate_minify_config(config, State)

        assert len(errors) == 0
        assert len(missing) == 0

    def test_duplicate_state_ids_detected(self):
        """Test that duplicate state IDs are detected."""
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {
                "test.Parent": "a",
                "test.Parent.ChildA": "b",
                "test.Parent.ChildB": "b",  # Duplicate!
            },
            "events": {},
        }

        # Create a mock state tree
        class Parent(BaseState):
            pass

        errors, _warnings, _missing = validate_minify_config(config, Parent)

        assert any("Duplicate state_id='b'" in e for e in errors)


class TestSyncMinifyConfig:
    """Tests for sync_minify_config function."""

    def test_sync_adds_new_states(self):
        """Test that sync adds new states."""

        class TestState(BaseState):
            def handler(self):
                pass

        # Start with empty config
        existing_config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {},
            "events": {},
        }

        new_config = sync_minify_config(existing_config, TestState)

        # Should have added the state
        state_path = get_state_full_path(TestState)
        assert state_path in new_config["states"]
        assert state_path in new_config["events"]
        assert "handler" in new_config["events"][state_path]

    def test_sync_preserves_existing_ids(self):
        """Test that sync preserves existing IDs."""

        class TestState(BaseState):
            def handler_a(self):
                pass

            def handler_b(self):
                pass

        state_path = get_state_full_path(TestState)

        # Start with partial config (using string IDs in v2 format)
        existing_config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {state_path: "bU"},  # codespell:ignore
            "events": {state_path: {"handler_a": "k"}},  # Another arbitrary name
        }

        new_config = sync_minify_config(existing_config, TestState)

        # Existing IDs should be preserved
        assert new_config["states"][state_path] == "bU"  # codespell:ignore
        assert new_config["events"][state_path]["handler_a"] == "k"
        # New handler should be added with next ID (k=10, so next is l=11)
        assert "handler_b" in new_config["events"][state_path]
        assert (
            new_config["events"][state_path]["handler_b"] == "l"
        )  # 10 + 1 = 11 -> 'l'


class TestStateMinification:
    """Tests for state name minification with minify.json."""

    def test_state_uses_full_name_without_config(self, temp_minify_json):
        """Test that states use full names when no minify.json exists."""

        class TestState(BaseState):
            pass

        TestState.get_name.cache_clear()
        name = TestState.get_name()

        # Should be the full name (snake_case module___class)
        assert "test_state" in name.lower()

    def test_state_uses_minified_name_with_config(self, temp_minify_json, monkeypatch):
        """Test that states use minified names when minify.json exists and env var is enabled."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.ENABLED.value
        )

        class TestState(BaseState):
            pass

        state_path = get_state_full_path(TestState)
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {state_path: "f"},  # Direct minified name
            "events": {},
        }
        save_minify_config(config)
        clear_config_cache()
        TestState.get_name.cache_clear()

        name = TestState.get_name()

        # Should be the minified name directly
        assert name == "f"

    def test_state_uses_full_name_when_env_disabled(
        self, temp_minify_json, monkeypatch
    ):
        """Test that states use full names when env var is disabled even with minify.json."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.DISABLED.value
        )

        class TestState(BaseState):
            pass

        state_path = get_state_full_path(TestState)
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {state_path: "f"},
            "events": {},
        }
        save_minify_config(config)
        clear_config_cache()
        TestState.get_name.cache_clear()

        name = TestState.get_name()

        # Should be the full name, not minified
        assert name != "f"
        assert "test_state" in name.lower()


class TestEventMinification:
    """Tests for event handler name minification with minify.json."""

    def test_event_uses_full_name_without_config(self, temp_minify_json):
        """Test that event handlers use full names when no minify.json exists."""
        import reflex as rx
        from reflex.utils.format import get_event_handler_parts

        class TestState(BaseState):
            @rx.event
            def my_handler(self):
                pass

        TestState.get_name.cache_clear()
        handler = TestState.event_handlers["my_handler"]
        _, event_name = get_event_handler_parts(handler)

        # Should use full name
        assert event_name == "my_handler"

    def test_event_uses_minified_name_with_config(self, temp_minify_json, monkeypatch):
        """Test that event handlers use minified names when minify.json exists and env var is enabled."""
        import reflex as rx
        from reflex.utils.format import get_event_handler_parts

        monkeypatch.setenv(
            environment.REFLEX_MINIFY_EVENTS.name, MinifyMode.ENABLED.value
        )

        # First, set up the config BEFORE creating the state class
        # The event_id_to_name registry is built during __init_subclass__
        # so the config must exist before the class is defined

        # For this test, we extend State (not BaseState) so that
        # get_event_handler_parts can look up our state in the State tree.
        # We need to include State's full path in our config too.

        # The state path includes the full class hierarchy from State.
        # For a direct subclass of State defined in this test module,
        # get_state_full_path returns: "tests.units.test_minification.State.TestStateWithMinifiedEvent"
        # (module + class hierarchy from root state to leaf)

        expected_module = "tests.units.test_minification"
        expected_state_path = f"{expected_module}.State.TestStateWithMinifiedEvent"

        # Also need to include the base State in the config (v2 format with nested events)
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {
                "reflex.state.State": "a",  # Base State
                expected_state_path: "b",  # Our test state
            },
            "events": {
                expected_state_path: {"my_handler": "d"},  # Nested under state path
            },
        }
        save_minify_config(config)
        clear_config_cache()
        State.get_name.cache_clear()
        State.get_full_name.cache_clear()
        State.get_class_substate.cache_clear()

        # Now create the state class extending State - it will pick up the config
        class TestStateWithMinifiedEvent(State):
            @rx.event
            def my_handler(self):
                pass

        # Verify the path matches what we expected
        actual_path = get_state_full_path(TestStateWithMinifiedEvent)
        assert actual_path == expected_state_path, (
            f"Expected path {expected_state_path}, got {actual_path}"
        )

        # The state's _event_id_to_name should be populated (key is minified name)
        assert TestStateWithMinifiedEvent._event_id_to_name == {"d": "my_handler"}

        handler = TestStateWithMinifiedEvent.event_handlers["my_handler"]
        _, event_name = get_event_handler_parts(handler)

        # Should be the minified name directly
        assert event_name == "d"

    def test_event_uses_full_name_when_env_disabled(
        self, temp_minify_json, monkeypatch
    ):
        """Test that event handlers use full names when env var is disabled even with minify.json."""
        import reflex as rx
        from reflex.utils.format import get_event_handler_parts

        monkeypatch.setenv(
            environment.REFLEX_MINIFY_EVENTS.name, MinifyMode.DISABLED.value
        )

        expected_module = "tests.units.test_minification"
        expected_state_path = (
            f"{expected_module}.State.TestStateWithMinifiedEventDisabled"
        )

        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {
                "reflex.state.State": "a",
                expected_state_path: "b",
            },
            "events": {
                expected_state_path: {"my_handler": "d"},
            },
        }
        save_minify_config(config)
        clear_config_cache()
        State.get_name.cache_clear()
        State.get_full_name.cache_clear()
        State.get_class_substate.cache_clear()

        class TestStateWithMinifiedEventDisabled(State):
            @rx.event
            def my_handler(self):
                pass

        # The state's _event_id_to_name should be empty when env var is disabled
        assert TestStateWithMinifiedEventDisabled._event_id_to_name == {}

        handler = TestStateWithMinifiedEventDisabled.event_handlers["my_handler"]
        _, event_name = get_event_handler_parts(handler)

        # Should use full name
        assert event_name == "my_handler"


class TestDynamicHandlerMinification:
    """Tests for dynamic event handler minification (setvar, auto-setters)."""

    def test_setvar_registered_with_config(self, temp_minify_json, monkeypatch):
        """Test that setvar is registered in _event_id_to_name when config exists."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_EVENTS.name, MinifyMode.ENABLED.value
        )
        expected_module = "tests.units.test_minification"
        expected_state_path = f"{expected_module}.State.TestStateWithSetvar"

        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {
                "reflex.state.State": "a",
                expected_state_path: "b",
            },
            "events": {
                expected_state_path: {"setvar": "s"},
            },
        }
        save_minify_config(config)
        clear_config_cache()
        State.get_name.cache_clear()
        State.get_full_name.cache_clear()
        State.get_class_substate.cache_clear()

        class TestStateWithSetvar(State):
            pass

        # Verify setvar is registered for minification
        assert "s" in TestStateWithSetvar._event_id_to_name
        assert TestStateWithSetvar._event_id_to_name["s"] == "setvar"

    def test_auto_setter_registered_with_config(self, temp_minify_json, monkeypatch):
        """Test that auto-setters (set_*) are registered in _event_id_to_name when config exists."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_EVENTS.name, MinifyMode.ENABLED.value
        )
        expected_module = "tests.units.test_minification"
        expected_state_path = f"{expected_module}.State.TestStateWithAutoSetter"

        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {
                "reflex.state.State": "a",
                expected_state_path: "b",
            },
            "events": {
                expected_state_path: {"set_count": "c", "setvar": "v"},
            },
        }
        save_minify_config(config)
        clear_config_cache()
        State.get_name.cache_clear()
        State.get_full_name.cache_clear()
        State.get_class_substate.cache_clear()

        class TestStateWithAutoSetter(State):
            count: int = 0

        # Verify auto-setter is registered for minification
        assert "c" in TestStateWithAutoSetter._event_id_to_name
        assert TestStateWithAutoSetter._event_id_to_name["c"] == "set_count"

    def test_dynamic_handlers_not_registered_without_config(self, temp_minify_json):
        """Test that dynamic handlers are NOT registered when no config exists."""
        # No config saved - temp_minify_json fixture ensures clean state

        class TestStateNoConfig(State):
            count: int = 0

        # Without config, _event_id_to_name should be empty
        assert TestStateNoConfig._event_id_to_name == {}

    def test_add_event_handler_registered_with_config(
        self, temp_minify_json, monkeypatch
    ):
        """Test that dynamically added event handlers via _add_event_handler are registered."""
        import reflex as rx

        monkeypatch.setenv(
            environment.REFLEX_MINIFY_EVENTS.name, MinifyMode.ENABLED.value
        )
        expected_module = "tests.units.test_minification"
        expected_state_path = f"{expected_module}.State.TestStateWithDynamicHandler"

        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {
                "reflex.state.State": "a",
                expected_state_path: "b",
            },
            "events": {
                expected_state_path: {"dynamic_handler": "d", "setvar": "v"},
            },
        }
        save_minify_config(config)
        clear_config_cache()
        State.get_name.cache_clear()
        State.get_full_name.cache_clear()
        State.get_class_substate.cache_clear()

        class TestStateWithDynamicHandler(State):
            pass

        # Dynamically add an event handler after class creation
        @rx.event
        def dynamic_handler(self):
            pass

        from reflex.event import EventHandler

        handler = EventHandler(
            fn=dynamic_handler,
            state_full_name=TestStateWithDynamicHandler.get_full_name(),
        )
        TestStateWithDynamicHandler._add_event_handler("dynamic_handler", handler)

        # Verify dynamic handler is registered for minification
        assert "d" in TestStateWithDynamicHandler._event_id_to_name
        assert TestStateWithDynamicHandler._event_id_to_name["d"] == "dynamic_handler"


class TestMinifyModeEnvVars:
    """Tests for REFLEX_MINIFY_STATES and REFLEX_MINIFY_EVENTS env vars."""

    def test_state_minify_disabled_by_default(self, temp_minify_json):
        """Test that state minification is disabled by default."""
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {"test.module.MyState": "a"},
            "events": {},
        }
        save_minify_config(config)
        clear_config_cache()

        assert is_state_minify_enabled() is False

    def test_event_minify_disabled_by_default(self, temp_minify_json):
        """Test that event minification is disabled by default."""
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {},
            "events": {"test.module.MyState": {"handler": "a"}},
        }
        save_minify_config(config)
        clear_config_cache()

        assert is_event_minify_enabled() is False

    def test_state_minify_enabled_with_env_and_config(
        self, temp_minify_json, monkeypatch
    ):
        """Test that state minification is enabled when env var is enabled and config exists."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.ENABLED.value
        )
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {"test.module.MyState": "a"},
            "events": {},
        }
        save_minify_config(config)
        clear_config_cache()

        assert is_state_minify_enabled() is True

    def test_event_minify_enabled_with_env_and_config(
        self, temp_minify_json, monkeypatch
    ):
        """Test that event minification is enabled when env var is enabled and config exists."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_EVENTS.name, MinifyMode.ENABLED.value
        )
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {},
            "events": {"test.module.MyState": {"handler": "a"}},
        }
        save_minify_config(config)
        clear_config_cache()

        assert is_event_minify_enabled() is True

    def test_state_minify_disabled_without_config(self, temp_minify_json, monkeypatch):
        """Test that state minification is disabled when env var is enabled but no config exists."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.ENABLED.value
        )
        clear_config_cache()

        assert is_state_minify_enabled() is False

    def test_event_minify_disabled_without_config(self, temp_minify_json, monkeypatch):
        """Test that event minification is disabled when env var is enabled but no config exists."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_EVENTS.name, MinifyMode.ENABLED.value
        )
        clear_config_cache()

        assert is_event_minify_enabled() is False

    def test_independent_state_and_event_toggles(self, temp_minify_json, monkeypatch):
        """Test that state and event minification can be toggled independently."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.ENABLED.value
        )
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_EVENTS.name, MinifyMode.DISABLED.value
        )
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {"test.module.MyState": "a"},
            "events": {"test.module.MyState": {"handler": "a"}},
        }
        save_minify_config(config)
        clear_config_cache()

        assert is_state_minify_enabled() is True
        assert is_event_minify_enabled() is False
        assert is_minify_enabled() is True

    def test_is_minify_enabled_true_when_either_enabled(
        self, temp_minify_json, monkeypatch
    ):
        """Test that is_minify_enabled returns True when either state or event is enabled."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.DISABLED.value
        )
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_EVENTS.name, MinifyMode.ENABLED.value
        )
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {},
            "events": {"test.module.MyState": {"handler": "a"}},
        }
        save_minify_config(config)
        clear_config_cache()

        assert is_minify_enabled() is True

    def test_is_minify_enabled_false_when_both_disabled(self, temp_minify_json):
        """Test that is_minify_enabled returns False when both are disabled (default)."""
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {"test.module.MyState": "a"},
            "events": {"test.module.MyState": {"handler": "a"}},
        }
        save_minify_config(config)
        clear_config_cache()

        assert is_minify_enabled() is False


class TestMinifiedNameCollision:
    """Tests for parent-child minified name collision in substate resolution."""

    def test_get_class_substate_with_parent_child_name_collision(
        self, temp_minify_json, monkeypatch
    ):
        """Test that get_class_substate resolves correctly when parent and child
        share the same minified name (IDs are only sibling-unique).
        """
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.ENABLED.value
        )

        # Build a hierarchy: State -> ParentState -> ChildState
        # where ParentState and ChildState both get minified name "b"

        class ParentState(State):
            pass

        class ChildState(ParentState):
            pass

        parent_path = get_state_full_path(ParentState)
        child_path = get_state_full_path(ChildState)

        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {
                "reflex.state.State": "a",
                parent_path: "b",
                child_path: "b",  # Same minified name as parent
            },
            "events": {},
        }
        save_minify_config(config)
        clear_config_cache()
        State.get_name.cache_clear()
        State.get_full_name.cache_clear()
        State.get_class_substate.cache_clear()
        ParentState.get_name.cache_clear()
        ParentState.get_full_name.cache_clear()
        ChildState.get_name.cache_clear()
        ChildState.get_full_name.cache_clear()

        # Verify both get the same minified name
        assert ParentState.get_name() == "b"
        assert ChildState.get_name() == "b"

        # Full path should be a.b.b
        assert ChildState.get_full_name() == "a.b.b"

        # get_class_substate should resolve a.b.b to ChildState, not ParentState
        resolved = State.get_class_substate("a.b.b")
        assert resolved is ChildState

    def test_get_substate_with_parent_child_name_collision(
        self, temp_minify_json, monkeypatch
    ):
        """Test that get_substate (instance method) resolves correctly when parent
        and child share the same minified name.
        """
        import reflex as rx

        monkeypatch.setenv(
            environment.REFLEX_MINIFY_STATES.name, MinifyMode.ENABLED.value
        )

        class ParentState2(State):
            pass

        class ChildState2(ParentState2):
            @rx.event
            def my_handler(self):
                pass

        parent_path = get_state_full_path(ParentState2)
        child_path = get_state_full_path(ChildState2)

        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {
                "reflex.state.State": "a",
                parent_path: "b",
                child_path: "b",  # Same minified name as parent
            },
            "events": {},
        }
        save_minify_config(config)
        clear_config_cache()
        State.get_name.cache_clear()
        State.get_full_name.cache_clear()
        State.get_class_substate.cache_clear()
        ParentState2.get_name.cache_clear()
        ParentState2.get_full_name.cache_clear()
        ChildState2.get_name.cache_clear()
        ChildState2.get_full_name.cache_clear()

        # Create a state instance tree
        root = State(_reflex_internal_init=True)  # type: ignore[call-arg]

        # Instance get_substate should resolve a.b.b to ChildState2
        resolved = root.get_substate(["a", "b", "b"])
        assert type(resolved) is ChildState2


class TestVarMinification:
    """Tests for variable name minification with minify.json."""

    def test_var_minify_disabled_by_default(self, temp_minify_json):
        """Test that var minification is disabled by default."""
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {"test.module.MyState": "a"},
            "events": {},
            "vars": {"test.module.MyState": {"my_var": "a"}},
        }
        save_minify_config(config)
        clear_config_cache()

        assert is_var_minify_enabled() is False

    def test_var_minify_enabled_with_env_and_config(
        self, temp_minify_json, monkeypatch
    ):
        """Test that var minification is enabled when env var is enabled and config exists."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_VARS.name, MinifyMode.ENABLED.value
        )
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {"test.module.MyState": "a"},
            "events": {},
            "vars": {"test.module.MyState": {"my_var": "a"}},
        }
        save_minify_config(config)
        clear_config_cache()

        assert is_var_minify_enabled() is True

    def test_var_minify_disabled_without_config(self, temp_minify_json, monkeypatch):
        """Test that var minification is disabled when env var is enabled but no config exists."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_VARS.name, MinifyMode.ENABLED.value
        )
        clear_config_cache()

        assert is_var_minify_enabled() is False

    def test_get_var_id_returns_minified_name(self, temp_minify_json, monkeypatch):
        """Test that get_var_id returns the minified name from config."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_VARS.name, MinifyMode.ENABLED.value
        )
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {"test.module.MyState": "a"},
            "events": {},
            "vars": {"test.module.MyState": {"my_var": "x"}},
        }
        save_minify_config(config)
        clear_config_cache()

        assert get_var_id("test.module.MyState", "my_var") == "x"
        assert get_var_id("test.module.MyState", "nonexistent") is None
        assert get_var_id("nonexistent.State", "my_var") is None

    def test_get_frontend_var_names(self, temp_minify_json):
        """Test that _get_frontend_var_names returns correct var names."""
        import reflex as rx

        class TestStateVars(BaseState):
            count: int = 0
            name: str = ""

            @rx.var
            def computed_value(self) -> int:
                return self.count * 2

            @rx.var(backend=True)
            def _backend_var(self) -> str:
                return "internal"

        var_names = _get_frontend_var_names(TestStateVars)

        # Should include base vars and non-backend computed vars
        assert "count" in var_names
        assert "name" in var_names
        assert "computed_value" in var_names
        # Should NOT include backend computed vars
        assert "_backend_var" not in var_names

    def test_generate_config_includes_vars(self, temp_minify_json):
        """Test that generate_minify_config includes vars section."""
        import reflex as rx

        class TestStateGenVars(BaseState):
            my_field: int = 0

            @rx.var
            def my_computed(self) -> int:
                return self.my_field * 2

        config = generate_minify_config(TestStateGenVars)

        assert "vars" in config
        state_path = get_state_full_path(TestStateGenVars)
        config_vars = config.get("vars", {})
        assert state_path in config_vars
        assert "my_field" in config_vars[state_path]
        assert "my_computed" in config_vars[state_path]

    def test_validate_config_detects_duplicate_var_ids(self, temp_minify_json):
        """Test that validate_minify_config detects duplicate var IDs."""

        class TestStateValidate(BaseState):
            var_a: int = 0
            var_b: int = 0

        state_path = get_state_full_path(TestStateValidate)
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {state_path: "a"},
            "events": {},
            "vars": {
                state_path: {
                    "var_a": "x",
                    "var_b": "x",  # Duplicate!
                },
            },
        }

        errors, _warnings, _missing = validate_minify_config(config, TestStateValidate)

        assert any("Duplicate var_id='x'" in e for e in errors)

    def test_validate_config_detects_missing_vars(self, temp_minify_json):
        """Test that validate_minify_config detects missing vars."""

        class TestStateMissing(BaseState):
            my_var: int = 0

        state_path = get_state_full_path(TestStateMissing)
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {state_path: "a"},
            "events": {},
            "vars": {},  # Missing vars section
        }

        _errors, _warnings, missing = validate_minify_config(config, TestStateMissing)

        assert any(f"var:{state_path}.my_var" in m for m in missing)

    def test_sync_config_adds_new_vars(self, temp_minify_json):
        """Test that sync_minify_config adds new vars."""

        class TestStateSync(BaseState):
            new_var: int = 0

        state_path = get_state_full_path(TestStateSync)
        existing_config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {state_path: "a"},
            "events": {},
            "vars": {},
        }

        new_config = sync_minify_config(existing_config, TestStateSync)

        new_config_vars = new_config.get("vars", {})
        assert state_path in new_config_vars
        assert "new_var" in new_config_vars[state_path]

    def test_state_get_var_name_returns_minified(self, temp_minify_json, monkeypatch):
        """Test that _get_var_name returns minified name when enabled."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_VARS.name, MinifyMode.ENABLED.value
        )

        class TestStateGetVarName(State):
            my_field: int = 0

        state_path = get_state_full_path(TestStateGetVarName)
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {
                "reflex.state.State": "a",
                state_path: "b",
            },
            "events": {},
            "vars": {state_path: {"my_field": "z"}},
        }
        save_minify_config(config)
        clear_config_cache()
        State.get_name.cache_clear()
        State.get_full_name.cache_clear()
        TestStateGetVarName._get_var_name.cache_clear()

        # _get_var_name should return minified name
        assert TestStateGetVarName._get_var_name("my_field") == "z"

    def test_state_get_var_name_returns_original_when_disabled(
        self, temp_minify_json, monkeypatch
    ):
        """Test that _get_var_name returns original name when env var is disabled."""
        monkeypatch.setenv(
            environment.REFLEX_MINIFY_VARS.name, MinifyMode.DISABLED.value
        )

        class TestStateGetVarNameOrig(State):
            my_field: int = 0

        state_path = get_state_full_path(TestStateGetVarNameOrig)
        config: MinifyConfig = {
            "version": SCHEMA_VERSION,
            "states": {
                "reflex.state.State": "a",
                state_path: "b",
            },
            "events": {},
            "vars": {state_path: {"my_field": "z"}},
        }
        save_minify_config(config)
        clear_config_cache()
        TestStateGetVarNameOrig._get_var_name.cache_clear()

        # _get_var_name should return original name when disabled
        assert TestStateGetVarNameOrig._get_var_name("my_field") == "my_field"
