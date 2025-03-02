"""Stub file for reflex/components/core/html.py"""

# ------------------- DO NOT EDIT ----------------------
# This file was generated by `reflex/utils/pyi_generator.py`!
# ------------------------------------------------------
from typing import Any, Literal, Optional, overload

from reflex.components.el.elements.typography import Div
from reflex.event import EventType
from reflex.style import Style
from reflex.vars.base import Var

class Html(Div):
    @overload
    @classmethod
    def create(  # type: ignore
        cls,
        *children,
        dangerouslySetInnerHTML: Var[dict[str, str]] | dict[str, str] | None = None,
        access_key: Var[str] | str | None = None,
        auto_capitalize: Literal[
            "characters", "none", "off", "on", "sentences", "words"
        ]
        | Var[Literal["characters", "none", "off", "on", "sentences", "words"]]
        | None = None,
        content_editable: Literal["inherit", "plaintext-only", False, True]
        | Var[Literal["inherit", "plaintext-only", False, True]]
        | None = None,
        context_menu: Var[str] | str | None = None,
        dir: Var[str] | str | None = None,
        draggable: Var[bool] | bool | None = None,
        enter_key_hint: Literal[
            "done", "enter", "go", "next", "previous", "search", "send"
        ]
        | Var[Literal["done", "enter", "go", "next", "previous", "search", "send"]]
        | None = None,
        hidden: Var[bool] | bool | None = None,
        input_mode: Literal[
            "decimal", "email", "none", "numeric", "search", "tel", "text", "url"
        ]
        | Var[
            Literal[
                "decimal", "email", "none", "numeric", "search", "tel", "text", "url"
            ]
        ]
        | None = None,
        item_prop: Var[str] | str | None = None,
        lang: Var[str] | str | None = None,
        role: Literal[
            "alert",
            "alertdialog",
            "application",
            "article",
            "banner",
            "button",
            "cell",
            "checkbox",
            "columnheader",
            "combobox",
            "complementary",
            "contentinfo",
            "definition",
            "dialog",
            "directory",
            "document",
            "feed",
            "figure",
            "form",
            "grid",
            "gridcell",
            "group",
            "heading",
            "img",
            "link",
            "list",
            "listbox",
            "listitem",
            "log",
            "main",
            "marquee",
            "math",
            "menu",
            "menubar",
            "menuitem",
            "menuitemcheckbox",
            "menuitemradio",
            "navigation",
            "none",
            "note",
            "option",
            "presentation",
            "progressbar",
            "radio",
            "radiogroup",
            "region",
            "row",
            "rowgroup",
            "rowheader",
            "scrollbar",
            "search",
            "searchbox",
            "separator",
            "slider",
            "spinbutton",
            "status",
            "switch",
            "tab",
            "table",
            "tablist",
            "tabpanel",
            "term",
            "textbox",
            "timer",
            "toolbar",
            "tooltip",
            "tree",
            "treegrid",
            "treeitem",
        ]
        | Var[
            Literal[
                "alert",
                "alertdialog",
                "application",
                "article",
                "banner",
                "button",
                "cell",
                "checkbox",
                "columnheader",
                "combobox",
                "complementary",
                "contentinfo",
                "definition",
                "dialog",
                "directory",
                "document",
                "feed",
                "figure",
                "form",
                "grid",
                "gridcell",
                "group",
                "heading",
                "img",
                "link",
                "list",
                "listbox",
                "listitem",
                "log",
                "main",
                "marquee",
                "math",
                "menu",
                "menubar",
                "menuitem",
                "menuitemcheckbox",
                "menuitemradio",
                "navigation",
                "none",
                "note",
                "option",
                "presentation",
                "progressbar",
                "radio",
                "radiogroup",
                "region",
                "row",
                "rowgroup",
                "rowheader",
                "scrollbar",
                "search",
                "searchbox",
                "separator",
                "slider",
                "spinbutton",
                "status",
                "switch",
                "tab",
                "table",
                "tablist",
                "tabpanel",
                "term",
                "textbox",
                "timer",
                "toolbar",
                "tooltip",
                "tree",
                "treegrid",
                "treeitem",
            ]
        ]
        | None = None,
        slot: Var[str] | str | None = None,
        spell_check: Var[bool] | bool | None = None,
        tab_index: Var[int] | int | None = None,
        title: Var[str] | str | None = None,
        style: Style | None = None,
        key: Any | None = None,
        id: Any | None = None,
        class_name: Any | None = None,
        autofocus: bool | None = None,
        custom_attrs: dict[str, Var | Any] | None = None,
        on_blur: Optional[EventType[()]] = None,
        on_click: Optional[EventType[()]] = None,
        on_context_menu: Optional[EventType[()]] = None,
        on_double_click: Optional[EventType[()]] = None,
        on_focus: Optional[EventType[()]] = None,
        on_mount: Optional[EventType[()]] = None,
        on_mouse_down: Optional[EventType[()]] = None,
        on_mouse_enter: Optional[EventType[()]] = None,
        on_mouse_leave: Optional[EventType[()]] = None,
        on_mouse_move: Optional[EventType[()]] = None,
        on_mouse_out: Optional[EventType[()]] = None,
        on_mouse_over: Optional[EventType[()]] = None,
        on_mouse_up: Optional[EventType[()]] = None,
        on_scroll: Optional[EventType[()]] = None,
        on_unmount: Optional[EventType[()]] = None,
        **props,
    ) -> "Html":
        """Create a html component.

        Args:
            *children: The children of the component.
            dangerouslySetInnerHTML: The HTML to render.
            access_key: Provides a hint for generating a keyboard shortcut for the current element.
            auto_capitalize: Controls whether and how text input is automatically capitalized as it is entered/edited by the user.
            content_editable: Indicates whether the element's content is editable.
            context_menu: Defines the ID of a <menu> element which will serve as the element's context menu.
            dir: Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl (Right-To-Left)
            draggable: Defines whether the element can be dragged.
            enter_key_hint: Hints what media types the media element is able to play.
            hidden: Defines whether the element is hidden.
            input_mode: Defines the type of the element.
            item_prop: Defines the name of the element for metadata purposes.
            lang: Defines the language used in the element.
            role: Defines the role of the element.
            slot: Assigns a slot in a shadow DOM shadow tree to an element.
            spell_check: Defines whether the element may be checked for spelling errors.
            tab_index: Defines the position of the current element in the tabbing order.
            title: Defines a tooltip for the element.
            style: The style of the component.
            key: A unique key for the component.
            id: The id for the component.
            class_name: The class name for the component.
            autofocus: Whether the component should take the focus once the page is loaded
            custom_attrs: custom attribute
            **props: The props to pass to the component.

        Returns:
            The html component.

        Raises:
            ValueError: If children are not provided or more than one child is provided.
        """
        ...

html = Html.create
