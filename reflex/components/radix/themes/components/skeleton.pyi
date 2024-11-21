"""Stub file for reflex/components/radix/themes/components/skeleton.py"""

# ------------------- DO NOT EDIT ----------------------
# This file was generated by `reflex/utils/pyi_generator.py`!
# ------------------------------------------------------
from typing import Any, Dict, Optional, Union, overload

from reflex.components.core.breakpoints import Breakpoints
from reflex.event import BASE_STATE, EventType
from reflex.style import Style
from reflex.vars.base import Var

from ..base import RadixLoadingProp, RadixThemesComponent

class Skeleton(RadixLoadingProp, RadixThemesComponent):
    @overload
    @classmethod
    def create(  # type: ignore
        cls,
        *children,
        width: Optional[
            Union[Breakpoints[str, str], Var[Union[Breakpoints[str, str], str]], str]
        ] = None,
        min_width: Optional[
            Union[Breakpoints[str, str], Var[Union[Breakpoints[str, str], str]], str]
        ] = None,
        max_width: Optional[
            Union[Breakpoints[str, str], Var[Union[Breakpoints[str, str], str]], str]
        ] = None,
        height: Optional[
            Union[Breakpoints[str, str], Var[Union[Breakpoints[str, str], str]], str]
        ] = None,
        min_height: Optional[
            Union[Breakpoints[str, str], Var[Union[Breakpoints[str, str], str]], str]
        ] = None,
        max_height: Optional[
            Union[Breakpoints[str, str], Var[Union[Breakpoints[str, str], str]], str]
        ] = None,
        loading: Optional[Union[Var[bool], bool]] = None,
        style: Optional[Style] = None,
        key: Optional[Any] = None,
        id: Optional[Any] = None,
        class_name: Optional[Any] = None,
        autofocus: Optional[bool] = None,
        custom_attrs: Optional[Dict[str, Union[Var, Any]]] = None,
        on_blur: Optional[EventType[[], BASE_STATE]] = None,
        on_click: Optional[EventType[[], BASE_STATE]] = None,
        on_context_menu: Optional[EventType[[], BASE_STATE]] = None,
        on_double_click: Optional[EventType[[], BASE_STATE]] = None,
        on_focus: Optional[EventType[[], BASE_STATE]] = None,
        on_mount: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_down: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_enter: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_leave: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_move: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_out: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_over: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_up: Optional[EventType[[], BASE_STATE]] = None,
        on_scroll: Optional[EventType[[], BASE_STATE]] = None,
        on_unmount: Optional[EventType[[], BASE_STATE]] = None,
        **props,
    ) -> "Skeleton":
        """Create a new component instance.

        Will prepend "RadixThemes" to the component tag to avoid conflicts with
        other UI libraries for common names, like Text and Button.

        Args:
            *children: Child components.
            width: The width of the skeleton
            min_width: The minimum width of the skeleton
            max_width: The maximum width of the skeleton
            height: The height of the skeleton
            min_height: The minimum height of the skeleton
            max_height: The maximum height of the skeleton
            loading: If set, show an rx.spinner instead of the component children.
            style: The style of the component.
            key: A unique key for the component.
            id: The id for the component.
            class_name: The class name for the component.
            autofocus: Whether the component should take the focus once the page is loaded
            custom_attrs: custom attribute
            **props: Component properties.

        Returns:
            A new component instance.
        """
        ...

skeleton = Skeleton.create
