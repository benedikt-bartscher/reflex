"""Stub file for reflex/components/plotly/plotly.py"""

# ------------------- DO NOT EDIT ----------------------
# This file was generated by `reflex/utils/pyi_generator.py`!
# ------------------------------------------------------
from typing import Any, Dict, List, Optional, Union, overload

from typing_extensions import TypedDict, TypeVar

from reflex.components.component import NoSSRComponent
from reflex.event import BASE_STATE, EventType
from reflex.style import Style
from reflex.utils import console
from reflex.vars.base import Var

try:
    from plotly.graph_objects import Figure, layout

    Template = layout.Template
except ImportError:
    console.warn("Plotly is not installed. Please run `pip install plotly`.")
    Figure = Any
    Template = Any
T = TypeVar("T")
ItemOrList = Union[T, List[T]]

class BBox(TypedDict):
    x0: Union[float, int, None]
    x1: Union[float, int, None]
    y0: Union[float, int, None]
    y1: Union[float, int, None]
    z0: Union[float, int, None]
    z1: Union[float, int, None]

class Point(TypedDict):
    x: Union[float, int, None]
    y: Union[float, int, None]
    z: Union[float, int, None]
    lat: Union[float, int, None]
    lon: Union[float, int, None]
    curveNumber: Union[int, None]
    pointNumber: Union[int, None]
    pointNumbers: Union[List[int], None]
    pointIndex: Union[int, None]
    markerColor: Union[ItemOrList[ItemOrList[Union[float, int, str, None]]], None]
    markerSize: Union[ItemOrList[ItemOrList[Union[float, int, None]]], None]
    bbox: Union[BBox, None]

class Plotly(NoSSRComponent):
    def add_imports(self) -> dict[str, str]: ...
    def add_custom_code(self) -> list[str]: ...
    @overload
    @classmethod
    def create(  # type: ignore
        cls,
        *children,
        data: Optional[Union[Figure, Var[Figure]]] = None,  # type: ignore
        layout: Optional[Union[Dict, Var[Dict]]] = None,
        template: Optional[Union[Template, Var[Template]]] = None,  # type: ignore
        config: Optional[Union[Dict, Var[Dict]]] = None,
        use_resize_handler: Optional[Union[Var[bool], bool]] = None,
        style: Optional[Style] = None,
        key: Optional[Any] = None,
        id: Optional[Any] = None,
        class_name: Optional[Any] = None,
        autofocus: Optional[bool] = None,
        custom_attrs: Optional[Dict[str, Union[Var, Any]]] = None,
        on_after_plot: Optional[EventType[[], BASE_STATE]] = None,
        on_animated: Optional[EventType[[], BASE_STATE]] = None,
        on_animating_frame: Optional[EventType[[], BASE_STATE]] = None,
        on_animation_interrupted: Optional[EventType[[], BASE_STATE]] = None,
        on_autosize: Optional[EventType[[], BASE_STATE]] = None,
        on_before_hover: Optional[EventType[[], BASE_STATE]] = None,
        on_blur: Optional[EventType[[], BASE_STATE]] = None,
        on_button_clicked: Optional[EventType[[], BASE_STATE]] = None,
        on_click: Optional[
            Union[EventType[[], BASE_STATE], EventType[[List[Point]], BASE_STATE]]
        ] = None,
        on_context_menu: Optional[EventType[[], BASE_STATE]] = None,
        on_deselect: Optional[EventType[[], BASE_STATE]] = None,
        on_double_click: Optional[EventType[[], BASE_STATE]] = None,
        on_focus: Optional[EventType[[], BASE_STATE]] = None,
        on_hover: Optional[
            Union[EventType[[], BASE_STATE], EventType[[List[Point]], BASE_STATE]]
        ] = None,
        on_mount: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_down: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_enter: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_leave: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_move: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_out: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_over: Optional[EventType[[], BASE_STATE]] = None,
        on_mouse_up: Optional[EventType[[], BASE_STATE]] = None,
        on_redraw: Optional[EventType[[], BASE_STATE]] = None,
        on_relayout: Optional[EventType[[], BASE_STATE]] = None,
        on_relayouting: Optional[EventType[[], BASE_STATE]] = None,
        on_restyle: Optional[EventType[[], BASE_STATE]] = None,
        on_scroll: Optional[EventType[[], BASE_STATE]] = None,
        on_selected: Optional[
            Union[EventType[[], BASE_STATE], EventType[[List[Point]], BASE_STATE]]
        ] = None,
        on_selecting: Optional[
            Union[EventType[[], BASE_STATE], EventType[[List[Point]], BASE_STATE]]
        ] = None,
        on_transition_interrupted: Optional[EventType[[], BASE_STATE]] = None,
        on_transitioning: Optional[EventType[[], BASE_STATE]] = None,
        on_unhover: Optional[
            Union[EventType[[], BASE_STATE], EventType[[List[Point]], BASE_STATE]]
        ] = None,
        on_unmount: Optional[EventType[[], BASE_STATE]] = None,
        **props,
    ) -> "Plotly":
        """Create the Plotly component.

        Args:
            *children: The children of the component.
            data: The figure to display. This can be a plotly figure or a plotly data json.
            layout: The layout of the graph.
            template: The template for visual appearance of the graph.
            config: The config of the graph.
            use_resize_handler: If true, the graph will resize when the window is resized.
            on_after_plot: Fired after the plot is redrawn.
            on_animated: Fired after the plot was animated.
            on_animating_frame: Fired while animating a single frame (does not currently pass data through).
            on_animation_interrupted: Fired when an animation is interrupted (to start a new animation for example).
            on_autosize: Fired when the plot is responsively sized.
            on_before_hover: Fired whenever mouse moves over a plot.
            on_button_clicked: Fired when a plotly UI button is clicked.
            on_click: Fired when the plot is clicked.
            on_deselect: Fired when a selection is cleared (via double click).
            on_double_click: Fired when the plot is double clicked.
            on_hover: Fired when a plot element is hovered over.
            on_relayout: Fired after the plot is layed out (zoom, pan, etc).
            on_relayouting: Fired while the plot is being layed out.
            on_restyle: Fired after the plot style is changed.
            on_redraw: Fired after the plot is redrawn.
            on_selected: Fired after selecting plot elements.
            on_selecting: Fired while dragging a selection.
            on_transitioning: Fired while an animation is occuring.
            on_transition_interrupted: Fired when a transition is stopped early.
            on_unhover: Fired when a hovered element is no longer hovered.
            style: The style of the component.
            key: A unique key for the component.
            id: The id for the component.
            class_name: The class name for the component.
            autofocus: Whether the component should take the focus once the page is loaded
            custom_attrs: custom attribute
            **props: The properties of the component.

        Returns:
            The Plotly component.
        """
        ...
