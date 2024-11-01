"""Stub file for reflex/components/radix/themes/components/slider.py"""

# ------------------- DO NOT EDIT ----------------------
# This file was generated by `reflex/utils/pyi_generator.py`!
# ------------------------------------------------------
from typing import Any, Dict, List, Literal, Optional, Union, overload

from reflex.components.core.breakpoints import Breakpoints
from reflex.event import EventType, identity_event
from reflex.style import Style
from reflex.vars.base import Var

from ..base import RadixThemesComponent

on_value_event_spec = (
    identity_event(list[Union[int, float]]),
    identity_event(list[int]),
    identity_event(list[float]),
)

class Slider(RadixThemesComponent):
    @overload
    @classmethod
    def create(  # type: ignore
        cls,
        *children,
        width: Optional[str] = "100%",
        as_child: Optional[Union[Var[bool], bool]] = None,
        size: Optional[
            Union[
                Breakpoints[str, Literal["1", "2", "3"]],
                Literal["1", "2", "3"],
                Var[
                    Union[
                        Breakpoints[str, Literal["1", "2", "3"]], Literal["1", "2", "3"]
                    ]
                ],
            ]
        ] = None,
        variant: Optional[
            Union[
                Literal["classic", "soft", "surface"],
                Var[Literal["classic", "soft", "surface"]],
            ]
        ] = None,
        color_scheme: Optional[
            Union[
                Literal[
                    "amber",
                    "blue",
                    "bronze",
                    "brown",
                    "crimson",
                    "cyan",
                    "gold",
                    "grass",
                    "gray",
                    "green",
                    "indigo",
                    "iris",
                    "jade",
                    "lime",
                    "mint",
                    "orange",
                    "pink",
                    "plum",
                    "purple",
                    "red",
                    "ruby",
                    "sky",
                    "teal",
                    "tomato",
                    "violet",
                    "yellow",
                ],
                Var[
                    Literal[
                        "amber",
                        "blue",
                        "bronze",
                        "brown",
                        "crimson",
                        "cyan",
                        "gold",
                        "grass",
                        "gray",
                        "green",
                        "indigo",
                        "iris",
                        "jade",
                        "lime",
                        "mint",
                        "orange",
                        "pink",
                        "plum",
                        "purple",
                        "red",
                        "ruby",
                        "sky",
                        "teal",
                        "tomato",
                        "violet",
                        "yellow",
                    ]
                ],
            ]
        ] = None,
        high_contrast: Optional[Union[Var[bool], bool]] = None,
        radius: Optional[
            Union[
                Literal["full", "none", "small"], Var[Literal["full", "none", "small"]]
            ]
        ] = None,
        default_value: Optional[
            Union[
                List[Union[float, int]],
                Var[Union[List[Union[float, int]], float, int]],
                float,
                int,
            ]
        ] = None,
        value: Optional[
            Union[List[Union[float, int]], Var[List[Union[float, int]]]]
        ] = None,
        name: Optional[Union[Var[str], str]] = None,
        min: Optional[Union[Var[Union[float, int]], float, int]] = None,
        max: Optional[Union[Var[Union[float, int]], float, int]] = None,
        step: Optional[Union[Var[Union[float, int]], float, int]] = None,
        disabled: Optional[Union[Var[bool], bool]] = None,
        orientation: Optional[
            Union[
                Literal["horizontal", "vertical"],
                Var[Literal["horizontal", "vertical"]],
            ]
        ] = None,
        style: Optional[Style] = None,
        key: Optional[Any] = None,
        id: Optional[Any] = None,
        class_name: Optional[Any] = None,
        autofocus: Optional[bool] = None,
        custom_attrs: Optional[Dict[str, Union[Var, str]]] = None,
        on_blur: Optional[EventType[[]]] = None,
        on_change: Optional[
            Union[
                EventType[list[Union[int, float]]],
                EventType[list[int]],
                EventType[list[float]],
            ]
        ] = None,
        on_click: Optional[EventType[[]]] = None,
        on_context_menu: Optional[EventType[[]]] = None,
        on_double_click: Optional[EventType[[]]] = None,
        on_focus: Optional[EventType[[]]] = None,
        on_mount: Optional[EventType[[]]] = None,
        on_mouse_down: Optional[EventType[[]]] = None,
        on_mouse_enter: Optional[EventType[[]]] = None,
        on_mouse_leave: Optional[EventType[[]]] = None,
        on_mouse_move: Optional[EventType[[]]] = None,
        on_mouse_out: Optional[EventType[[]]] = None,
        on_mouse_over: Optional[EventType[[]]] = None,
        on_mouse_up: Optional[EventType[[]]] = None,
        on_scroll: Optional[EventType[[]]] = None,
        on_unmount: Optional[EventType[[]]] = None,
        on_value_commit: Optional[
            Union[
                EventType[list[Union[int, float]]],
                EventType[list[int]],
                EventType[list[float]],
            ]
        ] = None,
        **props,
    ) -> "Slider":
        """Create a Slider component.

        Args:
            *children: The children of the component.
            width: The width of the slider.
            as_child: Change the default rendered element for the one passed as a child, merging their props and behavior.
            size: Button size "1" - "3"
            variant: Variant of button
            color_scheme: Override theme color for button
            high_contrast: Whether to render the button with higher contrast color against background
            radius: Override theme radius for button: "none" | "small" | "full"
            default_value: The value of the slider when initially rendered. Use when you do not need to control the state of the slider.
            value: The controlled value of the slider. Must be used in conjunction with onValueChange.
            name: The name of the slider. Submitted with its owning form as part of a name/value pair.
            min: The minimum value of the slider.
            max: The maximum value of the slider.
            step: The step value of the slider.
            disabled: Whether the slider is disabled
            orientation: The orientation of the slider.
            on_change: Props to rename  Fired when the value of the slider changes.
            on_value_commit: Fired when a thumb is released after being dragged.
            style: The style of the component.
            key: A unique key for the component.
            id: The id for the component.
            class_name: The class name for the component.
            autofocus: Whether the component should take the focus once the page is loaded
            custom_attrs: custom attribute
            **props: The properties of the component.

        Returns:
            The component.
        """
        ...

slider = Slider.create
